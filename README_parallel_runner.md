# Vul4C Framework Parallel Runner

This repository contains Python scripts to run the Vul4C vulnerability repair framework across multiple combinations of tools, software projects, and CVEs in parallel.

## Scripts Overview

### 1. `run_framework_parallel.py` - Main Parallel Runner
A comprehensive script that automatically discovers all available combinations and runs them in parallel with configurable concurrency.

### 2. `run_single.py` - Simple Single Runner  
A lightweight script for running individual combinations for testing purposes.

## Prerequisites

- Python 3.7+
- Docker (required by the Vul4C framework)
- All Vul4C framework dependencies installed

## Usage

### Running All Combinations in Parallel

```bash
# Run with default 4 parallel workers
python3 run_framework_parallel.py --max-parallel 4

# Run with 8 parallel workers
python3 run_framework_parallel.py --max-parallel 8

# Run only specific tools
python3 run_framework_parallel.py --max-parallel 4 --tools VulnFix ExtractFix

# Run only specific software projects
python3 run_framework_parallel.py --max-parallel 2 --software audiofile libxml2

# Combine tool and software filters
python3 run_framework_parallel.py --max-parallel 4 --tools VulnFix --software audiofile

# Dry run to see what would be executed
python3 run_framework_parallel.py --dry-run

# Save results to custom file
python3 run_framework_parallel.py --max-parallel 4 --output my_results.txt
```

### Running Individual Combinations

```bash
# Run a specific combination
python3 run_single.py VulnFix audiofile CVE-2017-6838

# Run with explicit paths
python3 run_single.py ExtractFix libxml2 CVE-2016-1838
```

### Advanced Examples

```bash
# Run only VulnFix tool on all available software/CVEs with 6 workers
python3 run_framework_parallel.py --max-parallel 6 --tools VulnFix

# Run multiple tools on specific software
python3 run_framework_parallel.py --max-parallel 4 \
    --tools VulnFix ExtractFix VRepair \
    --software audiofile jasper

# Test run on a subset before full execution
python3 run_framework_parallel.py --dry-run --tools VulnFix --software audiofile
```

## Available Tools

The framework supports the following repair tools:
- **VulnFix** - Automated vulnerability repair
- **ExtractFix** - Extract-based repair approach
- **Senx** - Syntax-based repair
- **VRepair** - Template-based repair
- **VulRepair** - Vulnerability-specific repair
- **VulMaster** - Master vulnerability repair
- **VQM** - Vulnerability Query Matching

## Available Software Projects

The framework includes vulnerabilities from various open-source projects:
- audiofile, bento4, binutils, elfutils
- graphicsmagick, imagemagick, imageworsener
- jasper, jhead, libarchive, libcroco
- libjpeg, libming, libsndfile, libtiff
- libxml2, libzip, ngiflib, openjpeg
- and more...

## Output and Results

### Console Output
The parallel runner provides real-time progress updates:
```
2025-09-21 23:43:58 - INFO - Found 596 combinations to process
2025-09-21 23:43:58 - INFO - Using 4 parallel workers
2025-09-21 23:43:58 - INFO - Starting VulnFix_audiofile_CVE-2017-6838
✓ Completed VulnFix_audiofile_CVE-2017-6838 in 45.2s
✗ Failed ExtractFix_jasper_CVE-2016-10248 in 30.1s (exit code: 1)
✓ Progress: 2/596 (0.3%) - Failed: 1
```

### Results Summary
After completion, a detailed summary is saved:
```
Vul4C Framework Execution Results
==================================================

Total combinations: 596
Successful: 234
Failed: 362
Success rate: 39.3%

Detailed Results:
------------------------------
✓ VulnFix_audiofile_CVE-2017-6838 (45.20s)
✗ ExtractFix_jasper_CVE-2016-10248 (30.10s)
   Error: Docker container failed to start...
```

### Log Files
- `framework_runner.log` - Detailed execution log
- `framework_results_YYYYMMDD_HHMMSS.txt` - Results summary

## Performance Considerations

### Parallelism Guidelines
- **2-4 workers**: Safe for most systems, good for initial testing
- **4-8 workers**: Recommended for modern multi-core systems
- **8+ workers**: Only for high-performance systems with adequate Docker resources

### Resource Requirements
- **CPU**: Each worker uses 1 CPU core intensively
- **Memory**: 2-4GB RAM per worker (Docker containers)
- **Disk**: Significant temporary storage for build artifacts
- **Network**: May download dependencies during builds

### Execution Time Estimates
- **Single combination**: 30 seconds to 10 minutes
- **All 596 combinations**: 
  - 4 workers: ~10-15 hours
  - 8 workers: ~5-8 hours
  - 16 workers: ~3-5 hours

## Troubleshooting

### Common Issues

1. **Docker Permission Errors**
   ```bash
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

2. **Out of Disk Space**
   ```bash
   # Clean up Docker
   docker system prune -a
   ```

3. **Memory Issues**
   ```bash
   # Reduce parallel workers
   python3 run_framework_parallel.py --max-parallel 2
   ```

4. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/SoK
   python3 run_framework_parallel.py
   ```

### Debugging Individual Failures

```bash
# Test a specific failing combination
python3 run_single.py VulnFix audiofile CVE-2017-6838

# Check the original framework directly
python3 Framework/vul4c.py --tool VulnFix --software audiofile --CVEID CVE-2017-6838
```

### Monitoring Progress

```bash
# Monitor in real-time
tail -f framework_runner.log

# Check system resources
htop
docker ps
df -h
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Vul4C Framework Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run subset of tests
      run: |
        python3 run_framework_parallel.py --max-parallel 2 \
          --tools VulnFix --software audiofile
```

### Batch Processing
```bash
#!/bin/bash
# Run different tool subsets on different machines
python3 run_framework_parallel.py --max-parallel 8 --tools VulnFix ExtractFix
python3 run_framework_parallel.py --max-parallel 8 --tools VRepair VulRepair  
python3 run_framework_parallel.py --max-parallel 8 --tools VulMaster VQM Senx
```

## Contributing

To add support for new tools or software:

1. Add tool configuration in `Framework/[ToolName]/`
2. Update tool import in `Framework/vul4c.py`
3. Test with single runner first:
   ```bash
   python3 run_single.py NewTool software CVE-XXXX-XXXX
   ```

## License

This project follows the same license as the original Vul4C framework.
