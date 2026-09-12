# Cryptnox Packaging

[![Check Cryptnox-CLI Version](https://github.com/cryptnox-snap/cryptnox-snap/actions/workflows/check_cryptnox_version.yml/badge.svg)](https://github.com/cryptnox-snap/cryptnox-snap/actions/workflows/check_cryptnox_version.yml)

Multi-format packaging for [Cryptnox CLI](https://github.com/Cryptnox-Software/cryptnox-cli) - CLI for managing Cryptnox smart card wallets.

![Cryptnox Cards CLI](https://dashboard.snapcraft.io/site_media/appmedia/2021/10/cryptnoxcard_small_QSpKpFT.png)

## Quick Install

```bash
# Universal installer (auto-detects OS)
curl -fsSL https://raw.githubusercontent.com/kokoye2007/cryptnox-snap/main/scripts/install.sh | bash

# Or with options
curl -fsSL https://raw.githubusercontent.com/kokoye2007/cryptnox-snap/main/scripts/install.sh | bash -s -- --snap
curl -fsSL https://raw.githubusercontent.com/kokoye2007/cryptnox-snap/main/scripts/install.sh | bash -s -- --deb
curl -fsSL https://raw.githubusercontent.com/kokoye2007/cryptnox-snap/main/scripts/install.sh | bash -s -- --pip
```

## Supported Formats

| Format | Distributions | Status |
|--------|--------------|--------|
| Snap | Ubuntu, Debian, Fedora, Arch, etc. | [![Snap Store](https://snapcraft.io/en/dark/install.svg)](https://snapcraft.io/cryptnox) |
| Deb | Debian 12+, Ubuntu 22.04+, Linux Mint 21+ | Available |
| RPM | Fedora, RHEL, CentOS (via pip) | Available |
| pip | Any Linux with Python 3.11+ | Available |

## Directory Structure

```
.
├── snap/                    # Snap packaging
│   ├── snapcraft.yaml       # Snap build configuration
│   └── hooks/               # Snap install/connect hooks
├── debian/                  # Debian packaging template
│   ├── control              # Package metadata
│   ├── rules                # Build rules
│   ├── changelog            # Package changelog
│   └── ...
├── scripts/
│   └── build-deb.sh         # Local deb build script
├── .github/workflows/       # CI/CD
│   ├── check_cryptnox_version.yml  # Weekly PyPI/Debian update check
│   ├── manual_build.yaml           # Manual snap build
│   └── build_deb.yaml              # Deb build workflow
└── version-cryptnox         # Current tracked version
```

## Automatic image rebuilds

Every Saturday, `check_cryptnox_version.yml` checks both the latest
`cryptnox-cli` release on PyPI and the Ubuntu 22.04 candidate versions of the
Debian packages staged in the snap. If either set changes, the workflow commits
the new version state. That commit triggers the repository's connected
Snapcraft/Launchpad image build.

The snap build reads `version-cryptnox` and installs that exact PyPI version.
`debian-dependencies.lock` is detection state only: Snapcraft still resolves the
listed Debian packages from the `core22` archive during the fresh build.

## Snap Installation

### From Snap Store (Recommended)

```bash
sudo snap install cryptnox
```

### Connect Required Interfaces

```bash
sudo snap connect cryptnox:raw-usb
sudo snap connect cryptnox:hardware-observe
sudo snap connect cryptnox:removable-media
```

### Usage

```bash
cryptnox.card          # Main CLI
cryptnox.pcsc-scan     # Scan for card readers
snap services cryptnox # Check pcscd service
```

## Debian Package Installation

### From GitHub Releases

Download the `.deb` file from [Releases](https://github.com/kokoye2007/cryptnox-snap/releases) and install:

```bash
sudo dpkg -i cryptnox-cli_*.deb
sudo apt-get install -f  # Install dependencies
```

### Build Locally

```bash
git clone https://github.com/kokoye2007/cryptnox-snap
cd cryptnox-snap
./scripts/build-deb.sh [version]
```

## Building from Source

### Snap

```bash
# Using LXD (local)
snapcraft --use-lxd

# Using Multipass (default)
snapcraft

# Remote build (Launchpad)
snapcraft remote-build --build-for=amd64,arm64
```

### Deb

```bash
# Automatic (downloads from PyPI)
./scripts/build-deb.sh 1.0.3

# Packages will be in /tmp/cryptnox-deb-build/
```

## Card Reader Setup

Some NFC readers require kernel module blacklisting:

```bash
echo "blacklist nfc" | sudo tee -a /etc/modprobe.d/blacklist-nfc.conf
echo "blacklist pn533" | sudo tee -a /etc/modprobe.d/blacklist-nfc.conf
echo "blacklist pn533_usb" | sudo tee -a /etc/modprobe.d/blacklist-nfc.conf
sudo reboot
```

## Components

| Component | Version | Description |
|-----------|---------|-------------|
| cryptnox-cli | 1.0.3 | Cryptnox CLI from PyPI |
| pcscd | 2.3.0 | PC/SC Smart Card Daemon |
| ccid | 1.6.1 | CCID USB driver |
| acsccid | 1.1.11 | ACS card reader driver |
| pcsc-tools | 1.7.3 | PC/SC debugging tools |
| Python | 3.12.7 | Python runtime (snap only) |

## Links

- [Cryptnox Website](https://www.cryptnox.com)
- [Cryptnox CLI Source](https://github.com/Cryptnox-Software/cryptnox-cli)
- [Snap Store](https://snapcraft.io/cryptnox)
- [PyPI Package](https://pypi.org/project/cryptnox-cli/)

## License

LGPL-3.0 - See [LICENSE](LICENSE) for details.
