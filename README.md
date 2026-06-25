# Intel Ethernet Linux DKMS Packaging

This repository carries COPR/rpkg packaging for Intel's out-of-tree Ethernet
Linux drivers.

Tracked packages:

| Package | Upstream | Version |
| --- | --- | --- |
| `ice-dkms` | `intel/ethernet-linux-ice` | `2.6.6` |
| `iavf-dkms` | `intel/ethernet-linux-iavf` | `4.13.35` |

## Layout

- `ice-dkms.spec` and `iavf-dkms.spec` are top-level COPR package specs.
- `drivers.json` is the single source of truth for tracked upstream release
  metadata.
- `scripts/update-drivers.py` refreshes GitHub release versions, asset names,
  and SHA-256 digests.
- `scripts/copr-rpkg-setup.sh` creates or updates COPR SCM package definitions.

## Local rpkg Flow

Install `rpkg` in a Fedora environment, then build SRPMs from the top-level
specs:

```sh
make validate
make srpm-ice
make srpm-iavf
```

Or call `rpkg` directly:

```sh
rpkg srpm --outdir dist/srpm --spec ice-dkms.spec
rpkg srpm --outdir dist/srpm --spec iavf-dkms.spec
```

## COPR Setup

After publishing this repository to GitHub, configure COPR packages to use SCM
with the `rpkg` SRPM build method:

```sh
COPR_REPO=flygoat/intel-ethernet-linux-dkms \
CLONE_URL=https://github.com/FlyGoat/copr-intel-ethernet-linux-dkms.git \
scripts/copr-rpkg-setup.sh
```

Then trigger builds:

```sh
copr-cli build-package flygoat/intel-ethernet-linux-dkms --name ice-dkms
copr-cli build-package flygoat/intel-ethernet-linux-dkms --name iavf-dkms
```

The same settings can be entered in the COPR web UI:

- Source type: SCM
- Type: Git
- Clone URL: `https://github.com/FlyGoat/copr-intel-ethernet-linux-dkms.git`
- Committish: `main`
- Method: `rpkg`
- Spec file: `ice-dkms.spec` or `iavf-dkms.spec`

## Upstream Updates

The scheduled GitHub Action runs:

```sh
python3 scripts/update-drivers.py --write
```

If Intel publishes a newer GitHub release with a matching release asset, the
workflow opens a pull request updating `drivers.json`, the spec `Version:`, and
the changelog entry.

## Adding Another Driver

To add another Intel driver such as `i40e`:

1. Add a new entry to `drivers.json`.
2. Add a matching top-level `<driver>-dkms.spec`.
3. Add it to the `SPECS` list in `Makefile`, the CI matrix, and
   `scripts/copr-rpkg-setup.sh`.
4. Run `python3 scripts/update-drivers.py --write`.
