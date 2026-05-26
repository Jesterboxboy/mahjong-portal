# Plan: Migrate riichimahjong.at → mahjong-portal

## TL;DR
Extend mahjong-portal with a news app, Austrian-scoped views, WM/EM qualification page, and data migration scripts. The site will reuse mahjong-portal's tournament/club/rating infrastructure, filtered to country=Austria, with German nav labels and a new news/articles system. All code goes in the mahjong-portal repo.

## Key Findings
- mahjong-portal: no news app; tournament registration exists (TournamentRegistration); PlayerQuotaEvent handles WRC/EMA qualification; Club has country FK
- riichimahjong.at: Wagtail-based, EventEntry has richer fields than Tournament; Competitor records are per-tournament (no global player dedup); Member extends AbstractUser

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
9. `EmaTournamentResult`: scraped result row per player per quota period — `quota_period` FK, `ema_id`, `first_name`, `last_name`, `tournament_name`, `tournament_country_code`, `end_date`, `position`, `player_count`, `points` (computed), `is_austrian_tournament`
10. `AustrianRanking`: final output row — `quota_period` FK, `player` FK to portal `Player` (nullable, matched by `ema_id`), `ema_id`, `display_name`, `rank_position`, `total_points`, `at_points`, `foreign_points`
11. Create `0001_initial.py` migration; add `austria_ranking` to `INSTALLED_APPS`

### 3b: EMA Scraper (`austria_ranking/scraper.py`)
12. Port `Tournament_Scraper` and `Player_Scraper` from `ranking-calculator/utils/scrapers.py` — drop SQLAlchemy, return plain dicts
    - Source URL: `https://silk.mahjong.ie/ranking/` (EMA mirror); make configurable via `settings.EMA_RANKING_URL`
    - `scrape_at_players(session)` — fetch the EMA player list, filter `country='at'`, return list of `{ema_id, first_name, last_name}`
    - `scrape_player_results(session, ema_id, start_date, end_date)` — fetch individual player result pages; filter to riichi EMA tournaments whose `end_date` falls within `[start_date, end_date]`; return list of `{tournament_name, country_code, end_date, position, player_count}`
13. Store each scraped result as `EmaTournamentResult`; skip rows already present for the `QuotaPeriod` (idempotent)

### 3c: Ranking Engine (`austria_ranking/calculator.py`)
14. Port `PlayerRankingEngine` from `ranking-calculator/calculators/ranking_austria_riichi.py`:
    - `calculate_points(player_count, position)` → `round(1000 / player_count * (player_count − position + 1))`; returns 0 for last place — discard zeros
    - `rank_players_for_period(quota_period)`:
        - Load all `EmaTournamentResult` rows for the period
        - Per player: AT score = sum of points for `is_austrian_tournament=True`; foreign score = sum of top-3 points for `is_austrian_tournament=False`
        - Write / overwrite `AustrianRanking` rows sorted by `total_points` descending; assign `rank_position`
        - Match `ema_id` to `Player.ema_id` where possible; set `player` FK

### 3d: Admin Trigger (`austria_ranking/admin.py` + custom admin view)
15. `QuotaPeriodAdmin` registered in `admin.py` — `list_display = [name, event_type, start_date, end_date, calculated_at, is_current]`; add a "Run Calculation" button per row (links to step 16)
16. View `run_ranking_calculation(request, pk)` in `austria_ranking/views.py`:
    - Decorated with `@staff_member_required`
    - GET: render confirmation form showing period details + "Confirm & Run" button
    - POST: call `scraper.scrape_at_players()` → `scraper.scrape_player_results()` for each → `calculator.rank_players_for_period()`; set `calculated_at = now()`; redirect to Django admin changelist with success message
17. URL `/admin/austria-ranking/<int:pk>/run/` wired in `mahjong_portal/urls.py` (outside i18n block, inside admin namespace)

### 3e: Public Display
18. Views in `website/views.py`:
    - `rangliste(request)` — load `QuotaPeriod.objects.filter(is_current=True).first()`; render its `AustrianRanking` rows; also expose all periods as a dropdown for historical lookup
    - `rangliste_period(request, pk)` — same but for a specific period
19. URLs: `/rangliste/` and `/rangliste/<int:pk>/` in `website/urls.py`
20. Template `website/rangliste.html`: ranked table with columns rank / name / AT points / foreign points (collapsible detail rows showing individual tournament contributions) / total; period selector; "last calculated" timestamp

## Phase 4: "Sonstiges" Static Pages

21. Add `about_at_de.html` template (About the Austrian club) + view in `website/views.py` at `/uber-uns/`
22. Tournament application already exists at `tournament/new/` — just link in nav
23. Optional info pages as static templates served from `website` app

## Phase 5: Data Migration — Management Commands

All commands in `server/utils/management/commands/` or a new `migration_tools/` app.

### 5a: `migrate_at_clubs`
24. Script reads riichimahjong.at MariaDB (connection from `--source-db` arg or settings) — queries `clubs_club` Wagtail table
    - Creates `Club` in mahjong-portal: `name=title`, `slug`, `website=homepage_url`, `description`, `country=Country(code='AT')`
    - Skips existing slugs
    - Output: created/skipped counts

### 5b: `migrate_at_players` *(depends on 5a)*
25. Source: `members_member` table from riichimahjong.at
    - Create `Player` per Member: split `first_name`/`last_name` (already separate), `ema_id=ema_player_number`, `country=Country(code='AT')`, generate slug
    - Index by email for later deduplication

### 5c: `migrate_at_competitors` *(depends on 5b)*
26. Source: `events_competitor` table
    - Group by `(email, first_name, last_name)` to deduplicate cross-tournament competitors
    - For each unique person: look up existing `Player` by email match (from step 6b); create new `Player` if not found
    - Store mapping `competitor_email → player_id` for step 6e

### 5d: `migrate_at_tournaments`
27. Source: Wagtail `wagtailcore_page` JOIN `events_evententry`
    - Create `Tournament` per EventEntry:
      - `name=title`, `slug`, `start_date=start`, `end_date=end`
      - `country=Country(code='AT')`, `city` lookup/create for `locality`
      - `tournament_type`: if `austrian_championship=True` → `CHAMPIONSHIP`, else `EMA` or `OTHER`
      - `number_of_players` from Competitor count
      - `opened_registration=signup_enabled`, `registration_description=registration_information`
    - Store mapping `evententry_id → tournament_id`

### 5e: `migrate_at_registrations` *(depends on 5c + 5d)*
28. Source: `events_competitor`
    - For each Competitor, use mappings from 5c + 5d
    - Create `TournamentRegistration`: `player=player_from_mapping`, `first_name`, `last_name`, `phone`, `notes=comment`, `is_approved=True`
    - Store `ema_player_number` as additional note if not on Player yet
    - `has_payed` → mark as highlighted or in notes

## Verification
1. Run `python manage.py migrate_at_clubs` on a dev DB; verify Club count matches source
2. Run `python manage.py migrate_at_players` + `migrate_at_competitors`; check deduplication by running `Player.objects.count()`
3. Run `python manage.py migrate_at_tournaments`; check tournament list page renders
4. Run `python manage.py migrate_at_registrations`; spot-check TournamentRegistration records for a known tournament
5. In Django admin, create a `QuotaPeriod` for a past WRC period; click "Run Calculation"; verify `EmaTournamentResult` rows are created and `AustrianRanking` rows are populated
6. Open `/rangliste/` — verify ranked table renders with AT/foreign point columns
7. Open `/neuigkeiten/` — verify news list renders (empty is fine)
8. Open homepage — verify upcoming tournaments show
9. Test nav links end-to-end: all 5 nav items resolve without 404

## Decisions / Scope
- **Wagtail body content (rich HTML)** from EventEntry/NewsEntry: NOT migrated — too complex; import as plain text excerpt only
- **Member auth accounts**: NOT migrated — riichimahjong.at auth system differs; players are linked by EMA ID only
- **Images** (event headers, news images): NOT migrated in first pass — can be added manually via admin
- **SeasonRankingList**: NOT migrated — handled by existing mahjong-portal rating system
- **pyjsconnect (forum SSO)**: Out of scope
- **Mahjong-portal used as single-country instance** — no country filtering needed since only AT data will be in the DB

## Files to Modify/Create
- `server/templates/base.html` — nav update
- `server/website/views.py` — home + rangliste + about views
- `server/website/urls.py` — new URLs
- `server/mahjong_portal/urls.py` — include news + austria_ranking admin URLs
- `server/settings/*.py` — add `EMA_RANKING_URL`, add `austria_ranking` to `INSTALLED_APPS`
- NEW: `server/news/` (full app: models, views, urls, admin, migrations)
- NEW: `server/austria_ranking/` (full app: models, scraper, calculator, views, admin, migrations)
- NEW: `server/utils/management/commands/migrate_at_*.py` (5 commands)
- NEW templates: `news/list.html`, `news/detail.html`, `website/rangliste.html`, `austria_ranking/confirm_run.html`, `website/about_at_de.html`
