# Apptainer Migration for Vul4C

This document describes the migration from Docker to Apptainer for running the Vul4C vulnerability repair benchmark on HPC systems.

## Overview

The codebase has been modified to support both Docker and Apptainer backends through a configurable abstraction layer. This allows the framework to run on HPC systems that don't support Docker but have Apptainer (formerly Singularity) available.

## Architecture Changes

### 1. Container Abstraction Layer

- **`ContainerBase`**: Abstract base class defining the interface for container operations
- **`DockerContainer`**: Original Docker implementation (now inherits from `ContainerBase`)
- **`ApptainerContainer`**: New Apptainer implementation
- **`container_factory.py`**: Factory system to choose between Docker and Apptainer backends

### 2. Configuration

The container backend is controlled by the `VUL4C_CONTAINER_BACKEND` environment variable:

```bash
# Use Apptainer (default)
export VUL4C_CONTAINER_BACKEND=apptainer

# Use Docker
export VUL4C_CONTAINER_BACKEND=docker
```

### 3. Image Management

- **Docker**: Uses standard Docker images from the `vul4c` repository
- **Apptainer**: Uses `.sif` files stored in the `sif_images/` directory

## Setup Instructions

### Step 1: Convert Docker Images to SIF Files

Run the provided conversion script:

```bash
./convert_to_apptainer.sh
```

This script will:
- Create SIF files from the required Docker images
- Store them in `sif_images/` directory
- Use the naming convention: `{repository}_{tag}.sif`

### Step 2: Set Environment Variable

```bash
export VUL4C_CONTAINER_BACKEND=apptainer
```

### Step 3: Run the Framework

Use the framework as normal:

```bash
python3 Framework/vul4c.py --tool "VulnFix" --software "jasper" --CVEID "CVE-2016-10248"
```

## Key Differences Between Docker and Apptainer

### File Access

- **Docker**: Uses volume mounts and `docker cp` for file transfer
- **Apptainer**: Uses bind mounts, files are directly accessible

### Command Execution

- **Docker**: `docker exec` with persistent containers
- **Apptainer**: `apptainer exec` with SIF files (stateless)

### GPU Support

- **Docker**: `--gpus all` and device requests
- **Apptainer**: `--nv` flag for NVIDIA GPU support

## Required SIF Files

The following SIF files need to be available in `sif_images/`:

- `vul4c_vulnfix_1.0.sif`
- `vul4c_extractfix_1.0.sif`
- `vul4c_senx_1.0.sif`
- `vul4c_vrepair_1.0.sif`
- `vul4c_vulrepair_2.0.sif`
- `vul4c_vulmaster_1.0.sif`
- `vul4c_vqm_1.0.sif`
- `vul4c_test_1.0.sif`

## Troubleshooting

### SIF File Not Found

```
FileNotFoundError: Apptainer SIF file not found: /path/to/sif_images/vul4c_tool_1.0.sif
```

**Solution**: Ensure all required SIF files are present in the `sif_images/` directory.

### Permission Issues

If you encounter permission issues, ensure:
- SIF files are readable
- Bind mount directories have appropriate permissions
- Apptainer is properly configured on your HPC system

### GPU Access

For GPU-enabled tools, ensure:
- NVIDIA container toolkit is available
- Apptainer is configured with GPU support
- Use `--nv` flag (automatically handled by the framework)

## Migration Summary

The migration maintains full backward compatibility with Docker while adding Apptainer support. The key changes:

1. **Tool Classes**: All tool classes now inherit from `ContainerClass` (factory-provided)
2. **File Operations**: Adapted to handle both Docker volumes and Apptainer bind mounts
3. **Image References**: Automatic conversion from Docker image names to SIF file paths
4. **Environment Control**: Simple environment variable to switch backends

## Testing

To test the migration:

1. Ensure a SIF file exists (e.g., `vul4c_vulnfix_1.0.sif`)
2. Set `VUL4C_CONTAINER_BACKEND=apptainer`
3. Run a simple test case
4. Verify results are generated correctly

The framework will log which container backend is being used during initialization.
