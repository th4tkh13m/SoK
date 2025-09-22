#!/usr/bin/env python3
"""
Parallel Framework Runner for Vul4C

This script runs the Vul4C framework across all combinations of tools, software projects, and CVEs
with configurable parallelism.

Usage:
    python3 run_framework_parallel.py --max-parallel 4
    python3 run_framework_parallel.py --max-parallel 8 --tools VulnFix ExtractFix
    python3 run_framework_parallel.py --max-parallel 2 --software audiofile libxml2
"""

import sys
import argparse
import subprocess
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional
from pathlib import Path


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('framework_runner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class FrameworkRunner:
    """Manages parallel execution of the Vul4C framework across multiple configurations."""
    
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.root_dir = Path(__file__).parent.absolute()
        self.framework_dir = self.root_dir / "Framework"
        self.vul4c_script = self.framework_dir / "vul4c.py"
        
        # Verify the script exists
        if not self.vul4c_script.exists():
            raise FileNotFoundError(f"vul4c.py not found at {self.vul4c_script}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools from the Framework directory."""
        tools = []
        for item in self.framework_dir.iterdir():
            if item.is_dir() and item.name not in ['tool', '__pycache__']:
                tools.append(item.name)
        return sorted(tools)
    
    def get_available_software(self, tool: str) -> List[str]:
        """Get list of available software projects for a given tool."""
        tool_dir = self.framework_dir / tool
        if not tool_dir.exists():
            return []
        
        software_list = []
        for item in tool_dir.iterdir():
            if item.is_dir():
                software_list.append(item.name)
        return sorted(software_list)
    
    def get_available_cves(self, tool: str, software: str) -> List[str]:
        """Get list of available CVEs for a given tool and software combination."""
        software_dir = self.framework_dir / tool / software
        if not software_dir.exists():
            return []
        
        cves = []
        for item in software_dir.iterdir():
            if item.is_dir() and item.name.startswith('CVE-'):
                cves.append(item.name)
        return sorted(cves)
    
    def get_all_combinations(self, 
                           tools: List[str] | None = None, 
                           software_list: List[str] | None = None) -> List[Tuple[str, str, str]]:
        """Generate all valid combinations of (tool, software, cve)."""
        if tools is None:
            tools = self.get_available_tools()
        
        combinations = []
        
        for tool in tools:
            available_software = self.get_available_software(tool)
            
            # Filter by requested software if specified
            if software_list is not None:
                available_software = [sw for sw in available_software if sw in software_list]
            
            for software in available_software:
                cves = self.get_available_cves(tool, software)
                for cve in cves:
                    combinations.append((tool, software, cve))
        
        return combinations
    
    def run_single_combination(self, tool: str, software: str, cve: str) -> dict:
        """Run the framework for a single combination of tool, software, and CVE."""
        start_time = time.time()
        combination_id = f"{tool}_{software}_{cve}"
        
        logger.info(f"Starting {combination_id}")
        
        try:
            # Build the command
            cmd = [
                sys.executable,
                str(self.vul4c_script),
                "--tool", tool,
                "--software", software,
                "--CVEID", cve
            ]
            
            # Run the command
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            result_data = {
                'tool': tool,
                'software': software,
                'cve': cve,
                'combination_id': combination_id,
                'success': success,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if success:
                logger.info(f"✓ Completed {combination_id} in {duration:.2f}s")
            else:
                logger.error(f"✗ Failed {combination_id} in {duration:.2f}s (exit code: {result.returncode})")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr[:500]}...")
            
            return result_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"✗ Timeout {combination_id} after 1 hour")
            return {
                'tool': tool,
                'software': software,
                'cve': cve,
                'combination_id': combination_id,
                'success': False,
                'duration': 3600,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Process timed out after 1 hour'
            }
        except Exception as e:
            logger.error(f"✗ Exception in {combination_id}: {str(e)}")
            return {
                'tool': tool,
                'software': software,
                'cve': cve,
                'combination_id': combination_id,
                'success': False,
                'duration': 0,
                'returncode': -2,
                'stdout': '',
                'stderr': f'Exception: {str(e)}'
            }
    
    def run_parallel(self, 
                    tools: List[str] | None = None, 
                    software_list: List[str] | None = None,
                    dry_run: bool = False) -> List[dict]:
        """Run the framework in parallel across all specified combinations."""
        
        combinations = self.get_all_combinations(tools, software_list)
        
        logger.info(f"Found {len(combinations)} combinations to process")
        logger.info(f"Using {self.max_parallel} parallel workers")
        
        if dry_run:
            logger.info("DRY RUN - Would execute the following combinations:")
            for i, (tool, software, cve) in enumerate(combinations, 1):
                logger.info(f"  {i:3d}. {tool} -> {software} -> {cve}")
            return []
        
        results = []
        completed = 0
        failed = 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            # Submit all jobs
            future_to_combination = {
                executor.submit(self.run_single_combination, tool, software, cve): (tool, software, cve)
                for tool, software, cve in combinations
            }
            
            # Process completed jobs
            for future in as_completed(future_to_combination):
                result = future.result()
                results.append(result)
                completed += 1
                
                if result['success']:
                    status = "✓"
                else:
                    status = "✗"
                    failed += 1
                
                progress = completed / len(combinations) * 100
                logger.info(f"{status} Progress: {completed}/{len(combinations)} ({progress:.1f}%) - "
                          f"Failed: {failed}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Summary
        successful = completed - failed
        logger.info("\n" + "="*60)
        logger.info("EXECUTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total combinations: {len(combinations)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {successful/len(combinations)*100:.1f}%")
        logger.info(f"Total time: {total_duration:.2f}s ({total_duration/60:.1f}m)")
        logger.info(f"Average time per combination: {total_duration/len(combinations):.2f}s")
        
        return results
    
    def save_results_summary(self, results: List[dict], output_file: str | None = None):
        """Save a summary of results to a file."""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"framework_results_{timestamp}.txt"
        
        with open(output_file, 'w') as f:
            f.write("Vul4C Framework Execution Results\n")
            f.write("="*50 + "\n\n")
            
            # Summary statistics
            total = len(results)
            successful = sum(1 for r in results if r['success'])
            failed = total - successful
            
            f.write(f"Total combinations: {total}\n")
            f.write(f"Successful: {successful}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success rate: {successful/total*100:.1f}%\n\n")
            
            # Detailed results
            f.write("Detailed Results:\n")
            f.write("-" * 30 + "\n")
            
            for result in sorted(results, key=lambda x: (x['tool'], x['software'], x['cve'])):
                status = "✓" if result['success'] else "✗"
                f.write(f"{status} {result['combination_id']} ({result['duration']:.2f}s)\n")
                if not result['success'] and result['stderr']:
                    f.write(f"   Error: {result['stderr'][:100]}...\n")
        
        logger.info(f"Results summary saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Vul4C framework in parallel across multiple configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --max-parallel 4
  %(prog)s --max-parallel 8 --tools VulnFix ExtractFix  
  %(prog)s --max-parallel 2 --software audiofile libxml2
  %(prog)s --dry-run
        """
    )
    
    parser.add_argument(
        '--max-parallel', 
        type=int, 
        default=4,
        help='Maximum number of parallel tasks (default: 4)'
    )
    
    parser.add_argument(
        '--tools',
        nargs='+',
        help='Specific tools to run (default: all available tools)'
    )
    
    parser.add_argument(
        '--software',
        nargs='+',
        help='Specific software projects to run (default: all available software)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without actually running'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for results summary'
    )
    
    args = parser.parse_args()
    
    try:
        runner = FrameworkRunner(max_parallel=args.max_parallel)
        
        # Show available options
        available_tools = runner.get_available_tools()
        logger.info(f"Available tools: {', '.join(available_tools)}")
        
        # Validate requested tools
        if args.tools:
            invalid_tools = [t for t in args.tools if t not in available_tools]
            if invalid_tools:
                logger.error(f"Invalid tools specified: {', '.join(invalid_tools)}")
                logger.error(f"Available tools: {', '.join(available_tools)}")
                sys.exit(1)
        
        # Run the framework
        results = runner.run_parallel(
            tools=args.tools,
            software_list=args.software,
            dry_run=args.dry_run
        )
        
        # Save results if not dry run
        if not args.dry_run and results:
            runner.save_results_summary(results, args.output)
        
    except KeyboardInterrupt:
        logger.info("\nExecution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
