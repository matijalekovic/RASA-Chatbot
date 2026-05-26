# Calendly integration

The chatbot books meetings through the public Calendly hosted page only.

The conversation flow is:

1. Collect invitee name and email.
2. Collect a short meeting purpose.
3. Ask for a meeting window, such as "tomorrow afternoon" or "next week".
4. Open the hosted Calendly page in headless Chromium and read available slots.
5. Offer numbered time slots in chat.
6. Ask for explicit confirmation.
7. Reopen the exact prefilled Calendly URL for the selected slot, click through
   the hosted page, submit **Schedule Event**, and return the confirmation link.

## Required environment variables

Set this before running the action server:

```bash
CALENDLY_SCHEDULING_LINK="https://calendly.com/communications-1pax/30min"
```

No Calendly access token or event type URI is required for the current hosted
page automation flow.

## Optional environment variables

```bash
CALENDLY_DEFAULT_TIMEZONE="Europe/Belgrade"
CALENDLY_MAX_SLOTS="5"
CALENDLY_BROWSER_FALLBACK="true"
CALENDLY_BROWSER_TIMEOUT_SECONDS="30"
CALENDLY_BROWSER_HEADFUL="false"
CALENDLY_BROWSER_EXECUTABLE_PATH=""
CALENDLY_ALLOW_LINK_FALLBACK="true"
```

With `CALENDLY_SCHEDULING_LINK` configured, browser automation and the manual
prefilled-link fallback are enabled by default. Set `CALENDLY_BROWSER_FALLBACK`
to `false` only when you intentionally want to stop automated hosted-page
submission.

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
