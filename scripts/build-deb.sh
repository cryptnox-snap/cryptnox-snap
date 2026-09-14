#!/bin/bash
# Build Debian package for cryptnox-cli
# Usage: ./build-deb.sh [version]
#
# Supports: Debian 12+, Ubuntu 22.04+, Linux Mint 21+

set -e

# Capture script location BEFORE any cd commands
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"

VERSION="${1:-1.0.3}"
PKG_NAME="cryptnox-cli"
BUILD_DIR="${BUILD_DIR:-$(mktemp -d /tmp/cryptnox-deb-build.XXXXXX)}"
SKIP_DEPS="${SKIP_DEPS:-false}"

# cryptnox-cli 1.0.4 declares Requires-Python <=3.14, which pip interprets
# as <=3.14.0.  Hosts running Python 3.14.x (for example 3.14.4) therefore
# need a compatible interpreter for the source download.  Prefer an installed
# Python 3.12/3.13/3.11 while allowing callers to override the choice.
if [[ -z "${PYTHON_BIN:-}" ]]; then
    for candidate in python3.13 python3.12 python3.11; do
        if command -v "${candidate}" >/dev/null 2>&1; then
            PYTHON_BIN="$(command -v "${candidate}")"
            break
        fi
    done
fi
if [[ -z "${PYTHON_BIN:-}" ]]; then
    echo "Error: cryptnox-cli ${VERSION} requires Python 3.11-3.14.0." >&2
    echo "Install python3.11/3.12/3.13 or set PYTHON_BIN to a compatible interpreter." >&2
    exit 1
fi
export PYTHON_BIN

echo "=== Building ${PKG_NAME} ${VERSION} deb package ==="
echo "Build directory: ${BUILD_DIR}"
echo "Repo root: ${REPO_ROOT}"
echo "Python for source download: ${PYTHON_BIN} ($(${PYTHON_BIN} --version 2>&1))"

# Cleanup previous build if using default location
if [[ "${BUILD_DIR}" == /tmp/cryptnox-deb-build.* ]]; then
    trap "rm -rf ${BUILD_DIR}" EXIT
fi
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Download source from PyPI
echo "Downloading ${PKG_NAME} ${VERSION} from PyPI..."
"${PYTHON_BIN}" -m pip download --no-deps --no-binary :all: "${PKG_NAME}==${VERSION}"

# Extract source
TAR_FILE=$(ls ${PKG_NAME}*.tar.gz 2>/dev/null || ls ${PKG_NAME//-/_}*.tar.gz)
echo "Extracting ${TAR_FILE}..."
tar -xzf "${TAR_FILE}"

# Find extracted directory
SRC_DIR=$(find . -maxdepth 1 -type d -name "${PKG_NAME}*" -o -name "${PKG_NAME//-/_}*" | grep -v "^\.$" | head -1)
if [ -z "${SRC_DIR}" ]; then
    SRC_DIR=$(find . -maxdepth 1 -type d ! -name "." | head -1)
fi

# Rename to Debian standard format
DEBIAN_DIR="${PKG_NAME}-${VERSION}"
mv "${SRC_DIR}" "${DEBIAN_DIR}"
cd "${DEBIAN_DIR}"

# Copy debian directory from repo root
if [ -d "${REPO_ROOT}/debian" ]; then
    cp -r "${REPO_ROOT}/debian" .
    echo "Copied debian/ from ${REPO_ROOT}"
else
    echo "Error: debian/ directory not found at ${REPO_ROOT}"
    exit 1
fi

# Update changelog version if different
if [ "${VERSION}" != "1.0.3" ]; then
    sed -i "s/1.0.3-1/${VERSION}-1/g" debian/changelog
fi

# Install build dependencies (skip with SKIP_DEPS=true)
if [ "${SKIP_DEPS}" != "true" ]; then
    echo "Installing build dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        debhelper \
        dh-python \
        python3-all \
        python3-setuptools \
        python3-pip \
        pybuild-plugin-pyproject \
        swig \
        libpcsclite-dev \
        pcscd \
        devscripts \
        fakeroot
else
    echo "Skipping dependency installation (SKIP_DEPS=true)"
fi

# Build the package
echo "Building package..."
dpkg-buildpackage -us -uc -b

# Copy results
echo "=== Build complete ==="
echo "Packages are in: ${BUILD_DIR}"
ls -la "${BUILD_DIR}"/*.deb 2>/dev/null || echo "No .deb files found"

echo ""
echo "To install: sudo dpkg -i ${BUILD_DIR}/${PKG_NAME}_${VERSION}-1_*.deb"
echo "Then fix dependencies: sudo apt-get install -f"
