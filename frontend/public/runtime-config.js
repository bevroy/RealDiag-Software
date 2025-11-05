// Default runtime configuration included in the built site.
// This file is used when Netlify (or any static host) serves the site and
// the container-entrypoint runtime write isn't available. It can be
// overridden at runtime when deploying as a container by writing a
// different /runtime-config.js that sets window.__RUNTIME_CONFIG__.

window.__RUNTIME_CONFIG__ = window.__RUNTIME_CONFIG__ || {
  // API base used by the frontend to call the backend.
  // Matches the variable name used in the app (NEXT_PUBLIC_API_BASE).
  NEXT_PUBLIC_API_BASE: "https://realdiag-software.onrender.com"
};
