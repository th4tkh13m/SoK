#!/bin/bash

# Interactive debugging script for Apptainer containers used by Vul4C
# Usage: ./debug_container.sh [tool_name] [cveid]

set -e

# Default values
TOOL_NAME=${1:-"VulnFix"}
CVE_ID=${2:-"CVE-2016-10248"}
SOFTWARE=${3:-"jasper"}

# Paths
PROJECT_ROOT="/project/phan/kt477/RLVR-Vuln/Benchmarks/SoK"
SIF_DIR="$PROJECT_ROOT/sif_images"
RUNTIME_DIR="$PROJECT_ROOT/vul4c_runtime/${TOOL_NAME}/${SOFTWARE}/${CVE_ID}"

# Convert tool name to SIF file name
TOOL_LOWER=$(echo "$TOOL_NAME" | tr '[:upper:]' '[:lower:]')
SIF_FILE="$SIF_DIR/vul4c_${TOOL_LOWER}_1.0.sif"

echo "=== Vul4C Container Debug Shell ==="
echo "Tool: $TOOL_NAME"
echo "CVE ID: $CVE_ID"
echo "Software: $SOFTWARE"
echo "SIF file: $SIF_FILE"
echo "Runtime directory: $RUNTIME_DIR"
echo "=================================="

# Check if SIF file exists
if [ ! -f "$SIF_FILE" ]; then
    echo "ERROR: SIF file not found: $SIF_FILE"
    echo "Available SIF files:"
    ls -la "$SIF_DIR"
    exit 1
fi

# Check if runtime directory exists
if [ ! -d "$RUNTIME_DIR" ]; then
    echo "WARNING: Runtime directory not found: $RUNTIME_DIR"
    echo "Creating directory..."
    mkdir -p "$RUNTIME_DIR"
fi

# Load apptainer module
echo "Loading Apptainer module..."
module load apptainer

# Run interactive shell
echo "Starting interactive shell in container..."
echo "The host directory $RUNTIME_DIR is mounted at /$CVE_ID inside the container"
echo "Type 'exit' to leave the container."
echo ""

apptainer shell \
    --bind "$RUNTIME_DIR:/$CVE_ID" \
    "$SIF_FILE"

echo "Exited container debug shell."
