#!/bin/bash
# Sat Apr 19 09:46:01 EDT 2025

set -e  # Exit on error
set -u  # Treat unset variables as errors

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Defaults
VERBOSE=0
OUTPUT_DIR=""  # Initially unset

# Get the computer name
COMPUTER_NAME=$(scutil --get ComputerName)

# Help message
print_help() {
    cat <<EOF
Usage: $0 [-v] [--outdir DIR] [-h|--help]

Creates timestamped ZIP backups of the Mixxx configuration and music directories.

Options:
  -v              Verbose mode (shows debug output)
  --outdir DIR    Output directory for backup files (default: script location)
  -h, --help      Show this help message and exit

Backed up:
  - Config: ~/Library/Containers/org.mixxx.mixxx/data/Library/Application Support/mixxx
  - Music:  ~/Music/Mixxx

Creates:
  CONFIG_YYYYMMDD_<COMPUTER_NAME>.zip
  MUSIC_YYYYMMDD_<COMPUTER_NAME>.zip

Example:
  $0 -v --outdir ~/Backups

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -v)
            VERBOSE=1
            shift
            ;;
        --outdir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

# Enable verbose/debug mode if requested
[[ $VERBOSE -eq 1 ]] && set -x

# Check zip availability
if ! command -v zip >/dev/null; then
    echo -e "${RED}Error: 'zip' command not found. Please install it.${NC}"
    exit 1
fi

# Source directories
CONFIG_DIR="$HOME/Library/Containers/org.mixxx.mixxx/data/Library/Application Support/mixxx"
MUSIC_DIR="$HOME/Music/Mixxx"

# Validate source directories
if [ ! -d "$CONFIG_DIR" ] || [ ! -d "$MUSIC_DIR" ]; then
    echo -e "${RED}Error: Both source directories must exist to proceed.${NC}"
    echo "Missing:"
    [ ! -d "$CONFIG_DIR" ] && echo "  - $CONFIG_DIR"
    [ ! -d "$MUSIC_DIR" ] && echo "  - $MUSIC_DIR"
    exit 1
fi

# Ensure the output directory exists only if --outdir is provided
if [ -n "$OUTPUT_DIR" ]; then
    # Use user-provided output directory
    mkdir -p "$OUTPUT_DIR"
else
    # Default to script's location if --outdir is not provided
    OUTPUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Get timestamp
DATESTAMP=$(date +"%Y%m%d")
CONFIG_ZIP="$OUTPUT_DIR/CONFIG_${DATESTAMP}_${COMPUTER_NAME}.zip"
MUSIC_ZIP="$OUTPUT_DIR/MUSIC_${DATESTAMP}_${COMPUTER_NAME}.zip"

# Backup function with confirmation
zip_directory_contents() {
    local dir="$1"
    local zipfile="$2"

    if [ -f "$zipfile" ]; then
        read -p "File '$zipfile' exists. Overwrite? (y/N): " answer
        [[ "$answer" =~ ^[Yy]$ ]] || { echo -e "${YELLOW}Skipped: $zipfile${NC}"; return 1; }
    fi

    echo "Zipping $dir -> $zipfile"
    (cd "$dir" && zip -qr "$zipfile" .)

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Success: $zipfile created${NC}"
    else
        echo -e "${RED}Failed to create: $zipfile${NC}"
        return 2
    fi
}

# Run backups
zip_directory_contents "$CONFIG_DIR" "$CONFIG_ZIP"
zip_directory_contents "$MUSIC_DIR" "$MUSIC_ZIP"

echo -e "${GREEN}Backup complete.${NC}"

