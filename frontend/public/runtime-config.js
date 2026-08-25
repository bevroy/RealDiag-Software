// Default runtime configuration included in the built site.
// This file is used when Netlify (or any static host) serves the site and
// the container-entrypoint runtime write isn't available. It can be
// overridden at runtime when deploying as a container by writing a
// different /runtime-config.js that sets window.__RUNTIME_CONFIG__.

// Set both names to be safe: some builds expect `window.__RUNTIME_CONFIG` while
// older/alternate code used `window.__RUNTIME_CONFIG__` (double underscore).
window.__RUNTIME_CONFIG = window.__RUNTIME_CONFIG || window.__RUNTIME_CONFIG__ || {
  // API base used by the frontend to call the backend.
  // Matches the variable name used in the app (NEXT_PUBLIC_API_BASE).
  // For local development, use the forwarded GitHub Codespaces URL or localhost.
  NEXT_PUBLIC_API_BASE: window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : window.location.hostname.includes("github.dev")
    ? window.location.origin.replace(/-8080\.app\.github\.dev/, "-8000.app.github.dev")
        : window.location.hostname === "realdiag-cerner-test-frontend.netlify.app"
        ? "https://realdiag-cerner-test.onrender.com"
    : window.location.hostname === "realdiag-test-frontend.netlify.app"
    ? "https://realdiag-test-backend.onrender.com"
    : "https://api.realdiag.com"
};

// Ensure both variables reference the same object
window.__RUNTIME_CONFIG__ = window.__RUNTIME_CONFIG__ || window.__RUNTIME_CONFIG;
