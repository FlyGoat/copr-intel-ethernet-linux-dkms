#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.request


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "drivers.json")
MAINTAINER = "FlyGoat <flygoat@users.noreply.github.com>"


def request(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "intel-ethernet-linux-dkms-updater",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        return json.load(f)


def write_manifest(data):
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def github_json(url):
    with urllib.request.urlopen(request(url), timeout=60) as resp:
        return json.load(resp)


def latest_release(repo):
    return github_json(f"https://api.github.com/repos/{repo}/releases/latest")


def choose_asset(driver, release):
    version = release["tag_name"].removeprefix("v")
    expected = f"{driver['name']}-{version}.tar.gz"
    assets = release.get("assets", [])
    for asset in assets:
        if asset.get("name") == expected:
            return version, asset

    candidates = [
        asset for asset in assets
        if asset.get("name", "").startswith(f"{driver['name']}-{version}")
        and asset.get("name", "").endswith(".tar.gz")
    ]
    if len(candidates) == 1:
        return version, candidates[0]

    names = ", ".join(asset.get("name", "") for asset in assets)
    raise RuntimeError(
        f"Could not find release asset {expected} in {driver['upstream']} "
        f"release {release['tag_name']}. Assets: {names}"
    )


def asset_sha256(asset):
    digest = asset.get("digest") or ""
    if digest.startswith("sha256:"):
        return digest.split(":", 1)[1]

    sha = hashlib.sha256()
    with urllib.request.urlopen(request(asset["browser_download_url"]), timeout=300) as resp:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def spec_version(spec_path):
    with open(spec_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"^Version:\s*(\S+)", line)
            if match:
                return match.group(1)
    raise RuntimeError(f"No Version tag found in {spec_path}")


def update_spec(driver, old_version, new_version):
    spec_path = os.path.join(ROOT, driver["spec"])
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    content, count = re.subn(
        r"^Version:\s*\S+",
        f"Version:        {new_version}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError(f"Could not update Version tag in {driver['spec']}")

    if new_version != old_version:
        content, count = re.subn(
            r"^Release:\s*\S+",
            "Release:        1%{?dist}",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise RuntimeError(f"Could not reset Release tag in {driver['spec']}")

        today = dt.datetime.now(dt.timezone.utc).strftime("%a %b %d %Y")
        entry = (
            f"%changelog\n"
            f"* {today} {MAINTAINER} - {new_version}-1\n"
            f"- Update to upstream {driver['name']} {new_version}.\n\n"
        )
        content = content.replace("%changelog\n", entry, 1)

    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(content)


def validate_local(data):
    errors = []
    for driver in data["drivers"]:
        spec_path = os.path.join(ROOT, driver["spec"])
        if not os.path.exists(spec_path):
            errors.append(f"{driver['name']}: missing {driver['spec']}")
            continue

        version = spec_version(spec_path)
        if version != driver["version"]:
            errors.append(
                f"{driver['name']}: {driver['spec']} Version is {version}, "
                f"drivers.json has {driver['version']}"
            )

        expected_asset = f"{driver['name']}-{driver['version']}.tar.gz"
        if driver.get("asset") != expected_asset:
            errors.append(
                f"{driver['name']}: asset is {driver.get('asset')}, "
                f"expected {expected_asset}"
            )

        expected_tag = f"v{driver['version']}"
        if driver.get("tag") != expected_tag:
            errors.append(
                f"{driver['name']}: tag is {driver.get('tag')}, "
                f"expected {expected_tag}"
            )

    if errors:
        raise RuntimeError("\n".join(errors))


def refresh(data, selected):
    changed = False
    for driver in data["drivers"]:
        if selected and driver["name"] not in selected and driver["package"] not in selected:
            continue

        release = latest_release(driver["upstream"])
        version, asset = choose_asset(driver, release)
        sha256 = asset_sha256(asset)

        old_version = driver["version"]
        updates = {
            "version": version,
            "tag": release["tag_name"],
            "asset": asset["name"],
            "sha256": sha256,
        }
        for key, value in updates.items():
            if driver.get(key) != value:
                driver[key] = value
                changed = True

        spec_path = os.path.join(ROOT, driver["spec"])
        if spec_version(spec_path) != version:
            update_spec(driver, old_version, version)
            changed = True

    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh release metadata from GitHub and update files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate that specs and manifest agree",
    )
    parser.add_argument(
        "--driver",
        action="append",
        default=[],
        help="driver name or package name to refresh; defaults to all",
    )
    args = parser.parse_args()

    data = load_manifest()
    try:
        if args.write:
            changed = refresh(data, set(args.driver))
            write_manifest(data)
            validate_local(data)
            if changed:
                print("Updated upstream release metadata.")
            else:
                print("All tracked drivers are already current.")
        elif args.check:
            validate_local(data)
            print("Driver manifest and specs are consistent.")
        else:
            parser.error("use --check or --write")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
