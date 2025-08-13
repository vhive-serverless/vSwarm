#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import json
import time
import re
from pathlib import Path
import pandas as pd
import glob
import shutil
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# CONFIGURATION - Edit these values to customize your tests
# =============================================================================

RPS_VALUES = [20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500]
# Duration for all tests (in seconds)
TEST_DURATION = 60
# Number of iterations per RPS level
ITERATIONS_PER_RPS = 3

class ComprehensiveTestRunner:
    def __init__(self, title, invoker_dir="../tools/invoker", service_name=None, namespace="default"):
        self.title = title
        self.rps_values = RPS_VALUES
        self.durations = [TEST_DURATION] * len(RPS_VALUES)  # Same duration for all tests
        self.iterations_per_rps = ITERATIONS_PER_RPS
        self.invoker_dir = invoker_dir
        self.results_dir = f"results_{title}"
        self.stats_file = os.path.join(self.results_dir, f"{title}_statistics.csv")
        self.service_name = service_name
        self.namespace = namespace
        self.monitoring_running = False
        self.monitoring_file = None
        
        # Dynamic load threshold based on available CPUs (nproc)
        try:
            available_cpus = os.cpu_count() or 1
        except Exception:
            available_cpus = 1
        self.load_threshold = max(1.0, 0.8 * available_cpus)
        
        # Create a test-specific directory inside invoker dir for raw files
        self.raw_files_dir = os.path.join(self.invoker_dir, f"raw_files_{title}")
        os.makedirs(self.raw_files_dir, exist_ok=True)
        
        print(f"=== Comprehensive Test Runner ===")
        print(f"Test Title: {title}")
        print(f"RPS Values: {self.rps_values}")
        print(f"Duration: {TEST_DURATION} seconds (all tests)")
        print(f"Iterations per RPS: {self.iterations_per_rps}")
        print(f"Total Tests: {len(self.rps_values) * self.iterations_per_rps}")
        print(f"Results Directory: {self.results_dir}")
        print(f"Statistics File: {self.stats_file}")
        print(f"Raw Files Directory: {self.raw_files_dir}")
        if service_name:
            print(f"Pod Monitoring: {service_name} (namespace: {namespace})")
        print("=" * 50)
    
    def check_prerequisites(self):
        """Check if all required tools are available."""
        print("Checking prerequisites...")
        
        # Check if invoker exists
        invoker_path = os.path.join(self.invoker_dir, "invoker")
        if not os.path.exists(invoker_path):
            print(f" Invoker not found at {invoker_path}")
            print("Building invoker...")
            self.build_invoker()
        else:
            print(" Invoker found")
        
        # Check if endpoints.json exists
        endpoints_path = os.path.join(self.invoker_dir, "endpoints.json")
        if not os.path.exists(endpoints_path):
            print(f" endpoints.json not found at {endpoints_path}")
            return False
        else:
            print(" endpoints.json found")
        
        # Check if matplotlib and seaborn are available
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            print(" matplotlib and seaborn found")
        except ImportError as e:
            print(f" Required visualization libraries not found: {e}")
            print("Install with: pip install matplotlib seaborn")
            return False
        
        return True
    
    def build_invoker(self):
        """Build the invoker binary."""
        try:
            subprocess.run(["make", "invoker"], cwd=self.invoker_dir, check=True)
            print(" Invoker built successfully")
        except subprocess.CalledProcessError as e:
            print(f" Failed to build invoker: {e}")
            sys.exit(1)
    
    def get_latency_files(self):
        """Get all latency files in the invoker directory."""
        files = glob.glob(os.path.join(self.invoker_dir, "target_rps*_actual_rps*_lat.csv"))
        rps_files = {}
        for f in files:
            filename = os.path.basename(f)
            match = re.search(r'target_rps(\d+\.?\d*)_actual_rps(\d+\.?\d*)_lat\.csv', filename)
            if match:
                target_rps = float(match.group(1))
                if target_rps not in rps_files:
                    rps_files[target_rps] = []
                rps_files[target_rps].append({
                    'path': f,
                    'filename': filename,
                    'mtime': os.path.getmtime(f)
                })
        return rps_files

    def run_invoker_test(self, rps, duration, iteration=1):
        """Run a single invoker test."""
        print(f"\n--- Running Test: RPS={rps}, Duration={duration}s, Iteration={iteration}/{self.iterations_per_rps} ---")
        
        # Build the invoker command
        cmd = [
            "./invoker",
            "-time", str(duration),
            "-rps", str(rps),
            "-port", "80"
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        # Run the invoker from the invoker directory
        try:
            result = subprocess.run(cmd, cwd=self.invoker_dir, capture_output=True, text=True, check=True)
            print(" Test completed successfully")
            
            # Find the newly generated latency file
            latency_files = glob.glob(os.path.join(self.invoker_dir, "rps*_lat.csv"))
            if latency_files:
                # Get the most recent file
                latest_file = max(latency_files, key=os.path.getctime)
                
                # Create a new filename with target RPS and iteration at the beginning
                original_name = os.path.basename(latest_file)
                new_name = f"target_rps{rps:.2f}_iter{iteration:02d}_{original_name}"
                new_path = os.path.join(self.results_dir, new_name)
                
                # Copy file to results directory
                os.makedirs(self.results_dir, exist_ok=True)
                try:
                    subprocess.run(["cp", latest_file, new_path], check=True)
                    print(f" Copied to: {new_name}")
                    
                    # Clean up original file
                    os.remove(latest_file)
                    print(f" Cleaned up: {original_name}")
                except (subprocess.CalledProcessError, OSError) as e:
                    print(f" Failed to handle file {original_name}: {e}")
            else:
                print("  No latency file was generated")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f" Test failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def manage_raw_files(self):
        """Move raw latency files to test directory."""
        print("\n--- Managing Raw Latency Files ---")
        
        # Move any existing latency files to the test directory
        existing_files = glob.glob(os.path.join(self.invoker_dir, "target_rps*_actual_rps*_lat.csv"))
        if existing_files:
            for file in existing_files:
                filename = os.path.basename(file)
                dest = os.path.join(self.raw_files_dir, filename)
                try:
                    shutil.move(file, dest)
                    print(f" Moved to test directory: {filename}")
                except Exception as e:
                    print(f" Failed to move {filename}: {e}")
            print(f" Total files moved: {len(existing_files)}")
        else:
            print("No latency files found to move.")

    def find_latency_files_for_rps(self, rps):
        """Find all latency files for a given RPS value (all iterations)."""
        # Look for files with exact matching target RPS
        pattern = f"target_rps{rps:.2f}_iter*_rps*_lat.csv"
        files = glob.glob(os.path.join(self.results_dir, pattern))
        
        if not files:
            print(f" No latency files found for target RPS {rps}")
            return []
        
        # Sort files by iteration number
        files.sort(key=lambda x: os.path.basename(x))
        print(f" Found {len(files)} latency files for RPS {rps}")
        for f in files:
            print(f"   - {os.path.basename(f)}")
        return files
    
    def copy_latency_files(self):
        """Copy latency files to results directory."""
        print(f"\n--- Finding Latency Files in {self.results_dir} ---")
        
        all_files = []
        rps_files_map = {}
        
        # Find all latency files in results directory
        for rps in self.rps_values:
            pattern = f"target_rps{rps:.2f}_iter*_rps*_lat.csv"
            files = glob.glob(os.path.join(self.results_dir, pattern))
            
            if files:
                # Sort files by iteration number
                files.sort(key=lambda x: os.path.basename(x))
                all_files.extend(files)
                rps_files_map[rps] = files
                print(f" Found {len(files)} files for RPS {rps}")
                for f in files:
                    print(f"   - {os.path.basename(f)}")
            else:
                print(f" No latency files found for target RPS {rps}")
        
        if not all_files:
            print(" No latency files found")
        else:
            print(f" Total files found: {len(all_files)} out of {len(self.rps_values) * self.iterations_per_rps} expected files")
        
        return all_files, rps_files_map
    
    def map_rps_to_latency_files(self, latency_files):
        """Map RPS values to their corresponding latency files."""
        rps_to_file = {}
        
        for rps in self.rps_values:
            # Find the latency file that corresponds to this RPS
            for latency_file in latency_files:
                filename = os.path.basename(latency_file)
                try:
                    match = re.search(r'target_rps(\d+\.?\d*)_actual_rps(\d+\.?\d*)_lat\.csv', filename)
                    if match:
                        file_target_rps = float(match.group(1))
                        file_actual_rps = float(match.group(2))
                        # Check if this file is close to our target RPS
                        if abs(file_target_rps - rps) <= 5 or abs(file_actual_rps - rps) <= 5:  # Accept files within 5 RPS difference
                            rps_to_file[rps] = latency_file
                            break
                except (ValueError, AttributeError):
                    continue
        
        return rps_to_file
    
    def generate_statistics(self, latency_files, rps_files_map):
        """Generate comprehensive statistics with averaging across iterations."""
        print(f"\n--- Generating Statistics (Averaging {self.iterations_per_rps} iterations per RPS) ---")
        
        all_stats = []
        all_data = {}  # Store all latency data for visualization
        
        # Process each RPS level and average across iterations
        for rps in self.rps_values:
            if rps not in rps_files_map:
                print(f" No files found for RPS {rps}")
                continue
                
            files_for_rps = rps_files_map[rps]
            print(f"\n--- Analyzing RPS {rps} ({len(files_for_rps)} iterations) ---")
            
            # Collect statistics for all iterations
            iteration_stats = []
            
            for i, latency_file in enumerate(files_for_rps, 1):
                print(f"  Iteration {i}/{len(files_for_rps)}: {os.path.basename(latency_file)}")
                
                # Load and analyze latency data using integrated function
                latency_data = self.load_latency_data(latency_file)
                if latency_data is not None:
                    filename = os.path.basename(latency_file)
                    stats = self.calculate_statistics(latency_data, TEST_DURATION, filename)
                    if stats:
                        iteration_stats.append(stats)
                        # Store data for visualization
                        all_data[filename] = latency_data
                        print(f"     Statistics generated")
                    else:
                        print(f"     Failed to calculate statistics for {latency_file}")
                else:
                    print(f"     Failed to load data from {latency_file}")
            
            # Average statistics across iterations
            if iteration_stats:
                averaged_stats = self.average_statistics(iteration_stats, rps)
                all_stats.append(averaged_stats)
                print(f" Averaged statistics generated for RPS {rps}")
            else:
                print(f" No valid statistics for RPS {rps}")
        
        # Save statistics to CSV
        if all_stats:
            self.save_statistics_csv(all_stats)
        
        # Generate detailed analysis CSV
        print(f"\n--- Generating Detailed Analysis CSV ---")
        analysis_csv_path = os.path.join(self.results_dir, f"{self.title}_detailed_analysis.csv")
        
        detailed_stats = []
        for filename, data in all_data.items():
            if data is not None:
                stats = self.calculate_statistics(data, TEST_DURATION, filename)
                if stats:
                    stats['filename'] = filename
                    detailed_stats.append(stats)
        
        if detailed_stats:
            df = pd.DataFrame(detailed_stats)
            df.to_csv(analysis_csv_path, index=False)
            print(f" Detailed analysis CSV saved to: {analysis_csv_path}")
        
        # Store all_data for visualization
        self.all_data = all_data
        self.all_stats_dict = {stats.get('rps', 0): stats for stats in all_stats}
        
        return all_stats
    
    def parse_latency_with_units(self, latency_str):
        """Parse latency string with units and convert to milliseconds."""
        latency_str = latency_str.strip()
        
        # Handle different time units and convert to milliseconds
        if 'μs' in latency_str:
            # Microseconds to milliseconds
            value = float(latency_str.replace('μs', ''))
            return value / 1000.0
        elif 'ms' in latency_str:
            # Already in milliseconds
            return float(latency_str.replace('ms', ''))
        elif 's' in latency_str and 'ms' not in latency_str:
            # Seconds to milliseconds (but not catching 'ms' again)
            value = float(latency_str.replace('s', ''))
            return value * 1000.0
        else:
            # Assume milliseconds if no unit specified
            try:
                return float(latency_str)
            except ValueError:
                print(f"  Warning: Could not parse latency value: {latency_str}")
                return 0.0

    def parse_analysis_output(self, output, rps, duration):
        """Parse the analysis script output to extract statistics."""
        lines = output.strip().split('\n')
        
        # Find the statistics section
        stats = {
            'rps': rps,
            'duration': duration,
            'test_title': self.title
        }
        
        for line in lines:
            line = line.strip()
            if 'Data points:' in line:
                stats['total_requests'] = int(line.split(':')[1].replace(',', ''))
            elif 'Minimum latency:' in line:
                latency_str = line.split(':')[1].strip()
                stats['min_latency_us'] = self.parse_latency_with_units(latency_str)
            elif 'Maximum latency:' in line:
                latency_str = line.split(':')[1].strip()
                stats['max_latency_us'] = self.parse_latency_with_units(latency_str)
            elif 'Average latency:' in line:
                latency_str = line.split(':')[1].strip()
                stats['avg_latency_us'] = self.parse_latency_with_units(latency_str)
            elif 'Median latency:' in line:
                latency_str = line.split(':')[1].strip()
                stats['median_latency_us'] = self.parse_latency_with_units(latency_str)
            elif '95th percentile:' in line:
                latency_str = line.split(':')[1].strip()
                stats['p95_latency_us'] = self.parse_latency_with_units(latency_str)
            elif '99th percentile:' in line:
                latency_str = line.split(':')[1].strip()
                stats['p99_latency_us'] = self.parse_latency_with_units(latency_str)
            elif 'Throughput:' in line:
                throughput_str = line.split(':')[1].strip()
                if 'RPS' in throughput_str:
                    stats['throughput_rps'] = float(throughput_str.replace(' RPS', ''))
                else:
                    stats['throughput_rps'] = 0.0
        
        return stats
    
    def average_statistics(self, iteration_stats, rps):
        """Average statistics across multiple iterations."""
        if not iteration_stats:
            return None
        
        # Initialize averaged stats with the first iteration's structure
        averaged_stats = {
            'rps': rps,
            'duration': TEST_DURATION,
            'test_title': self.title,
            'iterations': len(iteration_stats)
        }
        
        # Calculate averages for numeric fields (using integrated stats keys)
        numeric_fields = [
            'total_requests', 'min', 'max', 'average',
            'median', 'p95', 'p99', 'throughput_rps'
        ]
        
        for field in numeric_fields:
            values = [stats.get(field, 0) for stats in iteration_stats if field in stats]
            if values:
                averaged_stats[f'avg_{field}'] = sum(values) / len(values)
                averaged_stats[f'std_{field}'] = pd.Series(values).std()
                averaged_stats[f'min_{field}'] = min(values)
                averaged_stats[f'max_{field}'] = max(values)
        
        # For backward compatibility, also include the main fields
        for field in numeric_fields:
            if f'avg_{field}' in averaged_stats:
                averaged_stats[field] = averaged_stats[f'avg_{field}']
        
        return averaged_stats
    
    def save_statistics_csv(self, all_stats):
        """Save statistics to CSV file."""
        df = pd.DataFrame(all_stats)
        df.to_csv(self.stats_file, index=False)
        print(f" Statistics saved to: {self.stats_file}")
        
        # Print summary
        print("\n=== Statistics Summary (Averaged Across Iterations) ===")
        print("Note: Only showing statistics for RPS values where latency files were found")
        print("-" * 120)
        
        # Create a more readable summary
        summary_df = df.copy()
        # Round numeric columns to 2 decimal places
        numeric_cols = summary_df.select_dtypes(include=['float64']).columns
        summary_df[numeric_cols] = summary_df[numeric_cols].round(2)
        
        # Reorder columns for better readability
        desired_order = ['rps', 'iterations', 'throughput_rps', 'std_throughput_rps', 
                        'average', 'p95', 'p99', 'total_requests']
        other_cols = [col for col in summary_df.columns if col not in desired_order]
        final_order = desired_order + other_cols
        summary_df = summary_df[final_order]
        
        print(summary_df.to_string(index=False))
        print("-" * 120)
        
        # Print analysis of missing RPS values
        missing_rps = set(self.rps_values) - set(df['rps'].values)
        if missing_rps:
            print("\nMissing RPS values (no statistics generated):")
            for rps in sorted(missing_rps):
                print(f"- RPS {rps}")
        
        # Print consistency analysis
        print("\n=== Consistency Analysis ===")
        high_variance_rps = []
        for _, row in df.iterrows():
            if 'std_throughput_rps' in row and row['std_throughput_rps'] > 5.0:
                high_variance_rps.append((row['rps'], row['std_throughput_rps']))
        
        if high_variance_rps:
            print("  High variance detected (>5 RPS std dev):")
            for rps, std in high_variance_rps:
                print(f"   - RPS {rps}: ±{std:.1f} RPS")
        else:
            print(" All RPS levels show consistent results")
        print()
    
    def create_visualizations(self, latency_files):
        """Create comprehensive visualizations using integrated functions."""
        print(f"\n--- Creating Visualizations ---")
        
        charts_dir = os.path.join(self.results_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # Use the stored data from generate_statistics
        if not hasattr(self, 'all_data') or not hasattr(self, 'all_stats_dict'):
            print(" No data available for visualization")
            return False
        
        all_data = self.all_data
        all_stats = self.all_stats_dict
        
        # Create comprehensive time series chart
        if self.service_name:
            monitoring_file = os.path.join(self.results_dir, f"{self.title}_pod_monitoring.csv")
            if os.path.exists(monitoring_file):
                resource_data = self.load_resource_data(monitoring_file)
                if resource_data is not None:
                    self.create_comprehensive_time_series(all_data, all_stats, resource_data)
        
        # Create latency vs throughput chart
        self.create_latency_vs_throughput_chart(all_stats)
        
        # Create percentile charts
        self.create_percentile_charts(all_stats)
        
        print(f" Visualizations created in: {charts_dir}")
        return True
    
    def create_resource_evolution_charts(self, latency_files):
        """Create the new resource evolution charts that show changes throughout all requests."""
        if not self.service_name:
            return False
            
        monitoring_file = os.path.join(self.results_dir, f"{self.title}_pod_monitoring.csv")
        if not os.path.exists(monitoring_file):
            print("  No pod monitoring data found for resource evolution charts")
            return False
            
        print(f"\n--- Creating Resource Evolution Charts ---")
        
        try:
            # Import visualization functions
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from visualize_latency_enhanced import (
                load_latency_data, 
                load_resource_data, 
                calculate_statistics,
                create_resource_evolution_chart,
                create_resource_vs_latency_correlation
            )
            
            # Load the comprehensive resource data
            full_resource_data = load_resource_data(monitoring_file)
            if full_resource_data is None:
                print(" Failed to load resource monitoring data")
                return False
            
            # Load all latency data and calculate statistics
            all_stats = {}
            all_resource_data = {}
            
            for latency_file in latency_files:
                base_name = os.path.splitext(os.path.basename(latency_file))[0]
                
                # Load latency data
                latency_data = load_latency_data(latency_file)
                if latency_data is not None:
                    filename = os.path.basename(latency_file)
                    all_stats[base_name] = calculate_statistics(latency_data, filename=filename)
                    # Use the full resource dataset for each phase
                    all_resource_data[base_name] = full_resource_data
            
            if not all_stats:
                print(" No valid latency data found for resource evolution")
                return False
            
            # Create charts directory
            charts_dir = os.path.join(self.results_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            # Generate resource evolution charts
            evolution_path = os.path.join(charts_dir, "resource_evolution_comprehensive.png")
            create_resource_evolution_chart(all_resource_data, all_stats, evolution_path)
            
            correlation_path = os.path.join(charts_dir, "resource_vs_latency_correlation.png")
            create_resource_vs_latency_correlation(all_resource_data, all_stats, correlation_path)
            
            # Show summary
            rps_values = [stats.get('target_rps', 0) for stats in all_stats.values() if stats]
            rps_values.sort()
            
            print(f" Resource evolution charts created:")
            print(f"    Resource Evolution: resource_evolution_comprehensive.png")
            print(f"    Resource vs Latency Correlation: resource_vs_latency_correlation.png")
            print(f"    Covering {len(all_stats)} test phases ({min(rps_values):.1f} - {max(rps_values):.1f} RPS)")
            print(f"    {len(full_resource_data)} resource monitoring points")
            
            return True
            
        except Exception as e:
            print(f" Failed to create resource evolution charts: {e}")
            return False

    def archive_existing_files(self):
        """Archive existing latency files from previous runs."""
        print("\n--- Archiving Previous Test Files ---")
        
        # Find all existing latency files
        existing_files = glob.glob(os.path.join(self.invoker_dir, "target_rps*_actual_rps*_lat.csv"))
        if not existing_files:
            print("No previous test files found.")
            return
        
        # Create timestamped archive folder
        archive_timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_folder = os.path.join(self.archive_dir, f"archived_{archive_timestamp}")
        os.makedirs(archive_folder, exist_ok=True)
        
        # Move files to archive
        for file in existing_files:
            filename = os.path.basename(file)
            dest = os.path.join(archive_folder, filename)
            try:
                shutil.move(file, dest)
                print(f" Archived: {filename}")
            except Exception as e:
                print(f" Failed to archive {filename}: {e}")
        
        print(f" Files archived to: {archive_folder}")
        print(f" Total files archived: {len(existing_files)}")

    def start_monitoring(self):
        """Start pod monitoring in background."""
        if not self.service_name:
            return False
        
        print(f"\n--- Starting Pod Monitoring ---")
        
        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.monitoring_file = os.path.join(self.results_dir, f"{self.title}_pod_monitoring.csv")
        self.monitoring_running = True
        
        # Start monitoring in a separate thread
        import threading
        self.monitoring_thread = threading.Thread(target=self._monitor_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print(f" Pod monitoring started")
        print(f" Monitoring data will be saved to: {self.monitoring_file}")
        time.sleep(2)  # Give monitoring time to start
        
        return True
    
    def _monitor_resources(self):
        """Internal method to monitor Kubernetes pod resources."""
        import time
        from datetime import datetime
        
        # Create monitoring file with headers
        with open(self.monitoring_file, 'w') as f:
            f.write("timestamp,pod_count,cpu_usage_millicores,memory_usage_mib\n")
        
        # Determine a working label selector for this Knative service (once)
        self.label_selector = None
        selector_candidates = [
            f"serving.knative.dev/service={self.service_name}",
            f"app={self.service_name}",
            f"serving.knative.dev/configuration={self.service_name}"
        ]
        for sel in selector_candidates:
            probe = subprocess.run([
                'kubectl', 'get', 'pods', '-n', self.namespace,
                '-l', sel, '--no-headers'
            ], capture_output=True, text=True)
            if probe.returncode == 0 and probe.stdout.strip():
                self.label_selector = sel
                break
        if not self.label_selector:
            # Fall back to the most probable Knative label
            self.label_selector = selector_candidates[0]
        
        while self.monitoring_running:
            try:
                # Get current timestamp
                timestamp = datetime.now().isoformat()
                
                # Get pod list for the selector
                result = subprocess.run([
                    'kubectl', 'get', 'pods', '-n', self.namespace,
                    '-l', self.label_selector, '--no-headers'
                ], capture_output=True, text=True)
                
                pod_count = 0
                if result.returncode == 0:
                    pod_lines = [ln for ln in result.stdout.strip().split('\n') if ln.strip()]
                    pod_count = len(pod_lines)
                
                # Get CPU and memory usage
                cpu_millicores = 0
                memory_mib = 0
                
                if pod_count > 0:
                    # Get resource usage for pods (requires metrics-server)
                    result = subprocess.run([
                        'kubectl', 'top', 'pods', '-n', self.namespace,
                        '-l', self.label_selector
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        # Some kubectl versions include a header line; detect and skip if present
                        if lines and ('CPU' in lines[0] or 'MEMORY' in lines[0] or 'NAME' in lines[0]):
                            lines = lines[1:]
                        total_cpu_millicores = 0
                        total_memory_mib = 0
                        
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 3:
                                    # Parse CPU (e.g., "100m" -> 100 millicores)
                                    cpu_str = parts[1]
                                    if cpu_str.endswith('m'):
                                        cpu_val = int(cpu_str[:-1])
                                    else:
                                        # e.g., "0" or cores; convert to millicores
                                        cpu_val = int(float(cpu_str) * 1000)
                                    
                                    # Parse memory (e.g., "50Mi" -> 50 MiB, "1Gi" -> 1024 MiB)
                                    memory_str = parts[2]
                                    if memory_str.endswith('Mi'):
                                        mem_val = int(memory_str[:-2])
                                    elif memory_str.endswith('Gi'):
                                        mem_val = int(float(memory_str[:-2]) * 1024)
                                    else:
                                        # Fallback: try to parse as MiB-equivalent
                                        mem_val = int(float(memory_str))
                                    
                                    total_cpu_millicores += cpu_val
                                    total_memory_mib += mem_val
                        
                        cpu_millicores = total_cpu_millicores
                        memory_mib = total_memory_mib
                
                # Write data to file
                with open(self.monitoring_file, 'a') as f:
                    f.write(f"{timestamp},{pod_count},{cpu_millicores},{memory_mib}\n")
                
                # Wait for next interval
                time.sleep(2)
                
            except Exception as e:
                print(f"  Monitoring error: {e}")
                time.sleep(2)

    def stop_monitoring(self):
        """Stop pod monitoring process."""
        if hasattr(self, 'monitoring_running') and self.monitoring_running:
            print(f"\n--- Stopping Pod Monitoring ---")
            try:
                # Stop the monitoring thread
                self.monitoring_running = False
                print(" Waiting for monitoring to save final data...")
                time.sleep(3)  # Give thread time to finish
                
                print(" Pod monitoring stopped")
                
                # Verify monitoring file was created
                if hasattr(self, 'monitoring_file') and os.path.exists(self.monitoring_file):
                    print(f" Monitoring data saved: {self.monitoring_file}")
                else:
                    print(f"  Warning: Monitoring file not found")
                    
            except Exception as e:
                print(f" Error stopping monitoring: {e}")
            finally:
                self.monitoring_running = False

    def convert_monitoring_data(self, monitoring_file):
        """Convert monitoring data to format expected by visualizer."""
        try:
            converted_file = monitoring_file.replace('.csv', '_converted.csv')
            
            # Read our monitoring data
            df = pd.read_csv(monitoring_file)
            
            # Create new dataframe with expected format
            converted_df = pd.DataFrame()
            converted_df['timestamp'] = df['timestamp']
            converted_df['pod_count'] = df['pod_count']
            
            # Convert CPU from millicores to approximate percentage
            # Assuming 1000 millicores = 100% of 1 CPU core
            converted_df['cpu_percent'] = (df['cpu_usage_millicores'] / 1000) * 100
            
            # Convert memory from MiB to approximate percentage 
            # Assuming 1024 MiB = 100% (rough approximation)
            converted_df['memory_percent'] = (df['memory_usage_mib'] / 1024) * 100
            
            # Save converted data
            converted_df.to_csv(converted_file, index=False)
            print(f" Converted monitoring data for visualizer: {converted_file}")
            
            return converted_file
            
        except Exception as e:
            print(f" Failed to convert monitoring data: {e}")
            return None

    def run_complete_pipeline(self, skip_tests=False):
        """Run the complete test pipeline with optional pod monitoring."""
        print("Starting comprehensive test pipeline...")
        
        # Step 1: Move any existing files to test directory
        self.manage_raw_files()
        
        # Step 2: Check prerequisites
        if not self.check_prerequisites():
            print(" Prerequisites check failed")
            return False
        
        # Step 3: Start pod monitoring if service specified
        monitoring_started = False
        if self.service_name and not skip_tests:
            monitoring_started = self.start_monitoring()
        
        try:
            if not skip_tests:
                # Step 4: Run all invoker tests with iterations
                print(f"\n--- Running {len(self.rps_values) * self.iterations_per_rps} Invoker Tests ---")
                for rps, duration in zip(self.rps_values, self.durations):
                    print(f"\n{'='*50}")
                    print(f"Testing RPS {rps} ({self.iterations_per_rps} iterations)")
                    print(f"{'='*50}")
                    
                    for iteration in range(1, self.iterations_per_rps + 1):
                        if not self.run_invoker_test(rps, duration, iteration):
                            print(f" Test failed for RPS {rps}, iteration {iteration}")
                            return False
                        time.sleep(2)  # Small delay between iterations
                    
                    print(f" Completed all {self.iterations_per_rps} iterations for RPS {rps}")
                    time.sleep(5)  # Longer delay between RPS levels
            else:
                print("\n--- Skipping invoker tests, using existing files ---")
        finally:
            # Always stop monitoring if it was started
            if monitoring_started:
                self.stop_monitoring()
        
        # Step 5: Copy latency files
        latency_files, rps_files_map = self.copy_latency_files()
        if not latency_files:
            print(" No latency files found")
            return False
        
        # Step 6: Generate statistics
        stats = self.generate_statistics(latency_files, rps_files_map)
        if not stats:
            print(" Failed to generate statistics")
            return False
        
        # Step 7: Create visualizations
        if latency_files:  # Only try to create visualizations if we have files
            if not self.create_visualizations(latency_files):
                print(" Failed to create visualizations")
                # Don't return False here, as the statistics are still useful
            
            # Step 7b: Create resource evolution charts (NEW!)
            if self.service_name:
                self.create_resource_evolution_charts(latency_files)
        else:
            print("  No latency files available for visualizations")
        
        print(f"\n Pipeline completed!")
        print(f" Statistics: {self.stats_file}")
        print(f" Results: {self.results_dir}")
        if latency_files:
            print(f" Charts: {self.results_dir}/charts")
            if self.service_name:
                print(f" Resource Evolution Charts: {self.results_dir}/charts/resource_evolution_comprehensive.png")
                print(f" Resource vs Latency Correlation: {self.results_dir}/charts/resource_vs_latency_correlation.png")
        else:
            print(f"  No charts generated (no latency files available)")
        
        if self.service_name:
            monitoring_file = os.path.join(self.results_dir, f"{self.title}_pod_monitoring.csv")
            print(f" Pod Monitoring: {monitoring_file}")
        
        # System health check after test completion
        print(f"\n{'='*60}")
        print(f" POST-TEST SYSTEM HEALTH CHECK")
        print(f"{'='*60}")
        
        system_healthy = self.check_system_health_after_test()
        
        if system_healthy:
            print(f"\n SYSTEM HEALTHY - Safe to continue with next test")
            print(f" You can proceed to your next configuration/runtime test")
        else:
            print(f"\n  SYSTEM ISSUES DETECTED - Consider waiting before next test")
            print(f" Recommended actions:")
            print(f"   - Wait 2-3 minutes for system to stabilize")
            print(f"   - Run: ./check_system_state.sh")
            print(f"   - If udevd processes > 5: sudo pkill -f systemd-udevd && sudo systemctl restart systemd-udevd")
            print(f"   - If load > {self.load_threshold:.2f}: Wait longer or consider system restart")
        
        print(f"{'='*60}")
        
        return True

    # =============================================================================
    # INTEGRATED ANALYSIS AND VISUALIZATION FUNCTIONS
    # =============================================================================
    
    def load_latency_data(self, file_path):
        """Load latency data from CSV file."""
        try:
            data = pd.read_csv(file_path, header=None, names=['latency'])
            return data['latency'].values
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def load_resource_data(self, file_path):
        """Load resource usage data from CSV file."""
        try:
            data = pd.read_csv(file_path)
            if 'timestamp' in data.columns:
                try:
                    data['timestamp'] = pd.to_datetime(data['timestamp'])
                except:
                    pass
            return data
        except Exception as e:
            print(f"Error reading resource data {file_path}: {e}")
            return None
    
    def calculate_statistics(self, latency_data, test_duration_seconds=None, filename=None):
        """Calculate statistical measures for latency data.
        
        Note: latency_data is expected to be in microseconds (μs) from the invoker.
        All returned latency values are in microseconds.
        """
        if latency_data is None or len(latency_data) == 0:
            return None
        
        # All calculations done in microseconds (μs)
        stats = {
            'min': np.min(latency_data),      # μs
            'max': np.max(latency_data),      # μs
            'average': np.mean(latency_data), # μs
            'median': np.median(latency_data), # μs
            'p95': np.percentile(latency_data, 95), # μs
            'p99': np.percentile(latency_data, 99), # μs
            'std': np.std(latency_data)       # μs
        }
        
        total_requests = len(latency_data)
        
        if filename:
            import re
            match = re.search(r'target_rps(\d+\.?\d*)_actual_rps(\d+\.?\d*)_lat\.csv', filename)
            if match:
                stats['target_rps'] = float(match.group(1))
                stats['throughput_rps'] = float(match.group(2))
            else:
                if test_duration_seconds:
                    stats['throughput_rps'] = total_requests / test_duration_seconds
                else:
                    avg_latency_seconds = stats['average'] / 1000
                    if avg_latency_seconds > 0:
                        stats['throughput_rps'] = 1 / avg_latency_seconds
                    else:
                        stats['throughput_rps'] = 0
                stats['target_rps'] = stats['throughput_rps']
        else:
            if test_duration_seconds:
                stats['throughput_rps'] = total_requests / test_duration_seconds
            else:
                avg_latency_seconds = stats['average'] / 1000
                if avg_latency_seconds > 0:
                    stats['throughput_rps'] = 1 / avg_latency_seconds
                else:
                    stats['throughput_rps'] = 0
            stats['target_rps'] = stats['throughput_rps']
        
        stats['total_requests'] = total_requests
        return stats
    
    def create_comprehensive_time_series(self, all_data, all_stats, resource_data=None):
        """Create comprehensive time series chart for the whole test."""
        if resource_data is None or resource_data.empty:
            print("  No resource data available for comprehensive time series")
            return False
        
        print(f"\n--- Creating Comprehensive Time Series Chart ---")
        
        try:
            # Set style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
            
            # Build ordered list of (target_rps, iteration, data)
            ordered_entries = []
            for filename, data in all_data.items():
                if data is None:
                    continue
                try:
                    # Expect: target_rps{R}_iter{II}_rps{A}_lat.csv
                    m = re.search(r'target_rps(\d+\.?\d*)_iter(\d+)_rps(\d+\.?\d*)_lat\.csv', filename)
                    if m:
                        target_rps = float(m.group(1))
                        iteration = int(m.group(2))
                        ordered_entries.append((target_rps, iteration, data, filename))
                    else:
                        # Fallback: put at end if pattern doesn't match
                        ordered_entries.append((float('inf'), 999, data, filename))
                except Exception:
                    ordered_entries.append((float('inf'), 999, data, filename))
            
            # Sort by target RPS then iteration
            ordered_entries.sort(key=lambda x: (x[0], x[1]))
            
            # Concatenate all latency datasets for the full test series
            concatenated = np.concatenate([e[2] for e in ordered_entries]) if ordered_entries else None
            total_requests = int(len(concatenated)) if concatenated is not None else 0
            
            # Create request axis for resource data alignment
            time_points = np.linspace(0, total_requests, len(resource_data))
            
            # Plot pod count and resources
            ax2.plot(time_points, resource_data['pod_count'], 'g-', linewidth=2, label='Pod Count')
            ax2.set_ylabel('Pod Count')
            ax2.set_xlabel('Request Number')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
            
            if 'cpu_usage_millicores' in resource_data.columns:
                ax3 = ax2.twinx()
                ax3.plot(time_points, resource_data['cpu_usage_millicores'], 'orange', linewidth=2, label='CPU (millicores)', alpha=0.7)
                ax3.set_ylabel('CPU Usage (millicores)', color='orange')
                ax3.legend(loc='upper right')
            
            if 'memory_usage_mib' in resource_data.columns:
                ax3.plot(time_points, resource_data['memory_usage_mib'], 'purple', linewidth=2, label='Memory (MiB)', alpha=0.7)
                ax3.set_ylabel('Memory Usage (MiB)', color='purple')
            
            # Compute phase offsets using actual lengths per target RPS
            request_offset = 0
            phase_lengths = {}
            for target_rps, iteration, data, _ in ordered_entries:
                phase_lengths.setdefault(target_rps, 0)
                phase_lengths[target_rps] += len(data)
            
            for target_rps in sorted(phase_lengths.keys()):
                ax2.axvline(x=request_offset, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax2.text(request_offset, ax2.get_ylim()[1] * 0.9, f'RPS {target_rps:.0f}', 
                         rotation=90, verticalalignment='top', fontsize=8)
                request_offset += phase_lengths[target_rps]
            
            # Plot full latency series with moving average
            if concatenated is not None and len(concatenated) > 0:
                latency_ms = concatenated / 1000.0
                ax1.plot(range(len(latency_ms)), latency_ms, alpha=0.3, linewidth=0.8, label='Latency')
                ax1.set_ylabel('Latency (ms)')
                ax1.set_title(f'Comprehensive Test Timeline - {self.title}')
                ax1.grid(True, alpha=0.3)
                
                # Moving average over a window proportional to phase size
                window_size = max(20, min(1000, len(latency_ms) // 200))
                if window_size > 1:
                    moving_avg = pd.Series(latency_ms).rolling(window=window_size).mean()
                    ax1.plot(range(len(moving_avg)), moving_avg, 'r-', linewidth=2, 
                             label=f'Moving Average ({window_size} requests)')
                    ax1.legend()
            
            plt.tight_layout()
            
            # Save the chart
            charts_dir = os.path.join(self.results_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            output_path = os.path.join(charts_dir, "comprehensive_timeseries_with_pods.png")
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f" Comprehensive time series chart saved: {output_path}")
            return True
            
        except Exception as e:
            print(f" Failed to create comprehensive time series chart: {e}")
            return False
    
    def create_latency_vs_throughput_chart(self, all_stats):
        """Create latency vs throughput scatter plot."""
        if not all_stats:
            return False
        
        print(f"\n--- Creating Latency vs Throughput Chart ---")
        
        try:
            throughputs = []
            avg_latencies = []
            names = []
            
            for name, stats in all_stats.items():
                if stats and 'throughput_rps' in stats:
                    throughputs.append(stats['throughput_rps'])
                    avg_latencies.append(stats['average'] / 1000)  # Convert μs to ms
                    names.append(name)
            
            if throughputs:
                plt.figure(figsize=(10, 8))
                plt.scatter(throughputs, avg_latencies, s=100, alpha=0.7)
                
                # Add labels
                for i, name in enumerate(names):
                    plt.annotate(name, (throughputs[i], avg_latencies[i]), 
                                xytext=(5, 5), textcoords='offset points')
                
                plt.xlabel('Throughput (RPS)')
                plt.ylabel('Average Latency (ms)')
                plt.title(f'Throughput vs Average Latency - {self.title}')
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                charts_dir = os.path.join(self.results_dir, "charts")
                os.makedirs(charts_dir, exist_ok=True)
                output_path = os.path.join(charts_dir, "latency_vs_throughput.png")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f" Latency vs throughput chart saved: {output_path}")
                return True
                
        except Exception as e:
            print(f" Failed to create latency vs throughput chart: {e}")
            return False
    
    def create_percentile_charts(self, all_stats):
        """Create P95, P99, and Average latency vs RPS charts."""
        if not all_stats:
            return False
        
        print(f"\n--- Creating Percentile Charts ---")
        
        try:
            charts_dir = os.path.join(self.results_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            # Extract data
            rps_values = []
            p95_values = []
            p99_values = []
            avg_values = []
            names = []
            
            for name, stats in all_stats.items():
                if stats and 'throughput_rps' in stats:
                    rps_values.append(stats['throughput_rps'])
                    p95_values.append(stats['p95'] / 1000)  # Convert μs to ms
                    p99_values.append(stats['p99'] / 1000)  # Convert μs to ms
                    avg_values.append(stats['average'] / 1000)  # Convert μs to ms
                    names.append(name)
            
            if rps_values:
                # Sort by RPS for proper line plot
                sorted_data = sorted(zip(rps_values, p95_values, p99_values, avg_values, names))
                rps_sorted, p95_sorted, p99_sorted, avg_sorted, names_sorted = zip(*sorted_data)
                
                # P95 chart
                plt.figure(figsize=(12, 8))
                plt.plot(rps_sorted, p95_sorted, 'bo-', linewidth=3, markersize=8, alpha=0.8)
                plt.xlabel('Throughput (RPS)')
                plt.ylabel('P95 Latency (ms)')
                plt.title(f'P95 Latency vs Throughput - {self.title}')
                plt.grid(True, alpha=0.3)
                plt.yscale('log')
                plt.tight_layout()
                plt.savefig(os.path.join(charts_dir, "p95_vs_rps.png"), dpi=300, bbox_inches='tight')
                plt.close()
                
                # P99 chart
                plt.figure(figsize=(12, 8))
                plt.plot(rps_sorted, p99_sorted, 'go-', linewidth=3, markersize=8, alpha=0.8)
                plt.xlabel('Throughput (RPS)')
                plt.ylabel('P99 Latency (ms)')
                plt.title(f'P99 Latency vs Throughput - {self.title}')
                plt.grid(True, alpha=0.3)
                plt.yscale('log')
                plt.tight_layout()
                plt.savefig(os.path.join(charts_dir, "p99_vs_rps.png"), dpi=300, bbox_inches='tight')
                plt.close()
                
                # Average chart
                plt.figure(figsize=(12, 8))
                plt.plot(rps_sorted, avg_sorted, 'mo-', linewidth=3, markersize=8, alpha=0.8)
                plt.xlabel('Throughput (RPS)')
                plt.ylabel('Average Latency (ms)')
                plt.title(f'Average Latency vs Throughput - {self.title}')
                plt.grid(True, alpha=0.3)
                plt.yscale('log')
                plt.tight_layout()
                plt.savefig(os.path.join(charts_dir, "avg_vs_rps.png"), dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f" Percentile charts saved in: {charts_dir}")
                return True
                
        except Exception as e:
            print(f" Failed to create percentile charts: {e}")
            return False
    
    def check_system_health_after_test(self):
        """Check system health after test completion and provide recommendations."""
        try:
            # Check system load
            load = os.getloadavg()[0]
            load_threshold = getattr(self, 'load_threshold', 4.0)
            
            # Check udevd processes
            result = subprocess.run(['pgrep', '-c', 'systemd-udevd'], 
                                  capture_output=True, text=True)
            udevd_count = int(result.stdout.strip())
            
            # Check available memory
            result = subprocess.run(['free', '-g'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            mem_line = lines[1].split()
            available_gb = float(mem_line[6])
            
            # Check high CPU processes
            result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:6]  # Skip header, get top 5
            high_cpu_processes = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    cpu_percent = float(parts[2])
                    process_name = ' '.join(parts[10:])
                    if cpu_percent > 50:
                        high_cpu_processes.append((cpu_percent, process_name))
            
            # Print system status
            print(f" System Load: {load:.2f}")
            print(f" udevd Processes: {udevd_count}")
            print(f" Available Memory: {available_gb:.1f}GB")
            
            if high_cpu_processes:
                print(f"  High CPU Processes:")
                for cpu, process in high_cpu_processes[:3]:  # Show top 3
                    print(f"   - {process}: {cpu:.1f}%")
            
            # Determine if system is healthy
            issues = []
            
            if load > load_threshold:
                issues.append(f"High system load ({load:.2f} > {load_threshold:.2f})")
            
            if udevd_count > 5:
                issues.append(f"Too many udevd processes ({udevd_count})")
            
            if available_gb < 8.0:
                issues.append(f"Low available memory ({available_gb:.1f}GB)")
            
            if high_cpu_processes and high_cpu_processes[0][0] > 80:
                issues.append(f"Very high CPU process ({high_cpu_processes[0][1]}: {high_cpu_processes[0][0]:.1f}%)")
            
            if issues:
                print(f"\n System Issues Detected:")
                for issue in issues:
                    print(f"   - {issue}")
                return False
            else:
                print(f"\n✅ All system metrics are within normal ranges")
                return True
                
        except Exception as e:
            print(f" Error checking system health: {e}")
            print(f"  Unable to determine system health - proceed with caution")
            return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Comprehensive Test Runner for vSwarm with Pod Monitoring')
    parser.add_argument('--title', '-t', required=True, help='Test title (used for file naming)')
    parser.add_argument('--invoker-dir', default='../tools/invoker', help='Directory containing invoker binary')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running invoker tests and just do analysis')
    parser.add_argument('--service', '-s', help='Kubernetes service name to monitor (enables pod monitoring)')
    parser.add_argument('--namespace', '-n', default='default', help='Kubernetes namespace (default: default)')
    
    args = parser.parse_args()
    return args.title, args.invoker_dir, args.skip_tests, args.service, args.namespace


def main():
    """Main function."""
    try:
        title, invoker_dir, skip_tests, service_name, namespace = parse_arguments()
        
        # Create and run the test runner
        runner = ComprehensiveTestRunner(title, invoker_dir, service_name, namespace)
        success = runner.run_complete_pipeline(skip_tests)
        
        if success:
            print("\n All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n Pipeline failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
