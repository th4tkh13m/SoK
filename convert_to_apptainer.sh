#!/bin/bash

# Script to convert Docker images to Apptainer SIF files
# This script helps convert the required Docker images to SIF format for HPC use

set -e

SIF_DIR="/project/phan/kt477/RLVR-Vuln/Benchmarks/SoK/sif_images"
mkdir -p "$SIF_DIR"

# List of Docker images used by the framework
declare -a DOCKER_IMAGES=(
    "vul4c/vulnfix:1.0"
    "vul4c/extractfix:1.0"
    "vul4c/senx:1.0"
    "vul4c/vrepair:1.0"
    "vul4c/vulrepair:2.0"
    "vul4c/vulmaster:1.0"
    "vul4c/vqm:1.0"
    "vul4c/test:1.0"
)

echo "Converting Docker images to Apptainer SIF files..."
echo "SIF files will be stored in: $SIF_DIR"

for docker_image in "${DOCKER_IMAGES[@]}"; do
    # Convert image name to SIF filename
    sif_name=$(echo "$docker_image" | sed 's|/|_|g' | sed 's|:|_|g')
    sif_file="$SIF_DIR/${sif_name}.sif"
    
    echo "Converting $docker_image -> ${sif_name}.sif"
    
    if [ -f "$sif_file" ]; then
        echo "  SIF file already exists: $sif_file"
    else
        echo "  Building SIF file from Docker image..."
        apptainer build "$sif_file" "docker://$docker_image"
        echo "  Successfully created: $sif_file"
    fi
done

echo "Conversion complete!"
echo ""
echo "To use Apptainer backend, set the environment variable:"
echo "export VUL4C_CONTAINER_BACKEND=apptainer"
echo ""
echo "To use Docker backend (default), set:"
echo "export VUL4C_CONTAINER_BACKEND=docker"
