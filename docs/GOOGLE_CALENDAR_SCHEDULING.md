# Google Calendar Scheduling

The chatbot scheduling action now defaults to the integrated Google Calendar
workflow. Calendly remains available only when `SCHEDULING_PROVIDER=calendly`.

## What the chatbot does

1. Collects visitor name, email, meeting purpose, and time preference.
2. Detects language/region/timezone from Rasa language metadata, browser locale,
   browser timezone, and text hints such as "Spanish", "China", or "Lima".
3. Suggests the best 1PAX office/colleague and asks the visitor to confirm.
4. Offers alternate offices if the visitor declines.
5. Reads Google Calendar availability for the chosen colleague.
6. Books the event directly in Google Calendar after the visitor confirms in chat.

No external scheduling page is required.

## Local smoke test

Use dry-run mode to test the full chatbot flow without Google Workspace auth:

```bash
SCHEDULING_PROVIDER=google GOOGLE_CALENDAR_DRY_RUN=true ./start.sh
```

Dry-run mode uses the configured colleague roster and booking hours, returns
synthetic open slots, and creates a fake event ID after confirmation.

## Production authentication

Recommended setup is a Google Cloud service account with Google Workspace
domain-wide delegation.

Required Python packages are already listed in `requirements-actions.txt` and
the main Dockerfile:

```text
google-api-python-client
google-auth
```

### Keyless impersonation

Preferred setup is keyless service-account impersonation. This works well when
service-account key creation is blocked by organization policy.

For local CLI testing, run:

```bash
gcloud auth application-default login
gcloud iam service-accounts add-iam-policy-binding \
  pax-calendar-scheduler@live-translation-491109.iam.gserviceaccount.com \
  --member=user:YOUR_GOOGLE_ACCOUNT \
  --role=roles/iam.serviceAccountTokenCreator
```

Then set:

```bash
GOOGLE_CALENDAR_IMPERSONATE_SERVICE_ACCOUNT=pax-calendar-scheduler@live-translation-491109.iam.gserviceaccount.com
```

### JSON credentials fallback

If service-account key creation is allowed for your organization, the bot also
supports one JSON credential source:

```bash
GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE=/run/secrets/google-calendar-sa.json
```

or:

```bash
GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```

If your Workspace admin wants all free/busy reads to be delegated through a
specific user, set:

```bash
GOOGLE_CALENDAR_DELEGATED_SUBJECT=scheduling@1pax.com
```

The booking call impersonates the selected colleague calendar when creating the
event.

## Calendar scopes

Grant these scopes to the service account client ID in Google Workspace Admin:

```text
https://www.googleapis.com/auth/calendar.freebusy
https://www.googleapis.com/auth/calendar.events
https://www.googleapis.com/auth/calendar.events.readonly
```

## Colleague roster

The default roster has five offices: Shanghai, Barcelona, Lima, Paris, and
Belgrade. Set the actual calendar IDs through office-specific env vars:

```bash
GOOGLE_CALENDAR_SHANGHAI_CALENDAR_ID=colleague.shanghai@1pax.com
GOOGLE_CALENDAR_BARCELONA_CALENDAR_ID=colleague.barcelona@1pax.com
GOOGLE_CALENDAR_LIMA_CALENDAR_ID=colleague.lima@1pax.com
GOOGLE_CALENDAR_PARIS_CALENDAR_ID=colleague.paris@1pax.com
GOOGLE_CALENDAR_BELGRADE_CALENDAR_ID=colleague.belgrade@1pax.com
```

Override display labels if needed:

```bash
GOOGLE_CALENDAR_SHANGHAI_LABEL="Li Wei"
GOOGLE_CALENDAR_BARCELONA_LABEL="María García"
GOOGLE_CALENDAR_LIMA_LABEL="Ana Torres"
```

For full control, provide `GOOGLE_CALENDAR_ROSTER_JSON`:

```json
[
  {
    "id": "shanghai",
    "label": "Shanghai office colleague",
    "office": "Shanghai",
    "calendar_id": "colleague.shanghai@1pax.com",
    "timezone": "Asia/Shanghai",
    "languages": ["zh", "en"],
    "regions": ["CN", "HK", "Asia"],
    "booking_hours": { "mon-fri": [["12:00", "17:00"]] },
    "priority": 90
  }
]
```

Each colleague can optionally define `availability_calendar_id`. If set, the
bot reads events from that secondary calendar as available booking blocks;
otherwise it uses `booking_hours`.

## Scheduling controls

```bash
GOOGLE_CALENDAR_EVENT_DURATION_MINUTES=30
GOOGLE_CALENDAR_SLOT_STEP_MINUTES=30
GOOGLE_CALENDAR_LEAD_TIME_MINUTES=120
GOOGLE_CALENDAR_BUFFER_MINUTES=0
GOOGLE_CALENDAR_MAX_SLOTS=5
GOOGLE_CALENDAR_CREATE_MEET=true
GOOGLE_CALENDAR_SEND_UPDATES=all
GOOGLE_CALENDAR_EVENT_SUMMARY="1PAX consultation"
```

Employees should block unavailable time directly on their calendars. The bot
uses Google FreeBusy immediately before event creation to avoid stale slots.
