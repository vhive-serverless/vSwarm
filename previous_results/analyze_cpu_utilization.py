#!/usr/bin/env python3
"""
CPU Utilization Efficiency Analysis
Analyzes results from CPU scaling study to detect resource waste
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import re
import os

def load_test_results(base_path="test_set_C/results_fibonacci_*_c*"):
    """Load all CPU scaling test results"""
    results = []
    
    # Find all test result directories
    test_dirs = glob.glob(base_path)
    
    for test_dir in test_dirs:
        # Extract test configuration from directory name
        match = re.search(r'fibonacci_(\w+)_c(\d+)', test_dir)
        if not match:
            continue
            
        runtime = match.group(1)
        cpu_config = int(match.group(2))
        
        # Load detailed analysis (handle different naming patterns)
        analysis_file = os.path.join(test_dir, f"fibonacci_{runtime}_c{cpu_config}_detailed_analysis.csv")
        if not os.path.exists(analysis_file):
            # Try alternative naming pattern (e.g., fibonacci_c1_ instead of fibonacci_python_c1_)
            analysis_file = os.path.join(test_dir, f"fibonacci_c{cpu_config}_detailed_analysis.csv")
        
        if os.path.exists(analysis_file):
            df = pd.read_csv(analysis_file)
            
            # Extract key metrics
            max_rps = df['throughput_rps'].max()
            avg_latency_at_max = df[df['throughput_rps'] == max_rps]['average_latency_ms'].iloc[0]
            
            # Load monitoring data for CPU utilization
            monitoring_file = os.path.join(test_dir, f"fibonacci_{runtime}_c{cpu_config}_pod_monitoring.csv")
            if not os.path.exists(monitoring_file):
                # Try alternative naming pattern
                monitoring_file = os.path.join(test_dir, f"fibonacci_c{cpu_config}_pod_monitoring.csv")
            
            cpu_utilization = None
            if os.path.exists(monitoring_file):
                mon_df = pd.read_csv(monitoring_file)
                # Handle different column names for CPU usage
                if 'cpu_usage_millicores' in mon_df.columns:
                    cpu_utilization = mon_df['cpu_usage_millicores'].mean()
                elif 'cpu_percent' in mon_df.columns:
                    # Convert percentage to millicores (assuming 1000m = 100%)
                    cpu_utilization = mon_df['cpu_percent'].mean() * 10
            
            results.append({
                'runtime': runtime,
                'cpu_config': cpu_config,
                'max_rps': max_rps,
                'avg_latency_ms': avg_latency_at_max,
                'cpu_utilization_millicores': cpu_utilization,
                'test_dir': test_dir
            })
    
    return pd.DataFrame(results)

def calculate_efficiency_metrics(df):
    """Calculate CPU efficiency and scaling metrics"""
    results = []
    
    # Map C1, C2 to actual CPU allocations (you'll need to specify these)
    # Assuming C1 = 1 vCPU, C2 = 2 vCPU based on typical CPU scaling studies
    cpu_allocation_map = {1: 1000, 2: 2000}  # millicores
    
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime].sort_values('cpu_config')
        
        baseline = runtime_data.iloc[0]  # C1 baseline
        
        for _, row in runtime_data.iterrows():
            cpu_allocated = cpu_allocation_map.get(row['cpu_config'], row['cpu_config'] * 1000)
            cpu_efficiency = (row['cpu_utilization_millicores'] / cpu_allocated * 100) if row['cpu_utilization_millicores'] else None
            
            performance_scaling = (row['max_rps'] / baseline['max_rps']) * 100
            performance_per_vcpu = row['max_rps'] / (cpu_allocated / 1000)  # RPS per vCPU
            
            cpu_waste_factor = (cpu_allocated / 1000) - (row['max_rps'] / baseline['max_rps'])
            
            results.append({
                'runtime': row['runtime'],
                'cpu_config': row['cpu_config'],
                'cpu_allocated_millicores': cpu_allocated,
                'max_rps': row['max_rps'],
                'avg_latency_ms': row['avg_latency_ms'],
                'cpu_efficiency_percent': cpu_efficiency,
                'performance_scaling_percent': performance_scaling,
                'performance_per_vcpu': performance_per_vcpu,
                'cpu_waste_factor': cpu_waste_factor
            })
    
    return pd.DataFrame(results)

def create_visualizations(df, output_dir="cpu_study_charts"):
    """Create visualization charts for CPU utilization study"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. CPU Efficiency by Runtime
    plt.figure(figsize=(12, 8))
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        plt.plot(runtime_data['cpu_config'], runtime_data['cpu_efficiency_percent'], 
                marker='o', linewidth=2, label=f'{runtime.title()}')
    
    plt.xlabel('vCPU Allocation')
    plt.ylabel('CPU Utilization Efficiency (%)')
    plt.title('CPU Utilization Efficiency by Runtime')
    plt.legend()
    plt.grid(True)
    plt.xticks([1, 2])
    plt.savefig(os.path.join(output_dir, 'cpu_efficiency_by_runtime.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Performance Scaling
    plt.figure(figsize=(12, 8))
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        plt.plot(runtime_data['cpu_config'], runtime_data['performance_scaling_percent'], 
                marker='s', linewidth=2, label=f'{runtime.title()}')
    
    plt.xlabel('vCPU Allocation')
    plt.ylabel('Performance Scaling (% of 1 vCPU baseline)')
    plt.title('Performance Scaling with CPU Allocation')
    plt.legend()
    plt.grid(True)
    plt.xticks([1, 2])
    plt.axhline(y=100, color='gray', linestyle='--', alpha=0.7, label='No improvement')
    plt.savefig(os.path.join(output_dir, 'performance_scaling.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Performance per vCPU (Cost Effectiveness)
    plt.figure(figsize=(12, 8))
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        plt.plot(runtime_data['cpu_config'], runtime_data['performance_per_vcpu'], 
                marker='^', linewidth=2, label=f'{runtime.title()}')
    
    plt.xlabel('vCPU Allocation')
    plt.ylabel('Max RPS per vCPU')
    plt.title('Cost Effectiveness: Performance per vCPU')
    plt.legend()
    plt.grid(True)
    plt.xticks([1, 2])
    plt.savefig(os.path.join(output_dir, 'performance_per_vcpu.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_report(df):
    """Generate analysis report with key findings"""
    print("=" * 80)
    print("CPU UTILIZATION EFFICIENCY ANALYSIS REPORT")
    print("=" * 80)
    
    print("\n1. PERFORMANCE SCALING ANALYSIS")
    print("-" * 40)
    
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime].sort_values('cpu_config')
        print(f"\n{runtime.upper()} Runtime:")
        
        baseline_rps = runtime_data.iloc[0]['max_rps']
        for _, row in runtime_data.iterrows():
            scaling = (row['max_rps'] / baseline_rps) * 100
            print(f"  {row['cpu_config']} vCPU: {row['max_rps']:.1f} RPS ({scaling:.1f}% of baseline)")
    
    print("\n2. CPU EFFICIENCY ANALYSIS")
    print("-" * 40)
    
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime].sort_values('cpu_config')
        print(f"\n{runtime.upper()} Runtime:")
        
        for _, row in runtime_data.iterrows():
            if row['cpu_efficiency_percent']:
                print(f"  {row['cpu_config']} vCPU: {row['cpu_efficiency_percent']:.1f}% CPU efficiency")
    
    print("\n3. RESOURCE WASTE QUANTIFICATION")
    print("-" * 40)
    
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime].sort_values('cpu_config')
        max_config = runtime_data.iloc[-1]  # 4 vCPU config
        baseline_config = runtime_data.iloc[0]  # 1 vCPU config
        
        performance_improvement = (max_config['max_rps'] / baseline_config['max_rps'] - 1) * 100
        cpu_increase = (max_config['cpu_config'] / baseline_config['cpu_config'] - 1) * 100
        
        print(f"\n{runtime.upper()}:")
        print(f"  CPU allocation increase: {cpu_increase:.0f}%")
        print(f"  Performance improvement: {performance_improvement:.1f}%")
        print(f"  Resource efficiency: {performance_improvement/cpu_increase*100:.1f}%")
    
    print("\n4. KEY FINDINGS")
    print("-" * 40)
    
    # Detect which runtimes show plateau vs scaling
    single_threaded = []
    multi_threaded = []
    
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime].sort_values('cpu_config')
        max_improvement = runtime_data['performance_scaling_percent'].max() - 100
        
        if max_improvement < 10:  # Less than 10% improvement
            single_threaded.append(runtime)
        else:
            multi_threaded.append(runtime)
    
    print(f"\nSingle-threaded behavior (plateau): {', '.join(single_threaded)}")
    print(f"Multi-threaded behavior (scaling): {', '.join(multi_threaded)}")
    
    print("\n" + "=" * 80)

def main():
    """Main analysis function"""
    print("Loading CPU utilization test results...")
    
    # Load test results
    raw_df = load_test_results()
    if raw_df.empty:
        print("No test results found. Make sure test directories exist.")
        return
    
    print(f"Found {len(raw_df)} test configurations")
    
    # Calculate efficiency metrics
    analysis_df = calculate_efficiency_metrics(raw_df)
    
    # Create visualizations
    create_visualizations(analysis_df)
    print("Charts saved to cpu_study_charts/")
    
    # Generate report
    generate_report(analysis_df)
    
    # Save detailed results
    analysis_df.to_csv('cpu_utilization_analysis.csv', index=False)
    print("\nDetailed results saved to cpu_utilization_analysis.csv")

if __name__ == "__main__":
    main() 