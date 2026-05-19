# Website Integration

The chatbot is prepared to run as a floating assistant on the 1PAX website and to route users back to relevant website pages.

## What Is Wired

- Project questions append a `View on the 1PAX website` link for the matching project.
- Company questions route to the best page: `/about`, `/contact`, `/the-team`, `/patents`, or project pages for Ecoport and PAX Cart.
- Team questions route to `/the-team`.
- Office questions route to `/contact`.
- Service questions route to filtered project categories such as `/projects?category=airports-railstations`.
- The public website URL map lives in `actions/site_links.py`.

Updating website slugs only requires editing `actions/site_links.py` and restarting the action server. It does not require Rasa retraining.

## Floating Widget

Add this script to the website footer/body custom code:

```html
<script src="https://YOUR_CHATBOT_DOMAIN/widget.js" defer></script>
```

For local testing after running `./start.sh`:

```html
<script src="http://localhost:8080/widget.js" defer></script>
```

Optional attributes:

```html
<script
  src="https://YOUR_CHATBOT_DOMAIN/widget.js"
  data-title="1PAX Assistant"
  data-open="false"
  defer
></script>
```

The widget creates a bottom-right launcher and opens the chatbot in an iframe. Links to `https://www.1pax.com/...` navigate the parent website, so clicking a project/team/office link moves the visitor to the relevant website page.

## Website API Routes

The production nginx config exposes stable routes for the website:

- `POST /api/chat` proxies to Rasa REST webhook.
- `POST /api/translate` proxies to the translation proxy.
- `GET /api/status` proxies to Rasa status.
- `GET /api/translate/health` checks translation availability.

The full-page chat UI uses direct localhost Rasa/translation URLs during local development and these `/api/...` routes in production.

## Deployment Notes

Deploy the chatbot container, then use its public domain as `YOUR_CHATBOT_DOMAIN` in Webflow. Keep `GEMINI_API_KEY` or `GOOGLE_API_KEY` set in the deployment environment if multilingual input/output should work.

When Webflow slugs change, update:

- `PROJECT_URLS` for project detail pages.
- `COMPANY_URLS` for company, offices, careers, patents, product, and team routes.
- `SERVICE_URLS` for service category routes.
