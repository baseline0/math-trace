# Vendored from fleet-base @ v0.8.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# fleet-checks-sha256: bb8eacec36d7fddd1f1f5e1e03825df246edd9cb8728c487b7e3fe72d14e671b
# fleet-checks-body

# Lint the whole repository with ruff. Read-only.
[group("dev")]
fleet-lint:
    uv run ruff check .

# Lint, then run the repository's type check when it has one (a check-types recipe). Read-only.
# The type check is advisory: reported, never blocks. Its failure is printed and the recipe still succeeds.
[group("dev")]
fleet-check: fleet-lint
    @if just --summary | tr ' ' '\n' | grep -qx check-types; then just check-types || echo "fleet-check: check-types reported findings (advisory: reported, never blocks)"; else echo "fleet-check: no check-types recipe here; lint only"; fi

# Verify this copy is unedited: the hash in its header must match the body below the marker.
[group("dev")]
check-fleet-checks:
    #!/usr/bin/env bash
    set -euo pipefail
    want=$(sed -n 's/^# fleet-checks-sha256: //p' just/fleet-checks.just)
    got=$(sed -n '/^# fleet-checks-body$/,$p' just/fleet-checks.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/fleet-checks.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/fleet-checks.just matches fleet-base"
