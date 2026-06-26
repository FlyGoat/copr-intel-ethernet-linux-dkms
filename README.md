# Ethernet Linux DKMS Packaging

This repository carries COPR/rpkg packaging for out-of-tree Ethernet Linux
kernel modules.

Tracked packages:

| Package | Upstream | Version |
| --- | --- | --- |
| `ice-dkms` | `intel/ethernet-linux-ice` | `2.6.6` |
| `iavf-dkms` | `intel/ethernet-linux-iavf` | `4.13.35` |
| `idpf-dkms` | `intel/ethernet-linux-idpf` | `1.0.11` |
| `i40e-dkms` | `intel/ethernet-linux-i40e` | `2.30.18` |
| `ixgbe-dkms` | `intel/ethernet-linux-ixgbe` | `6.4.4` |
| `ixgbevf-dkms` | `intel/ethernet-linux-ixgbevf` | `5.3.36` |
| `igb-dkms` | `intel/ethernet-linux-igb` | `5.20.28` |
| `dpdk-kmods-dkms` | Debian sid `dpdk-kmods` source package | `0~20241120+git` |

## Layout

- `*-dkms.spec` files are top-level COPR package specs.
- `drivers.json` is the single source of truth for tracked upstream release
  metadata.
- `scripts/update-drivers.py` refreshes GitHub release versions, asset names,
  and SHA-256 digests. Most drivers use release assets; drivers without release
  assets can use GitHub tag archives.
- `dpdk-kmods-dkms.spec` is pinned to the Debian sid source package and is not
  auto-updated by `scripts/update-drivers.py`.
- `scripts/copr-rpkg-setup.sh` creates or updates COPR SCM package definitions.

## Local rpkg Flow

Install `rpkg` in a Fedora environment, then build SRPMs from the top-level
specs:

```sh
make validate
make srpm-all
```

Or call `rpkg` directly:

```sh
rpkg srpm --outdir dist/srpm --spec ice-dkms.spec
rpkg srpm --outdir dist/srpm --spec i40e-dkms.spec
```

## COPR Setup

After publishing this repository to GitHub, configure COPR packages to use SCM
with the `rpkg` SRPM build method:

```sh
COPR_REPO=flygoat/intel-ethernet-linux-dkms \
CLONE_URL=https://github.com/FlyGoat/copr-intel-ethernet-linux-dkms.git \
scripts/copr-rpkg-setup.sh
```

With webhook rebuild enabled, pushes to `main` trigger COPR package builds.

The same settings can be entered in the COPR web UI:

- Source type: SCM
- Type: Git
- Clone URL: `https://github.com/FlyGoat/copr-intel-ethernet-linux-dkms.git`
- Committish: `main`
- Method: `rpkg`
- Spec file: the matching top-level `*-dkms.spec`
- Webhook rebuild: enabled
- GitHub webhook content type: `application/json`

## Upstream Updates

The scheduled GitHub Action runs:

```sh
python3 scripts/update-drivers.py --write
```

If Intel publishes a newer GitHub release with a matching source, the workflow
opens a pull request updating `drivers.json`, the spec `Version:`, and the
changelog entry.

`dpdk-kmods-dkms` is pinned in its spec to Debian sid's source package and is
updated manually.

## Adding Another Driver

To add another Intel driver such as `e1000e`:

1. Add a new entry to `drivers.json`.
2. Add a matching top-level `<driver>-dkms.spec`.
3. Add it to the `SPECS` list in `Makefile`, the CI matrix, and
   `scripts/copr-rpkg-setup.sh`.
4. Run `python3 scripts/update-drivers.py --write`.
