# Calendly integration

The chatbot books meetings through Calendly's public hosted page only. It may
use Calendly's read-only availability API to find open slots, but it never
creates invitees or schedules events through the API.

The conversation flow is:

1. Collect invitee name and email.
2. Collect a short meeting purpose.
3. Ask for a meeting window, such as "tomorrow afternoon" or "next week".
4. Read available slots from Calendly's read-only availability API, falling
   back to the public hosted Calendly page if needed.
5. Offer numbered time slots in chat.
6. Ask for explicit confirmation.
7. Send the exact pre-filled hosted Calendly URL back to the UI as a
   `redirect_url` custom payload. The web UI redirects the user's browser to
   Calendly, where the user completes the final Calendly confirmation click.

## Required environment variables

Set this before running the action server:

```bash
CALENDLY_SCHEDULING_LINK="https://calendly.com/communications-1pax/30min"
CALENDLY_ACCESS_TOKEN="..."
CALENDLY_EVENT_TYPE_URI="https://api.calendly.com/event_types/..."
```

The scheduling link powers the final browser redirect. The API credentials are
used only for read-only slot availability.

## Optional environment variables

```bash
CALENDLY_DEFAULT_TIMEZONE="Europe/Belgrade"
CALENDLY_MAX_SLOTS="5"
CALENDLY_BROWSER_FALLBACK="true"
CALENDLY_BROWSER_TIMEOUT_SECONDS="30"
CALENDLY_BROWSER_HEADFUL="false"
CALENDLY_BROWSER_EXECUTABLE_PATH=""
CALENDLY_ALLOW_LINK_FALLBACK="true"
CALENDLY_ALLOW_CONFIRMATION_LINK_FALLBACK="false"
CALENDLY_LOCATION_KIND="google_conference"
```

After the user explicitly confirms a selected slot, the action no longer tries
server-side browser submission. Calendly blocks headless/data-center sessions
for the final hosted-page confirmation, so the reliable public-web flow is to
redirect the user's own browser to the pre-filled Calendly slot. The browser
automation settings remain available for local diagnostics and hosted-page slot
discovery fallback.

`CALENDLY_BROWSER_HEADFUL=true` is useful for local debugging because it shows
the Chromium window while the script chooses the slot and submits the form.
Production should normally keep the default headless mode.

For local setup:

```bash
.venv/bin/pip install playwright
.venv/bin/python3 -m playwright install chromium
```

Docker builds include Chromium by default. To skip the browser payload for a
deployment that will not use Calendly automation:

```bash
docker build --build-arg INSTALL_CALENDLY_BROWSER=false .
```

You can also run the automation directly for a selected slot:

```bash
.venv/bin/python3 scripts/book_calendly.py \
  --link "$CALENDLY_SCHEDULING_LINK" \
  --name "Matija Lekovic" \
  --email "matija.lekovic@1pax.com" \
  --purpose "chatbot scheduling testing" \
  --start-time "2026-05-29T08:30:00Z" \
  --timezone "Europe/Belgrade"
```

Add `--headful --dry-run` locally to watch it fill the page without submitting.

## Current chatbot intents

Scheduling turns route to `action_schedule_meeting`:

- `ask_schedule_meeting`
- `provide_schedule_name`
- `provide_schedule_email`
- `provide_schedule_time_preference`
- `select_schedule_slot`
- `confirm_schedule_booking`
- `cancel_schedule_booking`

Short fallback replies during an active scheduling flow are also delegated to
the scheduler, so replies like "2", "yes", or a bare email still work.
