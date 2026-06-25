#!/usr/bin/env bash
set -euo pipefail

EVENT_NAME="${EVENT_NAME:-}"
BASE_REF="${BASE_REF:-}"
BEFORE_SHA="${BEFORE_SHA:-}"
CURRENT_SHA="${CURRENT_SHA:-HEAD}"

GUIDE_USER="frontend/pages/user-guide.js"
GUIDE_TECH="frontend/pages/technical-medical.js"

get_diff_range() {
  if [[ "${EVENT_NAME}" == "pull_request" && -n "${BASE_REF}" ]]; then
    git fetch --no-tags --depth=1 origin "${BASE_REF}"
    echo "origin/${BASE_REF}...HEAD"
    return
  fi

  if [[ -n "${BEFORE_SHA}" && "${BEFORE_SHA}" != "0000000000000000000000000000000000000000" ]]; then
    echo "${BEFORE_SHA}...${CURRENT_SHA}"
    return
  fi

  if git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
    echo "HEAD~1...HEAD"
  else
    echo ""
  fi
}

DIFF_RANGE="$(get_diff_range)"

if [[ -z "${DIFF_RANGE}" ]]; then
  echo "Guide sync check: no diff range available, skipping check."
  exit 0
fi

CHANGED_FILES="$(git diff --name-only "${DIFF_RANGE}")"

if [[ -z "${CHANGED_FILES}" ]]; then
  echo "Guide sync check: no changed files detected."
  exit 0
fi

RELEVANT_CHANGES="$(echo "${CHANGED_FILES}" | grep -E '^(backend/|frontend/)' | grep -vE '^frontend/pages/(user-guide|technical-medical)\.js$' | grep -vE '\.md$|\.txt$' || true)"

if [[ -z "${RELEVANT_CHANGES}" ]]; then
  echo "Guide sync check: no software changes requiring guide review."
  exit 0
fi

echo "Guide sync check: software changes detected:"
echo "${RELEVANT_CHANGES}"

USER_GUIDE_UPDATED="false"
TECH_GUIDE_UPDATED="false"

if echo "${CHANGED_FILES}" | grep -q "^${GUIDE_USER}$"; then
  USER_GUIDE_UPDATED="true"
fi

if echo "${CHANGED_FILES}" | grep -q "^${GUIDE_TECH}$"; then
  TECH_GUIDE_UPDATED="true"
fi

if [[ "${USER_GUIDE_UPDATED}" != "true" || "${TECH_GUIDE_UPDATED}" != "true" ]]; then
  echo
  echo "ERROR: Software changes require guide updates."
  echo "Please review and update both of the following files in this change:"
  echo "  - ${GUIDE_USER}"
  echo "  - ${GUIDE_TECH}"
  echo
  echo "Changed files in this diff:"
  echo "${CHANGED_FILES}"
  exit 1
fi

echo "Guide sync check passed: both guide pages were updated."
