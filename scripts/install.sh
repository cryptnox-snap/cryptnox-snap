#!/bin/bash
# Cryptnox CLI Universal Installer
# Supports: Snap, Deb (Debian/Ubuntu/Mint), RPM (Fedora/RHEL), pip (fallback)
#
# Usage: curl -fsSL https://raw.githubusercontent.com/kokoye2007/cryptnox-snap/main/scripts/install.sh | bash
#    or: ./install.sh [--snap|--deb|--rpm|--pip]

set -e

# Cleanup on failure
cleanup() {
    rm -f /tmp/cryptnox-cli_*.deb 2>/dev/null || true
}
trap cleanup EXIT

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Version - fetch from PyPI if not specified
get_latest_version() {
    curl -fsSL https://pypi.org/pypi/cryptnox-cli/json 2>/dev/null | grep -o '"version":"[^"]*"' | head -1 | cut -d'"' -f4
}

VERSION="${CRYPTNOX_VERSION:-$(get_latest_version)}"
VERSION="${VERSION:-1.0.3}" # Fallback if fetch fails

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if sudo is available
check_sudo() {
    if ! command -v sudo &> /dev/null; then
        log_error "sudo is required but not found. Please install sudo or run as root."
        exit 1
    fi
}

# Detect OS and package manager
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        OS_NAME=$PRETTY_NAME
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        OS_VERSION=$DISTRIB_RELEASE
        OS_NAME=$DISTRIB_DESCRIPTION
    else
        OS=$(uname -s)
        OS_VERSION=$(uname -r)
        OS_NAME=$OS
    fi

    # Detect package manager
    if command -v snap &> /dev/null; then
        HAS_SNAP=true
    else
        HAS_SNAP=false
    fi

    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
    else
        PKG_MANAGER="unknown"
    fi

    log_info "Detected: $OS_NAME"
    log_info "Package manager: $PKG_MANAGER"
    log_info "Snap available: $HAS_SNAP"
}

# Install system dependencies
install_dependencies() {
    check_sudo
    log_info "Installing system dependencies..."

    case $PKG_MANAGER in
        apt)
            sudo apt-get update
            sudo apt-get install -y pcscd libpcsclite1 pcsc-tools python3-pip python3-pyscard
            ;;
        dnf|yum)
            sudo $PKG_MANAGER install -y pcsc-lite pcsc-lite-libs pcsc-tools python3-pip python3-pyscard
            sudo systemctl enable --now pcscd
            ;;
        pacman)
            sudo pacman -Syu --noconfirm pcsclite ccid python-pip python-pyscard
            sudo systemctl enable --now pcscd
            ;;
        zypper)
            sudo zypper install -y pcsc-lite pcsc-ccid python3-pip python3-pyscard
            sudo systemctl enable --now pcscd
            ;;
        *)
            log_warn "Unknown package manager. Please install pcscd manually."
            ;;
    esac
}

# Install via Snap
install_snap() {
    log_info "Installing via Snap..."

    if ! command -v snap &> /dev/null; then
        log_info "Installing snapd..."
        case $PKG_MANAGER in
            apt)
                sudo apt-get update && sudo apt-get install -y snapd
                ;;
            dnf|yum)
                sudo $PKG_MANAGER install -y snapd
                sudo systemctl enable --now snapd.socket
                sudo ln -sf /var/lib/snapd/snap /snap 2>/dev/null || true
                ;;
            pacman)
                log_warn "Install snapd from AUR: yay -S snapd"
                return 1
                ;;
            *)
                log_error "Cannot install snapd automatically"
                return 1
                ;;
        esac
    fi

    sudo snap install cryptnox

    log_info "Connecting required interfaces for USB card readers..."
    sudo snap connect cryptnox:raw-usb || true
    sudo snap connect cryptnox:hardware-observe || true

    log_success "Installed via Snap"
    log_info "Use: cryptnox.card"
}

# Install via Deb package
install_deb() {
    log_info "Installing via Deb package..."

    if [ "$PKG_MANAGER" != "apt" ]; then
        log_error "Deb installation requires apt (Debian/Ubuntu/Mint)"
        return 1
    fi

    install_dependencies

    # Check for pre-built deb in releases
    RELEASE_URL="https://github.com/kokoye2007/cryptnox-snap/releases/latest/download"
    ARCH=$(dpkg --print-architecture)
    DEB_FILE="cryptnox-cli_${VERSION}-1_${ARCH}.deb"

    log_info "Checking for pre-built package..."
    if curl -fsSL -o "/tmp/${DEB_FILE}" "${RELEASE_URL}/${DEB_FILE}" 2>/dev/null; then
        log_info "Installing pre-built package..."
        sudo dpkg -i "/tmp/${DEB_FILE}" || sudo apt-get install -f -y
        rm -f "/tmp/${DEB_FILE}"
    else
        log_warn "Pre-built package not found, falling back to pip..."
        install_pip
        return
    fi

    log_success "Installed via Deb"
    log_info "Use: cryptnox"
}

# Install via RPM package
install_rpm() {
    log_info "Installing via RPM/pip for Fedora/RHEL..."

    if [ "$PKG_MANAGER" != "dnf" ] && [ "$PKG_MANAGER" != "yum" ]; then
        log_error "RPM installation requires dnf/yum (Fedora/RHEL/CentOS)"
        return 1
    fi

    install_dependencies

    # RPM not yet available, use pip
    log_info "Installing cryptnox-cli via pip..."
    pip3 install --user cryptnox-cli

    log_success "Installed via pip"
    log_info "Use: ~/.local/bin/cryptnox or add ~/.local/bin to PATH"
}

# Install via pip (fallback)
install_pip() {
    log_info "Installing via pip..."

    install_dependencies

    # Ensure pip is available
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 not found. Please install python3-pip."
        return 1
    fi

    pip3 install --user cryptnox-cli

    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        log_warn "Add ~/.local/bin to your PATH:"
        log_warn "  echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.bashrc"
    fi

    log_success "Installed via pip"
    log_info "Use: ~/.local/bin/cryptnox"
}

# Setup card reader (blacklist kernel modules)
setup_reader() {
    log_info "Setting up card reader..."

    cat << 'EOF' | sudo tee /etc/modprobe.d/blacklist-nfc.conf > /dev/null
# Blacklist NFC modules for PC/SC compatibility
blacklist nfc
blacklist pn533
blacklist pn533_usb
EOF

    log_success "NFC modules blacklisted"
    log_warn "Reboot required for changes to take effect"
}

# Auto-detect best installation method
auto_install() {
    detect_os

    echo ""
    log_info "Selecting best installation method..."

    # Priority: Snap > Deb > RPM/pip > pip
    case $OS in
        ubuntu|debian|linuxmint|pop|elementary|zorin)
            if [ "$HAS_SNAP" = true ]; then
                install_snap
            else
                install_deb
            fi
            ;;
        fedora|rhel|centos|rocky|alma)
            if [ "$HAS_SNAP" = true ]; then
                install_snap
            else
                install_rpm
            fi
            ;;
        arch|manjaro|endeavouros)
            if [ "$HAS_SNAP" = true ]; then
                install_snap
            else
                install_pip
            fi
            ;;
        opensuse*)
            if [ "$HAS_SNAP" = true ]; then
                install_snap
            else
                install_pip
            fi
            ;;
        *)
            log_warn "Unknown distribution: $OS"
            log_info "Trying pip installation..."
            install_pip
            ;;
    esac
}

# Show usage
usage() {
    cat << EOF
Cryptnox CLI Universal Installer

Usage: $0 [OPTIONS]

Options:
    --snap      Force Snap installation
    --deb       Force Deb package installation
    --rpm       Force RPM/pip installation
    --pip       Force pip installation
    --setup     Setup card reader (blacklist NFC modules)
    --help      Show this help

Environment variables:
    CRYPTNOX_VERSION    Version to install (default: $VERSION)

Examples:
    $0              # Auto-detect and install
    $0 --snap       # Install via Snap
    $0 --deb        # Install via Deb
    $0 --setup      # Setup card reader

EOF
}

# Main
main() {
    echo ""
    echo "========================================"
    echo "  Cryptnox CLI Installer v${VERSION}"
    echo "========================================"
    echo ""

    case "${1:-}" in
        --snap)
            detect_os
            install_snap
            ;;
        --deb)
            detect_os
            install_deb
            ;;
        --rpm)
            detect_os
            install_rpm
            ;;
        --pip)
            detect_os
            install_pip
            ;;
        --setup)
            setup_reader
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        "")
            auto_install
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac

    echo ""
    log_success "Installation complete!"
    echo ""
}

main "$@"
