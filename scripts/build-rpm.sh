#!/bin/bash
# Build RPM package for cryptnox-cli
# Usage: ./build-rpm.sh [version]
#
# Supports: Fedora 38+, RHEL 9+, CentOS Stream 9+

set -e

VERSION="${1:-1.0.3}"
PKG_NAME="cryptnox-cli"
SPEC_FILE="cryptnox-cli.spec"

echo "=== Building ${PKG_NAME} ${VERSION} RPM package ==="

# Check if we're on an RPM-based system
if ! command -v rpmbuild &> /dev/null; then
    echo "Error: rpmbuild not found. Install with:"
    echo "  sudo dnf install rpm-build rpmdevtools"
    exit 1
fi

# Setup RPM build environment
echo "Setting up RPM build environment..."
rpmdev-setuptree 2>/dev/null || mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"

# Download source from PyPI
echo "Downloading ${PKG_NAME} ${VERSION} from PyPI..."
cd ~/rpmbuild/SOURCES
pip3 download --no-deps --no-binary :all: "${PKG_NAME}==${VERSION}" || {
    echo "Error: Failed to download ${PKG_NAME}==${VERSION}"
    exit 1
}

# Find the downloaded tarball
TAR_FILE=$(ls ${PKG_NAME}*.tar.gz 2>/dev/null || ls cryptnox_cli*.tar.gz 2>/dev/null | head -1)
if [ -z "$TAR_FILE" ]; then
    echo "Error: Could not find downloaded tarball"
    exit 1
fi
echo "Found source: ${TAR_FILE}"

# Create spec file
echo "Creating RPM spec file..."
cat > ~/rpmbuild/SPECS/${SPEC_FILE} << EOF
Name:           ${PKG_NAME}
Version:        ${VERSION}
Release:        1%{?dist}
Summary:        CLI for managing Cryptnox smart card wallets

License:        LGPLv3+
URL:            https://www.cryptnox.com
Source0:        ${TAR_FILE}

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  swig
BuildRequires:  pcsc-lite-devel
BuildRequires:  gcc

Requires:       python3
Requires:       python3-pyscard
Requires:       python3-cryptography
Requires:       pcsc-lite
Requires:       pcsc-lite-libs

%description
cryptnox-cli is a command-line interface for managing Cryptnox Smart cards,
enabling secure seed initialization and cryptographic signing for Bitcoin
and Ethereum.

Supported hardware:
- Cryptnox Smart cards
- Standard PC/SC Smart card Readers (USB NFC or USB smart card reader)

%prep
%autosetup -n cryptnox_cli-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/cryptnox_cli/
%{python3_sitelib}/cryptnox_cli-%{version}*
%{_bindir}/cryptnox

%changelog
* $(date "+%a %b %d %Y") Ko Ko Ye <kokoye2007@gmail.com> - ${VERSION}-1
- Initial RPM package
- CLI for managing Cryptnox smart card wallets
EOF

# Build the RPM
echo "Building RPM package..."
cd ~/rpmbuild/SPECS
rpmbuild -ba ${SPEC_FILE}

# Show results
echo ""
echo "=== Build complete ==="
echo "RPM packages:"
ls -la ~/rpmbuild/RPMS/*/${PKG_NAME}*.rpm 2>/dev/null || echo "No RPM files found"
echo ""
echo "Source RPM:"
ls -la ~/rpmbuild/SRPMS/${PKG_NAME}*.rpm 2>/dev/null || echo "No SRPM files found"
echo ""
echo "To install: sudo dnf install ~/rpmbuild/RPMS/\$(uname -m)/${PKG_NAME}-${VERSION}-1.*.rpm"
