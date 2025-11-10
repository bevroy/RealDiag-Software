#!/usr/bin/env python3
"""Pin Kubernetes manifests to image digests.

Usage:
  tools/pin-manifests.py --manifests k8s/staging-realdiag.yaml --image-digests image-digest.txt --out k8s/staging-realdiag.pinned.yaml

The image-digest file should contain lines like:
  ghcr.io/OWNER/realdiag-backend@sha256:...

This script will replace any image references that contain the repository name
`realdiag-backend` with the corresponding digest form.
"""
import argparse
import re
from pathlib import Path


def load_digests(path):
    digests = {}
    for line in Path(path).read_text().splitlines():
        s = line.strip()
        if not s:
            continue
        # Expect format: repository@sha256:...
        if '@' in s:
            repo, digest = s.split('@', 1)
            name = repo.split('/')[-1]
            digests[name] = f"{repo}@{digest}"
    return digests


def pin_manifest(manifest_path, digests_map):
    content = Path(manifest_path).read_text()
    # Find occurrences like image: something/realdiag-backend:tag or image: realdiag-backend
    def repl(m):
        full = m.group(0)
        image = m.group(1)
        base = image.split('/')[-1].split(':')[0].split('@')[0]
        if base in digests_map:
            return full.replace(image, digests_map[base])
        return full

    new = re.sub(r'image:\s*([A-Za-z0-9_./:-@]+)', repl, content)
    return new


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--manifests', required=True)
    p.add_argument('--image-digests', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    digests = load_digests(args.image_digests)
    if not digests:
        print('No image digests found in', args.image_digests)
        raise SystemExit(1)

    pinned = pin_manifest(args.manifests, digests)
    Path(args.out).write_text(pinned)
    print('Wrote pinned manifest to', args.out)


if __name__ == '__main__':
    main()
