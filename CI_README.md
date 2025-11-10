CI / CD README
================

This file documents the repository's CI/CD flows, required secrets, and how to run the build/publish/pin process.

Secrets
-------

Add the following repository secrets (GitHub -> Settings -> Secrets & variables -> Actions):

- GHCR_TOKEN (recommended): A personal access token that has the "write:packages" and "read:packages" scopes so GitHub Actions can push Docker images to GitHub Container Registry (ghcr.io). If not present, the image build will run but images will not be pushed.
- NETLIFY_TOKEN (optional): If you want CI to trigger Netlify builds via API.
- RENDER_API_KEY (optional): If you want CI to trigger Render deploys or manage services.

Built workflows
---------------

1. .github/workflows/images-release-pin.yml
   - Builds multi-arch Docker images (linux/amd64 and linux/arm64) using Docker Buildx.
   - Logs in and pushes images to GHCR only if `GHCR_TOKEN` is present.
   - Captures image digest(s) and uploads them as artifacts.
   - Runs `tools/pin-manifests.py` to create a pinned k8s manifest `k8s/staging-realdiag.pinned.yaml` and uploads it as an artifact. Optionally commits the pinned manifest back to `main` when run via workflow_dispatch with `commit_pinned=true`.
   - When a git tag (v*) is pushed the workflow also creates a GitHub Release and attaches the pinned manifest.

2. .github/workflows/e2e-netlify-diagnostic.yml
   - Runs a Playwright-based check (Python) to load the Netlify-hosted `/diagnostic` page and validate the backend health endpoint is reachable.
   - Triggered on `workflow_dispatch`, `push` to `main`, and when a release is published.

Local quickstart
----------------

1. Build images locally (multi-arch requires buildx and qemu):

```bash
# buildx setup
docker buildx create --use --name multi-builder || true
docker run --rm --privileged tonistiigi/binfmt --install all || true

# build (example) - will not push
docker buildx build --platform linux/amd64,linux/arm64 -f backend/Dockerfile --output=type=docker .
```

2. To run the CI pin-manifests step locally (use a real digest file if you have one):

```bash
mkdir -p artifacts
echo "ghcr.io/<owner>/realdiag-backend@sha256:<digest>" > artifacts/image-digest.txt
make pin-manifests
```

Triggering CI workflows
-----------------------

1. Manual trigger via the GitHub UI: go to Actions -> select the workflow -> Run workflow.
2. Using the GH CLI (requires `gh auth login` and appropriate permissions):

```bash
gh workflow run images-release-pin.yml --ref main -f commit_pinned=true
gh workflow run e2e-netlify-diagnostic.yml --ref main
```

Notes
-----

- The image push is gated on `GHCR_TOKEN` being set to avoid accidental pushes from forks or CI runs without credentials.
- `tools/pin-manifests.py` is intentionally lightweight (text substitution). For more robust YAML-aware pinning, we can extend it to use `ruamel.yaml` or `PyYAML`.
- You can change the release flow to include additional artifacts (prebuilt frontend zip, etc.) by editing the `images-release-pin.yml` workflow.

If you'd like, I can:

- Add automated PR creation for pinned manifests instead of pushing directly to `main`.
- Make the pinning script YAML-aware to handle more complex manifests and multiple images.
- Add the GHCR_TOKEN secret for you if you provide it (or instruct your CI admin) and then trigger a run and report back.
