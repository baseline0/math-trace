"""Install the latest elan release locally, after checking its SHA-256 against GitHub's published digest.

elan is the Lean toolchain manager. The VS Code Lean extension and `lake` both find it on PATH or under ELAN_HOME.
This script:
1. reads the latest release from the GitHub API;
2. picks the archive for this machine;
3. downloads it and refuses to continue unless its SHA-256 matches the digest GitHub publishes for that asset;
4. extracts it (refusing archive members that point outside the staging folder);
5. runs elan-init into --install-dir with --default-toolchain none, so no Lean version is installed yet.

A project's Lean version comes from its lean-toolchain file, and elan installs it on first use.

Usage:
    uv run python scripts/install_elan.py --install-dir ~/.elan
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
from pathlib import Path

import httpx
import typer

app = typer.Typer(help="Install the latest elan release, after verifying its SHA-256.", add_completion=False)

RELEASE_API = "https://api.github.com/repos/leanprover/elan/releases/latest"
TRIPLES: dict[tuple[str, str], str] = {
    ("Linux", "x86_64"): "x86_64-unknown-linux-gnu",
    ("Linux", "aarch64"): "aarch64-unknown-linux-gnu",
    ("Darwin", "x86_64"): "x86_64-apple-darwin",
    ("Darwin", "arm64"): "aarch64-apple-darwin",
}


class InstallError(RuntimeError):
    """A step failed. The message says which step and why, and nothing has been installed past that point."""


def asset_name_for(system: str, machine: str) -> str:
    """The release asset for this platform, e.g. elan-x86_64-unknown-linux-gnu.tar.gz."""
    triple = TRIPLES.get((system, machine))
    if triple is None:
        raise InstallError(
            f"no elan build for {system} {machine}; supported: {', '.join(sorted(set(TRIPLES.values())))}"
        )
    return f"elan-{triple}.tar.gz"


def published_digest(release: dict, asset: str) -> str:
    """The SHA-256 GitHub publishes for the asset. Refuses if the release gives none, because then nothing can be checked."""
    for entry in release.get("assets", []):
        if entry.get("name") == asset:
            digest = str(entry.get("digest") or "")
            if not digest.startswith("sha256:"):
                raise InstallError(
                    f"release asset {asset} has no sha256 digest; refusing to install an unchecked archive"
                )
            return digest.removeprefix("sha256:")
    raise InstallError(f"latest release has no asset named {asset}")


def asset_url(release: dict, asset: str) -> str:
    for entry in release.get("assets", []):
        if entry.get("name") == asset:
            return str(entry["browser_download_url"])
    raise InstallError(f"latest release has no asset named {asset}")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_digest(path: Path, expected: str) -> None:
    actual = sha256_of(path)
    if actual != expected:
        raise InstallError(
            f"SHA-256 mismatch for {path.name}: expected {expected}, got {actual}. Nothing was installed."
        )


def extract_safely(archive: Path, destination: Path) -> None:
    """Extract a tarball, refusing members with absolute paths or paths that escape the destination."""
    destination = destination.resolve()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (destination / member.name).resolve()
            if not str(target).startswith(str(destination) + os.sep) and target != destination:
                raise InstallError(f"archive member escapes the staging folder: {member.name}")
            if member.issym() or member.islnk():
                raise InstallError(f"archive contains a link, which is refused: {member.name}")
        tar.extractall(destination, filter="data")


def fetch_latest_release(client: httpx.Client) -> dict:
    response = client.get(RELEASE_API, timeout=30.0)
    response.raise_for_status()
    return dict(response.json())


def download(client: httpx.Client, url: str, target: Path) -> None:
    with client.stream("GET", url, timeout=120.0, follow_redirects=True) as response:
        response.raise_for_status()
        with target.open("wb") as handle:
            for chunk in response.iter_bytes(1 << 20):
                handle.write(chunk)


@app.command()
def main(
    install_dir: Path = typer.Option(
        ..., "--install-dir", help="Where elan goes; use ~/.elan for the default location."
    ),
) -> None:
    """Download, verify, and install elan. Installs no Lean toolchain."""
    try:
        install_dir = install_dir.expanduser().resolve()
        system, machine = platform.system(), platform.machine()
        asset = asset_name_for(system, machine)
        with httpx.Client(headers={"User-Agent": "math-trace-install-elan"}) as client:
            release = fetch_latest_release(client)
            tag = str(release.get("tag_name", "unknown"))
            expected = published_digest(release, asset)
            staging = install_dir.parent / f".elan-staging-{tag}"
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            archive = staging / asset
            typer.echo(f"downloading elan {tag}: {asset}")
            download(client, asset_url(release, asset), archive)
        check_digest(archive, expected)
        typer.echo(f"SHA-256 verified: {expected}")
        extract_safely(archive, staging)
        init = staging / "elan-init"
        if not init.is_file():
            raise InstallError("the archive has no elan-init binary")
        init.chmod(0o755)
        env = {**os.environ, "ELAN_HOME": str(install_dir)}
        done = subprocess.run(
            [str(init), "-y", "--no-modify-path", "--default-toolchain", "none"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode != 0:
            raise InstallError(f"elan-init failed ({done.returncode}): {done.stderr.strip() or done.stdout.strip()}")
        shutil.rmtree(staging)
    except InstallError as exc:
        typer.echo(f"ERROR {exc}", err=True)
        raise typer.Exit(1) from None
    except httpx.HTTPError as exc:
        typer.echo(f"ERROR network: {exc}", err=True)
        raise typer.Exit(1) from None
    typer.echo(f"elan {tag} installed in {install_dir}")
    typer.echo(f'add to PATH: export PATH="{install_dir}/bin:$PATH"  (or restart VS Code if it was open)')


if __name__ == "__main__":
    app()
