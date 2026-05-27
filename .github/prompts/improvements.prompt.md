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

# Improvement 3