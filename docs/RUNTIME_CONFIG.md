Runtime config for the frontend

This project supports exposing runtime environment variables to the browser at container start.

How it works
- Any environment variable prefixed with `NEXT_PUBLIC_` will be written into `public/runtime-config.js`
  by the container entrypoint script (`frontend/docker-entrypoint.sh`). That file sets a global variable
  `window.__RUNTIME_CONFIG` which the frontend reads at runtime.

Why this is useful
- Next.js compiles `process.env.NEXT_PUBLIC_*` at build time. When you build an image, those values are
  baked into the build and cannot change at container start. For dev and staging you may want to supply
  different API endpoints or feature flags at runtime — this provides that capability.

How to set values in docker-compose

In `docker-compose.yml` add environment variables under the `web` service, for example:

web:
  environment:
    NEXT_PUBLIC_API_BASE: "http://localhost:8000"
    NEXT_PUBLIC_EXAMPLE_FLAG: "false"

At container start the entrypoint will produce `/public/runtime-config.js` which the frontend will read.

Accessing values in client code
- The diagnostic page uses `window.__RUNTIME_CONFIG` if present. You can also reference `process.env.NEXT_PUBLIC_*`
  in code that runs at build time (e.g., server-side or during build).

Preview environments (Codespaces / GitHub preview)
-----------------------------------------------

When running the frontend inside a preview URL (for example `your-preview-3000.app.github.dev`),
the diagnostic page includes a small heuristic that attempts to rewrite the preview hostname
from `-3000` to `-8000` so the browser in the preview can reach the API exposed on the same
preview host at port `8000` (i.e. `your-preview-8000.app.github.dev`). If your preview platform
uses a different URL pattern, set `NEXT_PUBLIC_API_BASE` explicitly in the preview environment or
in `docker-compose.yml` to the forwarded URL for port `8000`.

Example (override in compose or preview env):

web:
  environment:
    NEXT_PUBLIC_API_BASE: "https://<your-preview>-8000.app.github.dev"

This explicit setting always overrides the heuristic and is the most reliable option for previews.

Overriding the preview-origin regex
-----------------------------------

The backend's CORS origin check uses a default regex that matches `localhost` and
hostnames like `*-3000.app.github.dev`. If your preview platform uses a different
pattern you can override that behavior by setting the `PREVIEW_ORIGIN_REGEX` env var
for the API. Example (docker-compose):

api:
  environment:
    PREVIEW_ORIGIN_REGEX: '^https?://(?:localhost(?::\\d+)?|.+-3000\\.app\\.github\\.dev)$'

This keeps the allowed origins explicit and portable between preview platforms.

Security note
- Only expose safe, non-secret values with the `NEXT_PUBLIC_` prefix. Any value written into `runtime-config.js`
  is visible to end users.
