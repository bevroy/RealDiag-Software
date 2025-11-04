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

Security note
- Only expose safe, non-secret values with the `NEXT_PUBLIC_` prefix. Any value written into `runtime-config.js`
  is visible to end users.
