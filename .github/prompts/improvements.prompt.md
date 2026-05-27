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
