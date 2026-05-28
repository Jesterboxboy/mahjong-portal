# Improvement 1 ✓ DONE
## Change Tournament registration mask
Add a field for email adress and make it mandatory
Make the telephone field optional
remove the additional contact

### Implementation
- `tournament/models.py`: Added `email = models.EmailField(...)` (mandatory) to `TournamentRegistration`; made `phone` optional (`null=True, blank=True`)
- `tournament/forms.py`: Updated `TournamentRegistrationForm.Meta.fields` — added `email`, removed `additional_contact`
- `tournament/admin.py`: Added `email` to `TournamentRegistrationAdmin.list_display`
- `tournament/migrations/0061_add_email_to_registration_make_phone_optional.py`: Migration created and applied

# Improvement 2 ✓ DONE
## Tournament announcement page — Info tab, country field, GDPR PDF, card styling

### Requirements
- Add an optional (later: mandatory) Country field to tournament registration
- Add a "Tournament Info" tab alongside "Registration" on the announcement page, showing date, address, itinerary, lunch options, contact info
- Make it possible to attach a GDPR/data-protection PDF document, linked above the consent checkbox
- Style the registration form similar to the settings page (card-based layout)
- Tournament Info tab fields must be bilingual (German + English), edited in Django admin

### Implementation

**`tournament/models.py`**
- `Tournament`: added `venue_address`, `schedule`, `lunch_options`, `contact_info` (all `TextField`, nullable) and `gdpr_document` (`FileField`, uploads to `tournament/gdpr/`)
- `TournamentRegistration`: added `registration_country` (`CharField`, `null=True`, mandatory at form level via `blank` not set)
- `OnlineTournamentRegistration`: same `registration_country` field

**`tournament/translation.py`**
- Added `venue_address`, `schedule`, `lunch_options`, `contact_info` to `TournamentTranslationOptions` → creates `_de`/`_en` DB columns; `TabbedTranslationAdmin` shows language tabs in admin

**`tournament/forms.py`**
- `TournamentRegistrationForm.Meta.fields`: added `registration_country` (between `first_name` and `city`)
- `OnlineTournamentRegistrationForm.Meta.fields`: same
- Both forms iterate fields individually in the template to inject the GDPR link before the consent checkbox

**`tournament/admin.py`**
- `TournamentAdmin` now inherits `TabbedTranslationAdmin` (from `modeltranslation.admin`) → DE/EN tabs for `venue_address`, `schedule`, `lunch_options`, `contact_info`
- New fieldsets: `"Tournament Info Tab"` (the 4 info fields) and `"GDPR"` (the document upload)
- `TournamentRegistrationAdmin` and `OnlineTournamentRegistrationAdmin` show `registration_country` in list

**`mahjong_portal/settings.py`**
- Added `MEDIA_URL = "/media/"` and `MEDIA_ROOT = os.path.join(BASE_DIR, "media")` to support file uploads

**`mahjong_portal/urls.py`**
- Added `serve` for `/media/` path when `DEBUG=True`

**`templates/tournament/announcement.html`**
- Full rewrite with Bootstrap 5 tab structure: "Registration" tab + optional "Tournament Info" tab
- "Tournament Info" tab only appears when at least one info field is filled; shows cards per section (Venue, Schedule, Lunch, Contact) with coloured headers
- Registration form and participants list wrapped in Bootstrap cards (matching settings page style)
- Fields rendered individually (`{% for field in form %}`) so GDPR PDF link can be injected before the consent checkbox
- "Registered players" count fixed to use `online_tournament_registrations` for Pantheon non-online tournaments

**Migrations**
- `0062_improvement2_info_fields`: adds all new Tournament and registration fields
- `0063_info_fields_translations`: adds `_de`/`_en` columns for the 4 info fields

# Improvement 3 ✓ DONE
Add the same fields that are in Tournament Info Tab in both languages to the
Turnieranmeldung, also with tabs.
Change telephone of organizer to optional, but change
"Zusätzlicher Kontakt des Veranstalters" to mandatory email field an move above phone field.
Also make judge fields non mandatory and do the same with phone and additional contact fields as with the organizers.
Options in type of tournament should be ema/other/online and match to TOurnament type. Online should also set tournament game type to online.

### Implementation

**`tournament/models.py` — TournamentApplication changes**
- `tournament_type`: `PositiveSmallIntegerField` [CRR/RR/EMA/OTHER] → `CharField(max_length=10)` with `[["ema","EMA"],["other","Other"],["online","Online"]]`, default `"ema"` — matches `Tournament.TOURNAMENT_TYPES`
- Added `country` (`CharField`, optional) to carry country name into the Tournament (used by Improvement 4 action)
- Added 8 bilingual info fields (all `TextField`, nullable): `venue_address_de/en`, `schedule_de/en`, `lunch_options_de/en`, `contact_info_de/en`
- `organizer_phone`: made optional (`null=True, blank=True`)
- `organizer_additional_contact` → renamed to `organizer_email` (`EmailField`, `null=True`; no `blank=True` → form-required), moved above phone in template
- `referee_name`: optional (`null=True, blank=True`)
- `referee_phone`: optional (`null=True, blank=True`)
- `referee_additional_contact` → renamed to `referee_email` (`EmailField`, `null=True, blank=True` — optional)

**`tournament/forms.py`**
- `TournamentApplicationForm`: added `required_css_class = "required-field"`; changed `exclude = []` → `exclude = ["tournament_admin_user"]`

**`templates/tournament/application.html`**
- Added `country` field to "Main info" section
- New "Tournament info (bilingual)" section with Bootstrap 5 DE/EN tabs containing `venue_address`, `schedule`, `lunch_options`, `contact_info` pairs
- "Organizer" section: `organizer_email` placed above `organizer_phone`; removed old `organizer_additional_contact`
- "Referee" section: `referee_email` replaces `referee_additional_contact`

**`tournament/migrations/0064_tournament_application_improvements.py`**
- `RemoveField`/`AddField` for `tournament_type` (type change), `AlterField` for organizer/referee fields, `RenameField` for _contact→_email, 8 `AddField` for bilingual info columns, `AddField` for `country`

# Improvement 4 ✓ DONE
Add an option to tournament application  in django admin under ournament/tournamentapplication/ that allows to create a tournament entry from a tournament application entry using all the information in the fields.
If necessary change fields from Application so they match the tournament model, but not the other way round.
The option should be in the dropdown of Aktion and should create a tournament draft and redirect to the tournament edit page.

### Implementation

**`tournament/admin.py`**
- Added helper `_parse_date(value)` that tries multiple date formats (`dd.mm.yyyy`, `yyyy-mm-dd`, etc.)
- Added admin action `create_tournament_from_application(modeladmin, request, queryset)`:
  - Enforces single-item selection
  - Resolves `Country` object by name or code from `app.country`; falls back to `Country.objects.first()`
  - Parses `start_date` / `end_date` from the CharField; uses today as fallback for `end_date`
  - Generates a unique `slug` from the tournament name (appends `-N` suffix on collision)
  - Sets `tournament_games_type = "online"` when `tournament_type == "online"`
  - Maps all bilingual info fields directly; falls back `venue_address_de` → legacy `address` field
  - Derives `contact_info_de` from organizer name/email/phone if explicit field is blank
  - Creates `Tournament` with `is_upcoming=True` (draft); saves
  - Shows success message and redirects to the new Tournament's admin change page
- `TournamentApplicationAdmin.actions = [create_tournament_from_application]`

# Improvement 5 ✓ DONE
http://localhost:8060/admin/rating/rating/2/change/
still shows de and en names, please remove these and all dependencies so its only showing one name field

### Implementation

**`rating/translation.py`**
- Removed `translator.register(Rating, ...)` and `translator.register(ExternalRating, ...)` — both models now use plain `name`/`description` without language variants.

**`rating/admin.py`**
- `RatingForm`: changed `exclude = ["name", "description"]` → `fields = ["name", "slug", "description", "type", "order"]`
- `ExternalRatingForm`: changed `exclude = ["name", "description"]` → `fields = ["name", "slug", "description", "type", "order", "is_hidden"]`

**`rating/migrations/0022_remove_rating_translation_fields.py`**
- `RunSQL` to copy `name_de → name` and `description_de → description` (German was the default language)
- `RemoveField` for `name_de`, `name_en`, `description_de`, `description_en` on both `rating` and `externalrating` tables

# Improvement 6 ✓ DONE
i want the EMA ranking to be populated by the information from http://mahjong-europe.org/ranking/Country/AUT_RCR.html
with the fields first name, last name, Total, EMA Ranking, but sorted by Total instead of the ranking calculator based on all ema tournaments in the system, but so that calling
40 1 * * * python /app/manage.py rating_calculate ema in the crontab still updates these values

use the scraper from the austrian_ranking app for that.

### Implementation

**`austria_ranking/scraper.py`**
- Added `scrape_at_ranking()` function: fetches `AUT_RCR.html`, parses `p[0]` (EMA global rank), `p[2]` (EMA ID), `p[3]` (last name), `p[4]` (first name), `p[6]` (total points)
- Returns list of `{ema_id, first_name, last_name, ema_rank, total_points}` sorted by `total_points` descending

**`rating/calculation/ema.py`**
- Completely rewrote `RatingEMACalculation` — no longer inherits from `RatingRRCalculation`/`RatingDatesMixin`
- `USE_SCRAPER = True` class attribute signals the command to use today-only refresh
- `calculate_players_rating_rank(rating, rating_date)`: calls `scrape_at_ranking()`, matches players by `ema_id`, creates `RatingResult` rows with `score=total_points`, `place` = rank by total, `rating_calculation` = EMA global rank string

**`rating/management/commands/rating_calculate.py`**
- Added `USE_SCRAPER` check after building the calculator: if True, skips tournament date scanning and instead clears+recreates `RatingDate`/`RatingResult` for today, then calls `calculate_players_rating_rank`
- `from_zero` flag still works: clears all historical data before refreshing

# Improvement 7 ✓ DONE
Run a nightly calculation for every QuotaEvent that is current in the Austrian rankings.
There are already "Run Calculation" buttons in http://localhost:8060/admin/austria_ranking/quotaevent/ — reuse that logic.

### Implementation

**`austria_ranking/management/commands/calculate_austrian_ranking.py`** (new)
- Queries `QuotaEvent.objects.filter(is_current=True)`
- For each: calls `scraper.run_full_scrape(period)` then `calculator.rank_players_for_period(period)` and updates `period.calculated_at` — identical to what the admin "Run Calculation" button does

**`docker/django/crontab`**
- Added `50 1 * * * python /app/manage.py calculate_austrian_ranking` (runs at 01:50, after the EMA rating job)


# Improvement 8 ✓ DONE
move functionality of the run calculation buttons in austria_ranking/quotaevents to the action dropdown menu instead of buttons as it is now.

### Implementation

**`austria_ranking/admin.py`**
- Removed `run_button` method and `"run_button"` from `list_display`
- Removed `from django.urls import reverse` and `from django.utils.html import format_html` imports
- Added module-level action function `run_ranking_calculation(modeladmin, request, queryset)`: iterates the selected queryset, calls `scraper.run_full_scrape(period)` + `calculator.rank_players_for_period(period)`, updates `calculated_at`, and shows a success message
- Added `actions = [run_ranking_calculation]` to `QuotaEventAdmin`

**`mahjong_portal/urls.py`**
- Removed `from austria_ranking.views import run_ranking_calculation` import
- Removed `url(r"^admin/austria-ranking/(?P<pk>\d+)/run/$", ...)` URL entry

**`austria_ranking/views.py`**
- Removed the now-unused `run_ranking_calculation` view and all its imports; file reduced to a single encoding comment

**`templates/website/rangliste.html`**
- Removed the staff-only "Calculate now" link that referenced the deleted `austria_ranking_run` URL

# Improvement 9 ✓ DONE
* Add an additional app "Vereinsmitglieder" that tracks active club members and fees per year.
  Create a model Mitgliedschaftsbeitrag that has the following fields.
  year, foreign key top player, but also display the player name and first name in the table view.
  Allow filtering by year.
  So if a player has payed his yearly fee i will add him to this list.

### Implementation

**`vereinsmitglieder/` (new app)**
- `models.py`: `Mitgliedschaftsbeitrag` with `year = PositiveIntegerField()` and `player = ForeignKey('player.Player', related_name='membership_fees')`; `unique_together = [['year', 'player']]`; default ordering by `-year, last_name, first_name`
- `admin.py`: `MitgliedschaftsbeitragAdmin` with `list_display = ['year', 'player_last_name', 'player_first_name']`, `list_filter = ['year']`, `raw_id_fields = ['player']`, `search_fields` on player name; `player_last_name` and `player_first_name` are display methods with `admin_order_field`
- `apps.py`, `__init__.py`, `migrations/__init__.py` created
- `migrations/0001_initial.py`: manually crafted (no `makemigrations` in Docker); depends on `player.0020`

**`mahjong_portal/settings.py`**
- Added `"vereinsmitglieder"` to `INSTALLED_APPS`

**Migration applied**: `vereinsmitglieder.0001_initial` — OK

# Improvement 10 ✓ DONE
Show an additional section under de/players/player for each player with the information if he has payed his club fee for the last three years.
show him a column of years descending, with a checkmark or an x named Membership fees payed.

### Implementation

**`player/views.py`**
- Added `from vereinsmitglieder.models import Mitgliedschaftsbeitrag`
- In `player_details()`: computes `fee_years = [current_year, current_year-1, current_year-2]`, queries `Mitgliedschaftsbeitrag` for those years, builds `membership_fees = [{year, paid}, ...]`
- Passes `membership_fees` in the render context

**`templates/player/details.html`**
- Added a new Bootstrap card "Mitgliedschaftsbeitrag" (green header, bill-list icon) between the Ratings section and the Latest Tournaments section
- Shows a two-column table (Jahr / Status) with ✓ (`text-success`) or ✗ (`text-danger`) per year
- Card is always rendered when `membership_fees` is in context (list is always populated for the last 3 years)


# Improvement 11 ✓ DONE
in quota event, only count tournaments in a given year to a player if he has payed his fees for this year.
Under details, still show the tournament entries but color them light red and if mouseover display "Fee for xxxx not payed" (where xxxx is the year.)

### Implementation

**`austria_ranking/calculator.py`**
- Added `from vereinsmitglieder.models import Mitgliedschaftsbeitrag`
- After building `player_lookup`, initialises `paid_years_lookup` with an **empty `set()`** for every portal player (key absent → player not in portal → no restriction; empty set → in portal, no fees paid → nothing counted)
- Fills in paid years from `Mitgliedschaftsbeitrag`; players not in the portal are simply absent from the lookup
- `_year_ok()` closure: returns `True` only if the result's year is in the player's paid-year set (or if the player is not tracked in the portal)
- Result dicts store `"year": r.end_date.year` so `_year_ok` can check it; closure captures `portal_paid_years` via default-arg to avoid late-binding issues
- AT points and foreign top-3 are computed only over fee-valid results

**`website/views.py`**
- Added `from vereinsmitglieder.models import Mitgliedschaftsbeitrag`
- `_annotate_unpaid_results(rankings, period)`: initialises `paid_years_by_ema` with an **empty `set()`** for every portal player (same sentinel logic as calculator); fills paid years from `Mitgliedschaftsbeitrag`; iterates all `EmaTournamentResult` for the period; marks result PKs as unpaid when `end_date.year not in paid_years`; players not in the portal are skipped (no restriction)
- Called in both `rangliste()` and `rangliste_period()` after the existing annotators

**`templates/website/rangliste.html`**
- Austrian tournament rows: `class="table-danger" title="Fee for {{ r.end_date.year }} not payed"` when `r.pk in ranking.unpaid_result_pks`, otherwise `class="table-success"`
- Foreign tournament rows: same `table-danger` override takes priority over `table-success` for used-foreign-top-3 rows


# Improvement 12 ✓ DONE
Add an dropwdpown action to player/player so i can bulk add entries to Mitgliedschaftsbeiträge for players.
Name it "Set Yearly Club Fee status", upon selection ask for the year, and add an entry to Mitgliedschaftsbeiträge if it doesnt already exist.

### Implementation

**`player/admin.py`**
- Added `set_yearly_club_fee(modeladmin, request, queryset)` module-level action
- First call (no `confirmed` POST key): renders intermediate template with selected player PKs as hidden fields and a year input (defaults to current year)
- Second call (`confirmed=1`): reads `fee_year` from POST, calls `Mitgliedschaftsbeitrag.objects.get_or_create(player=player, year=year)` for each selected player, reports how many were created vs already existed
- Added `actions = [set_yearly_club_fee]` to `PlayerAdmin`
- Added imports: `date`, `messages`, `render`, `Mitgliedschaftsbeitrag`

**`templates/admin/player/set_club_fee.html`** (new)
- Extends `admin/base_site.html`; shows player count, year number input, hidden `_selected_action` fields for the queryset PKs, and a submit button

# Improvement 13 ✓ DONE
Add django-tinymce wysiwig to the project and make the following fields editable with it.
in admin/tournament/tournament/
 Tournament info tab

in admin/news/newsarticle/
  Excerpt and body

### Implementation

**`requirements/base.txt`**
- Added `django-tinymce==5.0.0`

**`mahjong_portal/settings.py`**
- Added `"tinymce"` to `INSTALLED_APPS`
- Added `TINYMCE_DEFAULT_CONFIG` with toolbar: bold/italic/underline, lists, link, image, table, code; height 300px
- Added `TINYMCE_FILEBROWSER = True` (wires TinyMCE image picker to filebrowser — see Imp 14)
- Fixed `STORAGES` dict to include `"default"` key (required by Django 5 when `STORAGES` is explicitly defined)

**`mahjong_portal/urls.py`**
- Added `url(r"^tinymce/", include("tinymce.urls"))` for TinyMCE JS/spellcheck endpoints

**`tournament/admin.py`**
- Added `from tinymce.widgets import TinyMCE`
- `TournamentForm.Meta.widgets`: maps all 12 info fields to `TinyMCE()` — `venue_address`, `schedule`, `lunch_options`, `contact_info` plus their `_de` and `_en` translation variants

**`news/admin.py`**
- Replaced `format_html` / `image_preview` with `TinyMCE()` widgets on `excerpt` and `body` via `get_form()` override
- Removed `image_preview` from `list_display`


# Improvement 14 ✓ DONE

 Add django-filebrowser to the project so i can add files and images and add them with django-tinymce.
 Also remove the image section in admin/news/newsarticle.

### Implementation

**`requirements/base.txt`**
- Added `django-filebrowser-no-grappelli==4.0.2` (filebrowser without Grappelli admin dependency)
- Added `Pillow==12.2.0` (required by filebrowser for image processing)

**`mahjong_portal/settings.py`**
- Added `"filebrowser"` to `INSTALLED_APPS` **before** `"django.contrib.admin"` (required for template overrides)
- `TINYMCE_FILEBROWSER = True` — TinyMCE's "Insert Image" button opens the filebrowser dialog

**`mahjong_portal/urls.py`**
- Imported `filebrowser_site` and unpacked its 3-tuple (`_fb_patterns, _fb_app, _fb_ns`)
- Added `url(r"^admin/filebrowser/", include((_fb_patterns, _fb_app), namespace=_fb_ns))` — filebrowser accessible at `/admin/filebrowser/`

**`news/admin.py`**
- Added `exclude = ["image"]` to `NewsArticleAdmin` — image URL field hidden from admin form (model field retained to avoid migration)
- Removed `image_preview` column from `list_display`

**File browser usage**: navigate to `/admin/filebrowser/` to upload and manage files; use the "Upload" button; files are stored in `MEDIA_ROOT/uploads/` by default


# Improvement 15 ✓ DONE
Change the GDPR section in tournament/tournament so i can select an uploaded file with django-filebrowser.

### Implementation

**`tournament/models.py`**
- Added `from filebrowser.fields import FileBrowseField`
- Added `gdpr_file = FileBrowseField(…, directory="gdpr/", extensions=[".pdf", ".doc", ".docx"], null=True, blank=True)` alongside the existing `gdpr_document` FileField
- Existing `gdpr_document` renamed verbose_name to "… direct upload" to distinguish it in admin

**`tournament/migrations/0066_tournament_gdpr_file.py`** (manual)
- `AddField` for `gdpr_file` using `filebrowser.fields.FileBrowseField`; depends on `tournament.0065`; applied ✓

**`tournament/admin.py`**
- GDPR fieldset now shows both `gdpr_document` (direct upload, backward-compat) and `gdpr_file` (filebrowser picker)

**`templates/tournament/announcement.html`**
- GDPR link: checks `tournament.gdpr_file` first (`{{ tournament.gdpr_file.url }}`); falls back to `tournament.gdpr_document.url`
- Both Pantheon-registration and standard-registration form blocks updated

**Workflow**: upload a PDF via the filebrowser (`/admin/filebrowser/`), then select it in the tournament's GDPR fieldset → link appears above the consent checkbox on the registration page
