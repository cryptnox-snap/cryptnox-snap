#!/bin/bash
# Upload snap packages to Snap Store
# Usage: ./upload-store.sh [channel] [snap_files...]
#
# Examples:
#   ./upload-store.sh                    # Upload all snaps to edge
#   ./upload-store.sh stable             # Upload all snaps to stable
#   ./upload-store.sh edge foo.snap      # Upload specific snap to edge

set -e

# Default channel
CHANNEL="${1:-edge}"
MAX_RETRIES="${MAX_RETRIES:-3}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if logged in
check_login() {
    if ! snapcraft whoami &>/dev/null; then
        log_error "Not logged in to Snap Store. Run: snapcraft login"
        exit 1
    fi
    log_info "Logged in as: $(snapcraft whoami | grep email | awk '{print $2}')"
}

# Upload a single snap with retries
upload_snap() {
    local snap_file="$1"
    local channel="$2"
    local count=0

    if [ ! -f "$snap_file" ]; then
        log_error "Snap file not found: $snap_file"
        return 1
    fi

    log_info "Uploading: $snap_file -> $channel"

    while [ $count -lt $MAX_RETRIES ]; do
        if snapcraft upload "$snap_file" --release="$channel"; then
            log_success "Uploaded: $snap_file"
            return 0
        fi
        ((count++))
        log_warn "Retry $count/$MAX_RETRIES for $snap_file"
        sleep 5
    done

    log_error "Failed to upload after $MAX_RETRIES attempts: $snap_file"
    return 1
}

# Show current store status
show_status() {
    log_info "Current Snap Store status:"
    snapcraft status cryptnox 2>/dev/null || log_warn "Could not get status"
}

# Main
main() {
    echo ""
    echo "========================================"
    echo "  Snap Store Uploader"
    echo "========================================"
    echo ""

    check_login

    # Determine snap files to upload
    shift 2>/dev/null || true  # Remove channel arg if present

    if [ $# -gt 0 ]; then
        # Specific files provided
        SNAP_FILES=("$@")
    else
        # Find all snap files in current directory
        SNAP_FILES=(*.snap)
        if [ ! -f "${SNAP_FILES[0]}" ]; then
            log_error "No snap files found in current directory"
            exit 1
        fi
    fi

    log_info "Channel: $CHANNEL"
    log_info "Files to upload: ${#SNAP_FILES[@]}"
    echo ""

    # Upload each snap
    local failed=0
    for snap in "${SNAP_FILES[@]}"; do
        if ! upload_snap "$snap" "$CHANNEL"; then
            ((failed++))
        fi
    done

    echo ""
    if [ $failed -eq 0 ]; then
        log_success "All uploads completed successfully!"
    else
        log_error "$failed upload(s) failed"
    fi

    echo ""
    show_status
}

main "$@"
