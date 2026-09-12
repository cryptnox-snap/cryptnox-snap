# Cryptnox Packaging Makefile
# Supports: snap, deb, rpm, pip install

SHELL := /bin/bash
VERSION := $(shell curl -s https://pypi.org/pypi/cryptnox-cli/json 2>/dev/null | grep -o '"version":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "1.0.3")
PACKAGE := cryptnox-cli
BUILD_DIR := /tmp/cryptnox-build

.PHONY: all help clean snap deb rpm pip install uninstall test version

all: help

help:
	@echo "Cryptnox Packaging - Version $(VERSION)"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Build targets:"
	@echo "  snap          Build snap package (requires snapcraft)"
	@echo "  snap-remote   Build snap via Launchpad remote build"
	@echo "  deb           Build Debian package"
	@echo "  rpm           Build RPM package (Fedora/RHEL)"
	@echo ""
	@echo "Install targets:"
	@echo "  install       Install via best method for this OS"
	@echo "  install-snap  Install via snap"
	@echo "  install-deb   Install via deb"
	@echo "  install-pip   Install via pip"
	@echo "  uninstall     Remove cryptnox"
	@echo ""
	@echo "Other targets:"
	@echo "  clean         Clean build artifacts"
	@echo "  test          Test the installation"
	@echo "  version       Show versions"
	@echo "  upload        Upload snap to store (edge)"
	@echo ""

version:
	@echo "Package: $(PACKAGE)"
	@echo "Version: $(VERSION)"
	@echo "Build dir: $(BUILD_DIR)"

# === SNAP ===
snap:
	@echo "Building snap locally..."
	snapcraft --use-lxd

snap-remote:
	@echo "Building snap via Launchpad..."
	snapcraft remote-build --launchpad-accept-public-upload --build-for=amd64,arm64

snap-clean:
	snapcraft clean

upload:
	@echo "Uploading snaps to edge channel..."
	@for snap in *.snap; do \
		if [ -f "$$snap" ]; then \
			echo "Uploading $$snap..."; \
			snapcraft upload "$$snap" --release=edge || true; \
		fi; \
	done

# === DEB ===
deb:
	@echo "Building Debian package..."
	@./scripts/build-deb.sh $(VERSION)

deb-clean:
	rm -rf $(BUILD_DIR)

# === RPM ===
rpm:
	@echo "Building RPM package..."
	@./scripts/build-rpm.sh $(VERSION)

rpm-clean:
	rm -rf ~/rpmbuild/BUILD/$(PACKAGE)*
	rm -rf ~/rpmbuild/RPMS/*/$(PACKAGE)*

# === INSTALL ===
install:
	@./scripts/install.sh

install-snap:
	@./scripts/install.sh --snap

install-deb:
	@./scripts/install.sh --deb

install-pip:
	@./scripts/install.sh --pip

uninstall:
	@echo "Uninstalling cryptnox..."
	@if command -v snap &>/dev/null && snap list cryptnox &>/dev/null; then \
		sudo snap remove cryptnox; \
	elif dpkg -l | grep -q cryptnox-cli; then \
		sudo apt-get remove -y cryptnox-cli; \
	elif rpm -q cryptnox-cli &>/dev/null; then \
		sudo dnf remove -y cryptnox-cli || sudo yum remove -y cryptnox-cli; \
	elif pip3 show cryptnox-cli &>/dev/null; then \
		pip3 uninstall -y cryptnox-cli; \
	else \
		echo "cryptnox not found"; \
	fi

# === TEST ===
test:
	@echo "Testing cryptnox installation..."
	@if command -v cryptnox &>/dev/null; then \
		cryptnox --version || cryptnox --help | head -5; \
	elif command -v cryptnox.card &>/dev/null; then \
		cryptnox.card --version || cryptnox.card --help | head -5; \
	else \
		echo "cryptnox not found in PATH"; \
		exit 1; \
	fi

# === CLEAN ===
clean: snap-clean deb-clean
	rm -f *.snap
	rm -f *.deb
	rm -f *.rpm
	rm -f *.log
	rm -f *.txt
	@echo "Cleaned build artifacts"

# === DEV ===
dev-deps:
	@echo "Installing development dependencies..."
	sudo apt-get update
	sudo apt-get install -y snapcraft lxd debhelper dh-python python3-all \
		python3-setuptools python3-pip pybuild-plugin-pyproject \
		swig libpcsclite-dev pcscd devscripts fakeroot
