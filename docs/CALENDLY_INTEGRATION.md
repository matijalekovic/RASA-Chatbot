# Calendly integration

The chatbot can run a Calendly booking flow inside the conversation:

1. Collect invitee name and email.
2. Ask for a meeting window, such as "tomorrow afternoon" or "next week".
3. Fetch live availability from Calendly.
4. Offer numbered time slots.
5. Ask for explicit confirmation.
6. Create the Calendly invitee and return the confirmation links.

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
```

`CALENDLY_SCHEDULING_LINK` is used as a fallback when API booking is not
configured or temporarily unavailable. `CALENDLY_LOCATION_KIND` should match the
location expected by the Calendly event type; omit it when the event type does
not require a location object.

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
