#!/bin/sh
set -e


# Generate runtime config for any NEXT_PUBLIC_* env vars. This writes a small
# JS file the browser can read at startup (served from /runtime-config.js).
RUNTIME_FILE=/app/frontend/public/runtime-config.js
mkdir -p "$(dirname "$RUNTIME_FILE")"

# Use awk to gather NEXT_PUBLIC_* environment variables and produce JSON-safe output
env | awk -F'=' '
  BEGIN { print "window.__RUNTIME_CONFIG = {" }
  /^NEXT_PUBLIC_/ {
    val=$0; sub(/^[^=]*=/, "", val)
    gsub(/\\/, "\\\\", val); gsub(/"/, "\\\"", val)
    entries[++n]=sprintf("  \"%s\": \"%s\"", $1, val)
  }
  END {
    for(i=1;i<=n;i++){
      printf "%s", entries[i]
      if(i<n) printf ",\n"
      else printf "\n"
    }
    print "};"
  }' > "$RUNTIME_FILE"

exec npm run start
