# Calendly integration

The chatbot can run a Calendly booking flow inside the conversation:

1. Collect invitee name and email.
2. Ask for a meeting window, such as "tomorrow afternoon" or "next week".
3. Fetch live availability from Calendly.
4. Offer numbered time slots.
5. Ask for explicit confirmation.
6. Create the Calendly invitee and return the confirmation links.

This uses Calendly's Scheduling API (`GET /event_type_available_times` followed
by `POST /invitees`), so the invitee should not be sent to a Calendly-hosted
booking page during the normal flow.

## Required environment variables

Set these before running the action server:

```bash
CALENDLY_ACCESS_TOKEN="..."
CALENDLY_EVENT_TYPE_URI="https://api.calendly.com/event_types/..."
```

`CALENDLY_EVENT_TYPE_UUID` can be used instead of `CALENDLY_EVENT_TYPE_URI`.

## Optional environment variables

```bash
CALENDLY_SCHEDULING_LINK="https://calendly.com/..."
CALENDLY_DEFAULT_TIMEZONE="Europe/Belgrade"
CALENDLY_MAX_SLOTS="5"
CALENDLY_LOCATION_KIND="zoom_conference"
CALENDLY_LOCATION_VALUE=""
CALENDLY_EVENT_GUESTS="person1@example.com,person2@example.com"
CALENDLY_ALLOW_LINK_FALLBACK="false"
CALENDLY_SALESFORCE_UUID=""
CALENDLY_BROWSER_FALLBACK="false"
CALENDLY_BROWSER_PREFERRED="false"
CALENDLY_BROWSER_TIMEOUT_SECONDS="30"
CALENDLY_BROWSER_HEADFUL="false"
CALENDLY_BROWSER_EXECUTABLE_PATH=""
```

`CALENDLY_SCHEDULING_LINK` is only used as a fallback when
`CALENDLY_ALLOW_LINK_FALLBACK=true`. Leave that disabled when the chatbot must
complete scheduling without customer intervention in Calendly.

`CALENDLY_LOCATION_KIND` should match the location expected by the Calendly event
type; omit it when the event type does not require a location object. For the
smoothest fully-chat booking flow, configure the Calendly event type with one
fixed location, such as Zoom, Google Meet, Microsoft Teams, or a static custom
location. If the event type asks the invitee to provide a phone number/location
or lets them choose from multiple locations, the chatbot must collect and send
that location data or Calendly will reject `POST /invitees`.

`CALENDLY_SALESFORCE_UUID` is optional. Do not send a blank Salesforce UUID;
Calendly can reject invalid optional tracking values.

## Optional hosted-page automation fallback

When Calendly rejects `POST /invitees` but the hosted booking page can still
complete the event, `CALENDLY_ALLOW_LINK_FALLBACK=true` now automatically tries
the browser automation before showing the finalization link. To make the hosted
page automation run first on the final confirmation turn, enable:

```bash
CALENDLY_BROWSER_FALLBACK="true"
CALENDLY_BROWSER_PREFERRED="true"
CALENDLY_ALLOW_LINK_FALLBACK="true"
```

On confirmation, the bot shows a booking summary and finalizes the meeting. With
`CALENDLY_BROWSER_PREFERRED=true`, it opens the prefilled Calendly URL in
headless Chromium first, pins the URL to the already selected slot, fills any
missing name/email/purpose fields, clicks **Schedule Event**, and returns a
normal booked confirmation. If browser automation is unavailable or Calendly
changes the page, the bot uses the Scheduling API and then falls back to the
same prefilled finalization link.

For local setup:

```bash
.venv/bin/pip install playwright
.venv/bin/python3 -m playwright install chromium
```

Docker builds include Chromium by default. To skip the browser payload for a
deployment that only uses the Scheduling API:

```bash
docker build --build-arg INSTALL_CALENDLY_BROWSER=false .
```

You can also run the automation directly for a prefilled page:

```bash
.venv/bin/python3 scripts/book_calendly.py \
  --link "$CALENDLY_SCHEDULING_LINK" \
  --name "Matija Lekovic" \
  --email "matija.lekovic@1pax.com" \
  --purpose "chatbot scheduling testing" \
  --start-time "2026-05-29T08:30:00Z" \
  --timezone "Europe/Belgrade"
```

## Calendly account setup for fully in-chat scheduling

1. Use a Calendly paid plan that includes Scheduling API access.
2. Create a personal access token from the Calendly account that owns or can
   administer the event type.
3. Set `CALENDLY_ACCESS_TOKEN`.
4. Set `CALENDLY_EVENT_TYPE_URI` or `CALENDLY_EVENT_TYPE_UUID` for the event
   type that should be booked by the chatbot.
5. Configure a single API-compatible event location in Calendly, or set
   `CALENDLY_LOCATION_KIND` and `CALENDLY_LOCATION_VALUE` to match that event
   type.
6. Keep `CALENDLY_ALLOW_LINK_FALLBACK=false` so booking failures surface as
   configuration/API errors instead of sending the user to Calendly.

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
