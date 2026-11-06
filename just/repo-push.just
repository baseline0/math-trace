# Vendored from fleet-base @ v0.8.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# repo-push-sha256: e09d45a43fa1b3722bce0e5a90596c5a9cb06f287880c06d409da1c3b72628c4
# repo-push-body

# Push main to origin. Refuses a branch other than main, and a dirty tree.
push:
    #!/bin/bash
    set -euo pipefail

    branch="$(git branch --show-current)"
    if [ "$branch" != "main" ]; then
        echo "[!] refuse: push runs from main (trunk-based development); this checkout is on '$branch'" >&2
        exit 1
    fi
    if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
        echo "[!] refuse: uncommitted changes. Commit them first (just commit), then push." >&2
        exit 1
    fi

    LOCK="$(git rev-parse --git-common-dir)/fleet.lock"
    exec 9>>"$LOCK"
    if ! flock -w "${FLEET_LOCK_WAIT:-300}" 9; then
        echo "[!] $LOCK is held by another process. Waited ${FLEET_LOCK_WAIT:-300}s." >&2
        exit 1
    fi

    # The commits about to go out carry no Co-Authored-By trailer, unless the push names the override.
    uv run python -m fleet_base.commit_trailers --repo . --range "origin/main..HEAD"

    git push origin main

# Verify the vendored copy at just/repo-push.just is the one fleet-base ships (header hash over the body).
check-repo-push:
    #!/bin/bash
    set -euo pipefail
    want=$(sed -n 's/^# repo-push-sha256: //p' just/repo-push.just)
    got=$(sed -n '/^# repo-push-body$/,$p' just/repo-push.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/repo-push.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/repo-push.just matches fleet-base"
