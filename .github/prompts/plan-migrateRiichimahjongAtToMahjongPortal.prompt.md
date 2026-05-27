# Plan: Migrate riichimahjong.at → mahjong-portal

## TL;DR
Extend mahjong-portal with a news app, Austrian-scoped views, and a WM/EM qualification ranking page. The site reuses mahjong-portal's tournament/club/rating infrastructure with German nav labels and a new news/articles system. The Austrian player roster is sourced from the EMA website (`mahjong-europe.org`) and optionally enriched with contact data from Pantheon (Frey). No SQL migration from riichimahjong.at is required. All code goes in the mahjong-portal repo.

## Key Findings
- mahjong-portal: no news app; tournament registration exists (TournamentRegistration); PlayerQuotaEvent handles WRC/EMA qualification; Club has country FK; `Player.ema_id` links to EMA player IDs
- Pantheon (Frey): `FindByTitle(query)` searches players by full display name; `GetPersonalInfo(ids)` returns `PersonEx` with email — two-step lookup needed
- EMA Austrian RCR player list: `http://mahjong-europe.org/ranking/Country/AUT_RCR.html`

---

## Phase 1: Navigation & Homepage

1. Update `server/templates/base.html` — replace current nav with:
   - **Neuigkeiten & Termine** → `/neuigkeiten/`
   - **Turniere** → `/tournaments/riichi/<year>/` (existing view)
   - **Klubs** → `/clubs/riichi/` (existing view)
   - **Rangliste** → `/rangliste/` (new Austrian rating/qualification page)
   - **Sonstiges** (dropdown) → Turnieranmeldung, Über uns, info pages
   - Keep language switcher + user auth area
2. Update `server/website/views.py` `home()` to surface upcoming tournaments and latest news articles (*depends on Phase 2*)

## Phase 2: News App ("Neuigkeiten & Termine")

3. Create `server/news/` Django app:
   - `NewsArticle` model: `title`, `slug`, `excerpt`, `body` (TextField/HTML), `image` (ImageField), `published_date`, `is_published`, `category` (choices: News, Veranstaltung)
   - `apps.py`, `admin.py` (with image preview), `urls.py`, `views.py`
   - Add to `INSTALLED_APPS` in settings
4. Two views: `news_list` (paginated), `news_detail`
5. URL: `news/` → `news/urls.py`, add to `mahjong_portal/urls.py` i18n block
6. Templates: `templates/news/list.html`, `templates/news/detail.html` — card layout with image thumbnail, styled like existing portal
7. Django migration for the model

## Phase 3: Austrian Rankings & Qualification Page

New `server/austria_ranking/` Django app — owns the quota period config, EMA scraping, ranking calculation, and public display.

### 3a: Data Models (`austria_ranking/models.py`)
8. `QuotaPeriod`: `name` (e.g. "WRC 2026"), `event_type` (choices: WM, EM), `start_date`, `end_date`, `calculated_at` (nullable DateTimeField); `is_current` bool
9. `EmaTournamentResult`: scraped result row per player per quota period — `quota_period` FK, `ema_id`, `first_name`, `last_name`, `tournament_name`, `tournament_country_code`, `ema_tournament_url` (URLField), `end_date`, `position`, `player_count`, `points` (computed), `is_austrian_tournament`
10. `AustrianRanking`: final output row — `quota_period` FK, `player` FK to portal `Player` (nullable, matched by `ema_id`), `ema_id`, `display_name`, `rank_position`, `total_points`, `at_points`, `foreign_points`
11. Create `0001_initial.py` migration; add `austria_ranking` to `INSTALLED_APPS`

### 3b: EMA Scraper (`austria_ranking/scraper.py`)
12. Scrape directly from `https://mahjong-europe.org/ranking/`; make base URL configurable via `settings.EMA_RANKING_URL`
    - `scrape_at_players()` — fetch `Country/AUT_RCR.html`; parse `div.TCTT_lignes > div[class^=TCTT_ligne]`; skip first row (header); extract `p[2].text`=ema_id, `p[3].text`=last_name, `p[4].text`=first_name; return list of `{ema_id, first_name, last_name}`
    - `scrape_player_results(ema_id, start_date, end_date)` — fetch `Players/{ema_id}.html`; find table with `TD.HallFame_LigneGrise_*`; for each row extract `td[1]`=date range, `td[3]`=tournament name + EMA link (strip `../` prefix), `td[5]`=rank "pos/count"; filter to rows whose end date falls within `[start_date, end_date]`; return list of `{tournament_name, ema_tournament_url, country_code, end_date, position, player_count}`
13. Store each scraped result as `EmaTournamentResult`; idempotent via `get_or_create` on `(quota_period, ema_id, tournament_name, end_date)`

### 3c: Ranking Engine (`austria_ranking/calculator.py`)
14. `calculate_points(player_count, position)` → `round(1000 / player_count * (player_count − position + 1))`; discard zeros (last place)
15. `rank_players_for_period(quota_period)`:
    - Load all `EmaTournamentResult` rows for the period
    - Per player: AT score = sum of points for `is_austrian_tournament=True`; foreign score = sum of top-3 points for `is_austrian_tournament=False`
    - Write / overwrite `AustrianRanking` rows sorted by `total_points` descending; assign `rank_position`
    - Match `ema_id` to `Player.ema_id` where possible; set `player` FK

### 3d: Admin Trigger (`austria_ranking/admin.py` + custom admin view)
16. `QuotaPeriodAdmin` registered in `admin.py` — `list_display = [name, event_type, start_date, end_date, calculated_at, is_current]`; add a "Run Calculation" button per row
17. View `run_ranking_calculation(request, pk)` in `austria_ranking/views.py`:
    - Decorated with `@staff_member_required`
    - GET: render confirmation form showing period details + "Confirm & Run" button
    - POST: call `scraper.run_full_scrape(period)` → `calculator.rank_players_for_period(period)`; set `calculated_at = now()`; redirect to Django admin changelist with success message
18. URL `/admin/austria-ranking/<int:pk>/run/` wired in `mahjong_portal/urls.py`

### 3e: Public Display
19. Views in `website/views.py`:
    - `rangliste(request)` — load `QuotaPeriod.objects.filter(is_current=True).first()`; render its `AustrianRanking` rows; expose all periods as dropdown
    - `rangliste_period(request, pk)` — same but for a specific period
20. URLs: `/rangliste/` and `/rangliste/<int:pk>/` in `website/urls.py`
21. Template `website/rangliste.html`: ranked table (rank / name / AT points / foreign top-3 / total); collapsible detail rows per player showing AT tournaments (always green) and foreign tournaments (top-3 highlighted green); EMA tournament name links; period selector; "last calculated" timestamp

## Phase 4: "Sonstiges" Static Pages

22. `about_de.html` / `about_en.html` — static templates with ÖRMV club info (Vorstand, Impressum, ZVR number); served at `/about/` from `website/views.py`
23. `contacts_de.html` / `contacts_en.html` — contact page at `/contacts/`; email: `vorstand@riichimahjong.at`
24. Tournament application already exists at `tournament/new/` — just link in nav under "Sonstiges"
25. All nav strings use `{% trans %}` with German translations in `locale/de/LC_MESSAGES/django.po`

## Phase 5: Player Import from EMA + Pantheon Enrichment

Replace SQL migration with a lightweight management command that builds the player roster from the EMA ranking website and optionally enriches it with email addresses from Pantheon (Frey).

### Source: EMA Austrian RCR player list
URL: `http://mahjong-europe.org/ranking/Country/AUT_RCR.html`
This page lists all Austrian riichi players with EMA IDs. The existing `scrape_at_players()` in `austria_ranking/scraper.py` already parses this page.

### 5a: `sync_at_players_from_ema` management command
26. Command in `server/utils/management/commands/sync_at_players_from_ema.py`
    - Call `austria_ranking.scraper.scrape_at_players()` to get `[{ema_id, first_name, last_name}]`
    - For each entry:
      - If `Player.objects.filter(ema_id=ema_id).exists()` → skip (already imported)
      - Otherwise create `Player`: `first_name`, `last_name`, `ema_id`, `country=Country(code='AT')`, generate `slug` from name
    - Print created/skipped counts
    - Support `--dry-run` flag: print actions without writing to DB

### 5b: `enrich_players_from_pantheon` management command *(optional, run after 5a)*
27. Command in `server/utils/management/commands/enrich_players_from_pantheon.py`
    - Iterate over `Player.objects.filter(country__code='AT', email='')` (players without email)
    - For each player call Frey `FindByTitle(f"{first_name} {last_name}")`:
      - **0 matches** → print warning, skip
      - **1 match** → call `GetPersonalInfo([person_id])` to get `PersonEx`; set `Player.email = person.email`; optionally store `pantheon_id` if a field exists
      - **2+ matches** → print warning listing candidates, skip (requires manual resolution)
    - Support `--dry-run` flag
    - Note: Pantheon `title` is a single display name field; name order may vary for non-Western names — review warnings manually

### Name matching caveats
- EMA stores `first_name` + `last_name` separately; Pantheon `title` is the full display name (order may vary)
- Common names or slight spelling differences will produce 0 or 2+ matches → manual admin fix via Django admin `Player` changelist
- `GetPersonalInfo` requires a Frey `person_id` (from `FindByTitle`) — two API calls per player
- `FindByTitle` returns `Person` (no email); `GetPersonalInfo` returns `PersonEx` (includes `email`)

### What is NOT migrated
- Club membership data — clubs are entered manually via Django admin
- Past tournament results / registrations from riichimahjong.at — not needed; EMA scraper covers tournament history for the ranking
- Member auth accounts — users register fresh via mahjong-portal or Pantheon SSO
- News articles / event descriptions — entered manually via the news admin

## Phase 6: Event Attendance Intent

Allow logged-in users to indicate whether they intend to attend the qualifying event for each quota period. Their ranking row is then colour-coded for all visitors.

### 6a: Data Model (`austria_ranking/models.py`)
28. `EventAttendanceIntent`: `user` FK → `account.User`, `quota_period` FK → `QuotaPeriod`, `status` CharField with choices `yes` / `no` / `unknown` (default `unknown`). `unique_together = [(user, quota_period)]`.
29. Migration `0003_event_attendance_intent.py`.

### 6b: Attendance toggle endpoint (`account/views.py` + `account/urls.py`)
30. View `set_attendance_intent(request, period_pk)` — `@login_required @require_POST`. Reads `status` from POST body (validated against allowed choices). Calls `EventAttendanceIntent.objects.update_or_create(user=request.user, quota_period=period, defaults={"status": status})`. Redirects back to `account_settings`.
31. URL `POST /account/attendance/<int:period_pk>/` named `set_attendance_intent`.

### 6c: Account Settings section (`account/views.py` + `settings.html`)
32. In `account_settings` view: query all `QuotaPeriod` objects and the user's existing `EventAttendanceIntent` rows; pass `attendance_data = [(period, status_or_unknown)]` to template.
33. In `settings.html`: new section "Turnierteilnahme / Event Attendance". For each quota period render a Bootstrap button group with three buttons (✓ green, ? grey, ✗ red). The active choice is highlighted. Each button submits a small `<form method="post">` to `set_attendance_intent`. Only shown when user is authenticated.

### 6d: Rangliste row colouring (`website/views.py` + `rangliste.html`)
34. In both `rangliste` and `rangliste_period` views: load all `EventAttendanceIntent` rows for the period; build `{ema_id: status}` map (via `user.attached_player.ema_id`); annotate each `AustrianRanking` object with `attendance_status`.
35. In `rangliste.html`: apply `style="background-color:#e8f5e9"` (very light green) for `attendance_status == "yes"` and `style="background-color:#ffebee"` (very light red) for `"no"`. Also render a small status icon (✓ / ✗ / nothing) after the player name.

## Verification
1. Run `python manage.py sync_at_players_from_ema --dry-run`; verify expected player list printed
2. Run without `--dry-run`; check `Player.objects.filter(country__code='AT').count()` matches EMA list
3. Run `python manage.py enrich_players_from_pantheon --dry-run`; review match/warning output
4. In Django admin, create a `QuotaPeriod` for a current WRC period; click "Run Calculation"; verify `EmaTournamentResult` and `AustrianRanking` rows are populated
5. Open `/rangliste/` — verify ranked table renders; player names with `ema_id` matches show as links
6. Open `/neuigkeiten/` — verify news list renders (empty is fine)
7. Open homepage — verify upcoming tournaments show
8. Test nav links end-to-end: all nav items resolve without 404

## Decisions / Scope
- **Player source**: EMA ranking website only (`AUT_RCR.html`) — no SQL dump required
- **Email enrichment**: Pantheon Frey API via name matching — best-effort, manual fallback
- **Member auth accounts**: NOT migrated — players register fresh; `Player.ema_id` is the identity anchor
- **Images**: NOT migrated — added manually via admin
- **Club data**: NOT migrated — entered manually
- **Past tournament registrations**: NOT migrated — not needed for the ranking system
- **Mahjong-portal used as single-country instance** — no country filtering needed since only AT data will be in the DB

## Files to Modify/Create
- `server/templates/base.html` — nav update
- `server/website/views.py` — home + rangliste + about + contacts views
- `server/website/urls.py` — new URLs
- `server/mahjong_portal/urls.py` — include news + austria_ranking admin URLs
- `server/settings/*.py` — add `EMA_RANKING_URL`, add `austria_ranking` + `news` to `INSTALLED_APPS`
- NEW: `server/news/` (full app: models, views, urls, admin, migrations)
- NEW: `server/austria_ranking/` (full app: models, scraper, calculator, views, admin, migrations)
- NEW: `server/utils/management/commands/sync_at_players_from_ema.py`
- NEW: `server/utils/management/commands/enrich_players_from_pantheon.py`
- NEW templates: `news/list.html`, `news/detail.html`, `website/rangliste.html`, `austria_ranking/confirm_run.html`, `website/about_de.html`, `website/about_en.html`, `website/contacts_de.html`, `website/contacts_en.html`
