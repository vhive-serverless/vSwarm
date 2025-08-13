#!/usr/bin/env python3
"""
B1-B4 Configuration Comparison Analysis
Analyzes and compares Python, Go, and Node.js performance across B1-B4 configurations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
import os
from pathlib import Path

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_all_b_configs():
    """Load all B1-B4 configuration results"""
    results = []
    
    # Configuration mapping
    config_info = {
        'b1': {'pods': 2, 'cpu_per_pod': 500, 'memory': '1Gi', 'concurrency': 5, 'description': 'Moderate (2 pods, 500m)'},
        'b2': {'pods': 4, 'cpu_per_pod': 250, 'memory': '1Gi', 'concurrency': 10, 'description': 'Balanced (4 pods, 250m)'},
        'b3': {'pods': 8, 'cpu_per_pod': 125, 'memory': '1Gi', 'concurrency': 20, 'description': 'Horizontal (8 pods, 125m)'},
        'b4': {'pods': 10, 'cpu_per_pod': 100, 'memory': '1Gi', 'concurrency': 20, 'description': 'High Horizontal (10 pods, 100m)'}
    }
    
    # Look for all result directories
    patterns = ['results_fibonacci_python_b*', 'results_fibonacci_go_b*', 'results_fibonacci_nodejs_b*']
    
    for pattern in patterns:
        dirs = glob.glob(pattern)
        for result_dir in dirs:
            # Extract runtime and config from directory name
            match = re.search(r'fibonacci_(\w+)_b(\d+)', result_dir)
            if not match:
                continue
                
            runtime = match.group(1)
            config = f'b{match.group(2)}'
            
            if config not in config_info:
                continue
            
            # Load detailed analysis
            analysis_file = os.path.join(result_dir, f"fibonacci_{runtime}_{config}_detailed_analysis.csv")
            if os.path.exists(analysis_file):
                df = pd.read_csv(analysis_file)
                
                # Load monitoring data
                monitoring_file = os.path.join(result_dir, f"fibonacci_{runtime}_{config}_pod_monitoring_converted.csv")
                pod_data = None
                if os.path.exists(monitoring_file):
                    pod_data = pd.read_csv(monitoring_file)
                
                # Process each RPS test in the detailed analysis
                for _, row in df.iterrows():
                    # Extract target RPS from filename
                    filename = row['filename']
                    rps_match = re.search(r'target_rps(\d+\.?\d*)', filename)
                    target_rps = float(rps_match.group(1)) if rps_match else 0
                    
                    result_entry = {
                        'runtime': runtime,
                        'config': config,
                        'config_description': config_info[config]['description'],
                        'pods': config_info[config]['pods'],
                        'cpu_per_pod_m': config_info[config]['cpu_per_pod'],
                        'total_cpu_m': config_info[config]['pods'] * config_info[config]['cpu_per_pod'],
                        'concurrency': config_info[config]['concurrency'],
                        'target_rps': target_rps,
                        'achieved_rps': row['throughput_rps'],
                        'avg_latency_ms': row['average_latency_ms'],
                        'median_latency_ms': row['median_latency_ms'],
                        'p95_latency_ms': row['p95_latency_ms'],
                        'p99_latency_ms': row['p99_latency_ms'],
                        'min_latency_ms': row['min_latency_ms'],
                        'max_latency_ms': row['max_latency_ms'],
                        'total_requests': row['total_requests'],
                        'result_dir': result_dir
                    }
                    
                    # Add pod monitoring data if available
                    if pod_data is not None and len(pod_data) > 0:
                        result_entry['avg_cpu_percent'] = pod_data['cpu_percent'].mean()
                        result_entry['avg_memory_percent'] = pod_data['memory_percent'].mean()
                        result_entry['avg_pod_count'] = pod_data['pod_count'].mean()
                    
                    results.append(result_entry)
    
    return pd.DataFrame(results)

def create_latency_comparison_charts(df, output_dir="b1_b4_charts"):
    """Create comprehensive latency comparison charts"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Average Latency by Configuration and Runtime
    plt.figure(figsize=(15, 10))
    
    # Create pivot table for heatmap
    latency_pivot = df.pivot_table(
        values='avg_latency_ms', 
        index=['runtime', 'config'], 
        columns='target_rps', 
        aggfunc='mean'
    )
    
    plt.subplot(2, 2, 1)
    sns.heatmap(latency_pivot, annot=True, fmt='.1f', cmap='YlOrRd')
    plt.title('Average Latency Heatmap (ms)')
    plt.ylabel('Runtime + Config')
    
    # 2. Latency vs RPS by Runtime (separate lines for each config)
    plt.subplot(2, 2, 2)
    for runtime in df['runtime'].unique():
        for config in ['b1', 'b2', 'b3', 'b4']:
            runtime_config_data = df[(df['runtime'] == runtime) & (df['config'] == config)]
            if len(runtime_config_data) > 0:
                plt.plot(runtime_config_data['target_rps'], runtime_config_data['avg_latency_ms'], 
                        marker='o', label=f'{runtime} {config}', linewidth=2)
    
    plt.xlabel('Target RPS')
    plt.ylabel('Average Latency (ms)')
    plt.title('Average Latency vs RPS')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # 3. P95 Latency Comparison
    plt.subplot(2, 2, 3)
    high_rps_data = df[df['target_rps'] >= 200]  # Focus on high load
    sns.boxplot(data=high_rps_data, x='config', y='p95_latency_ms', hue='runtime')
    plt.title('P95 Latency at High Load (200+ RPS)')
    plt.ylabel('P95 Latency (ms)')
    
    # 4. Latency Efficiency (Latency per CPU unit)
    plt.subplot(2, 2, 4)
    df['latency_per_cpu'] = df['avg_latency_ms'] / df['total_cpu_m'] * 1000  # Normalize
    efficiency_data = df[df['target_rps'] >= 100]  # Medium to high load
    sns.barplot(data=efficiency_data, x='config', y='latency_per_cpu', hue='runtime')
    plt.title('Latency Efficiency (Lower is Better)')
    plt.ylabel('Latency per 1000m CPU')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'latency_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_throughput_comparison_charts(df, output_dir="b1_b4_charts"):
    """Create throughput and scaling comparison charts"""
    
    # Calculate max throughput for each runtime+config combination
    max_throughput = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'total_cpu_m': 'first',
        'pods': 'first',
        'config_description': 'first'
    }).reset_index()
    
    max_throughput['rps_per_cpu'] = max_throughput['achieved_rps'] / max_throughput['total_cpu_m'] * 1000
    max_throughput['rps_per_pod'] = max_throughput['achieved_rps'] / max_throughput['pods']
    
    plt.figure(figsize=(16, 12))
    
    # 1. Maximum Throughput by Configuration
    plt.subplot(2, 3, 1)
    throughput_pivot = max_throughput.pivot(index='config', columns='runtime', values='achieved_rps')
    throughput_pivot.plot(kind='bar', ax=plt.gca())
    plt.title('Maximum Throughput by Configuration')
    plt.ylabel('Max RPS')
    plt.xlabel('Configuration')
    plt.legend(title='Runtime')
    plt.xticks(rotation=45)
    
    # 2. RPS per CPU (Resource Efficiency)
    plt.subplot(2, 3, 2)
    efficiency_pivot = max_throughput.pivot(index='config', columns='runtime', values='rps_per_cpu')
    efficiency_pivot.plot(kind='bar', ax=plt.gca())
    plt.title('Throughput Efficiency (RPS per 1000m CPU)')
    plt.ylabel('RPS per 1000m CPU')
    plt.xlabel('Configuration')
    plt.legend(title='Runtime')
    plt.xticks(rotation=45)
    
    # 3. RPS per Pod (Horizontal Scaling Efficiency)
    plt.subplot(2, 3, 3)
    pod_efficiency_pivot = max_throughput.pivot(index='config', columns='runtime', values='rps_per_pod')
    pod_efficiency_pivot.plot(kind='bar', ax=plt.gca())
    plt.title('RPS per Pod')
    plt.ylabel('RPS per Pod')
    plt.xlabel('Configuration')
    plt.legend(title='Runtime')
    plt.xticks(rotation=45)
    
    # 4. Throughput vs Target RPS (Saturation Analysis)
    plt.subplot(2, 3, 4)
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        for config in ['b1', 'b2', 'b3', 'b4']:
            config_data = runtime_data[runtime_data['config'] == config]
            if len(config_data) > 0:
                plt.plot(config_data['target_rps'], config_data['achieved_rps'], 
                        marker='o', label=f'{runtime} {config}', alpha=0.7)
    
    # Add perfect scaling line
    max_rps = df['target_rps'].max()
    plt.plot([0, max_rps], [0, max_rps], 'k--', alpha=0.5, label='Perfect Scaling')
    plt.xlabel('Target RPS')
    plt.ylabel('Achieved RPS')
    plt.title('Achieved vs Target RPS')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    # 5. Configuration Scaling Patterns
    plt.subplot(2, 3, 5)
    configs = ['b1', 'b2', 'b3', 'b4']
    for runtime in df['runtime'].unique():
        runtime_max = max_throughput[max_throughput['runtime'] == runtime]
        if len(runtime_max) > 0:
            plt.plot(configs, runtime_max.set_index('config').reindex(configs)['achieved_rps'], 
                    marker='o', linewidth=3, label=runtime)
    
    plt.xlabel('Configuration')
    plt.ylabel('Maximum RPS')
    plt.title('Scaling Pattern Across Configurations')
    plt.legend()
    plt.grid(True)
    
    # 6. Resource Utilization vs Performance
    plt.subplot(2, 3, 6)
    if 'avg_cpu_percent' in df.columns:
        high_load = df[df['target_rps'] >= 200]
        scatter = plt.scatter(high_load['avg_cpu_percent'], high_load['achieved_rps'], 
                            c=high_load['runtime'].astype('category').cat.codes, 
                            s=high_load['total_cpu_m']/10, alpha=0.6)
        plt.xlabel('CPU Utilization %')
        plt.ylabel('Achieved RPS')
        plt.title('CPU Utilization vs Performance\n(Bubble size = Total CPU)')
        
        # Add runtime labels
        for runtime in df['runtime'].unique():
            runtime_data = high_load[high_load['runtime'] == runtime]
            if len(runtime_data) > 0:
                plt.scatter([], [], label=runtime, 
                          c=plt.cm.tab10(df['runtime'].unique().tolist().index(runtime)))
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'throughput_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_pod_scaling_analysis(df, output_dir="b1_b4_charts"):
    """Create pod scaling and resource utilization analysis"""
    
    plt.figure(figsize=(14, 10))
    
    # 1. Pod Count vs Performance
    plt.subplot(2, 2, 1)
    max_perf = df.groupby(['runtime', 'config', 'pods']).agg({
        'achieved_rps': 'max'
    }).reset_index()
    
    for runtime in max_perf['runtime'].unique():
        runtime_data = max_perf[max_perf['runtime'] == runtime]
        plt.plot(runtime_data['pods'], runtime_data['achieved_rps'], 
                marker='o', linewidth=2, label=runtime)
    
    plt.xlabel('Number of Pods')
    plt.ylabel('Maximum RPS')
    plt.title('Horizontal Scaling: Pods vs Performance')
    plt.legend()
    plt.grid(True)
    
    # 2. CPU per Pod vs Performance
    plt.subplot(2, 2, 2)
    for runtime in max_perf['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        config_max = runtime_data.groupby(['config', 'cpu_per_pod_m']).agg({
            'achieved_rps': 'max'
        }).reset_index()
        plt.plot(config_max['cpu_per_pod_m'], config_max['achieved_rps'], 
                marker='s', linewidth=2, label=runtime)
    
    plt.xlabel('CPU per Pod (millicores)')
    plt.ylabel('Maximum RPS')
    plt.title('Vertical Scaling: CPU per Pod vs Performance')
    plt.legend()
    plt.grid(True)
    
    # 3. Total CPU vs Performance (Resource Efficiency)
    plt.subplot(2, 2, 3)
    for runtime in df['runtime'].unique():
        runtime_data = df[df['runtime'] == runtime]
        config_max = runtime_data.groupby(['config', 'total_cpu_m']).agg({
            'achieved_rps': 'max'
        }).reset_index()
        plt.plot(config_max['total_cpu_m'], config_max['achieved_rps'], 
                marker='^', linewidth=2, label=runtime)
    
    plt.xlabel('Total CPU Allocation (millicores)')
    plt.ylabel('Maximum RPS')
    plt.title('Total Resource vs Performance')
    plt.legend()
    plt.grid(True)
    
    # 4. Configuration Efficiency Matrix
    plt.subplot(2, 2, 4)
    efficiency_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'total_cpu_m': 'first',
        'pods': 'first'
    }).reset_index()
    efficiency_data['efficiency'] = efficiency_data['achieved_rps'] / efficiency_data['total_cpu_m'] * 1000
    
    efficiency_pivot = efficiency_data.pivot(index='config', columns='runtime', values='efficiency')
    sns.heatmap(efficiency_pivot, annot=True, fmt='.2f', cmap='Greens')
    plt.title('Efficiency Matrix\n(RPS per 1000m CPU)')
    plt.ylabel('Configuration')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pod_scaling_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_comprehensive_report(df, output_dir="b1_b4_charts"):
    """Generate a comprehensive text report"""
    
    report_file = os.path.join(output_dir, 'b1_b4_comparison_report.txt')
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("B1-B4 CONFIGURATION COMPARISON REPORT\n")
        f.write("Python vs Go vs Node.js Performance Analysis\n")
        f.write("=" * 80 + "\n\n")
        
        # Configuration Summary
        f.write("CONFIGURATION SUMMARY\n")
        f.write("-" * 40 + "\n")
        configs = df.groupby('config').first()
        for config in ['b1', 'b2', 'b3', 'b4']:
            if config in configs.index:
                info = configs.loc[config]
                f.write(f"{config.upper()}: {info['config_description']}\n")
                f.write(f"  Pods: {info['pods']}, CPU per pod: {info['cpu_per_pod_m']}m, ")
                f.write(f"Total CPU: {info['total_cpu_m']}m, Concurrency: {info['concurrency']}\n\n")
        
        # Maximum Throughput Analysis
        f.write("MAXIMUM THROUGHPUT ANALYSIS\n")
        f.write("-" * 40 + "\n")
        max_throughput = df.groupby(['runtime', 'config']).agg({
            'achieved_rps': 'max',
            'total_cpu_m': 'first'
        }).reset_index()
        max_throughput['efficiency'] = max_throughput['achieved_rps'] / max_throughput['total_cpu_m'] * 1000
        
        for runtime in ['go', 'python', 'nodejs']:
            if runtime in max_throughput['runtime'].values:
                f.write(f"\n{runtime.upper()} Runtime:\n")
                runtime_data = max_throughput[max_throughput['runtime'] == runtime]
                for _, row in runtime_data.iterrows():
                    f.write(f"  {row['config']}: {row['achieved_rps']:.1f} RPS ")
                    f.write(f"(Efficiency: {row['efficiency']:.2f} RPS/1000m CPU)\n")
        
        # Best Performers
        f.write("\n\nBEST PERFORMERS BY CATEGORY\n")
        f.write("-" * 40 + "\n")
        
        # Highest throughput
        best_throughput = max_throughput.loc[max_throughput['achieved_rps'].idxmax()]
        f.write(f"Highest Throughput: {best_throughput['runtime']} {best_throughput['config']} ")
        f.write(f"({best_throughput['achieved_rps']:.1f} RPS)\n")
        
        # Most efficient
        best_efficiency = max_throughput.loc[max_throughput['efficiency'].idxmax()]
        f.write(f"Most Efficient: {best_efficiency['runtime']} {best_efficiency['config']} ")
        f.write(f"({best_efficiency['efficiency']:.2f} RPS/1000m CPU)\n")
        
        # Latency Analysis
        f.write("\n\nLATENCY ANALYSIS (at 200+ RPS)\n")
        f.write("-" * 40 + "\n")
        high_load = df[df['target_rps'] >= 200]
        latency_summary = high_load.groupby(['runtime', 'config']).agg({
            'avg_latency_ms': 'mean',
            'p95_latency_ms': 'mean'
        }).reset_index()
        
        for runtime in ['go', 'python', 'nodejs']:
            if runtime in latency_summary['runtime'].values:
                f.write(f"\n{runtime.upper()} Runtime (High Load):\n")
                runtime_data = latency_summary[latency_summary['runtime'] == runtime]
                for _, row in runtime_data.iterrows():
                    f.write(f"  {row['config']}: Avg {row['avg_latency_ms']:.1f}ms, ")
                    f.write(f"P95 {row['p95_latency_ms']:.1f}ms\n")
        
        # Key Insights
        f.write("\n\nKEY INSIGHTS\n")
        f.write("-" * 40 + "\n")
        
        # Runtime ranking by max throughput
        runtime_ranking = max_throughput.groupby('runtime')['achieved_rps'].max().sort_values(ascending=False)
        f.write("Runtime Performance Ranking (by max throughput):\n")
        for i, (runtime, max_rps) in enumerate(runtime_ranking.items(), 1):
            f.write(f"  {i}. {runtime}: {max_rps:.1f} RPS\n")
        
        # Best configuration per runtime
        f.write("\nBest Configuration per Runtime:\n")
        for runtime in max_throughput['runtime'].unique():
            runtime_data = max_throughput[max_throughput['runtime'] == runtime]
            best_config = runtime_data.loc[runtime_data['achieved_rps'].idxmax()]
            f.write(f"  {runtime}: {best_config['config']} ({best_config['achieved_rps']:.1f} RPS)\n")
    
    print(f"📊 Comprehensive report saved to: {report_file}")

def main():
    """Main analysis function"""
    print("Loading B1-B4 configuration data...")
    
    # Load all data
    df = load_all_b_configs()
    if df.empty:
        print("❌ No B1-B4 result directories found!")
        print("Expected directories: results_fibonacci_python_b1, results_fibonacci_go_b2, etc.")
        return
    
    print(f"✅ Found {len(df)} test results across {df['runtime'].nunique()} runtimes and {df['config'].nunique()} configurations")
    
    # Create output directory
    output_dir = "b1_b4_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all charts
    print("Creating latency comparison charts...")
    create_latency_comparison_charts(df, output_dir)
    
    print("Creating throughput comparison charts...")
    create_throughput_comparison_charts(df, output_dir)
    
    print("Creating pod scaling analysis...")
    create_pod_scaling_analysis(df, output_dir)
    
    # Generate comprehensive report
    print("Generating comprehensive report...")
    generate_comprehensive_report(df, output_dir)
    
    # Save detailed data
    summary_file = os.path.join(output_dir, 'b1_b4_detailed_data.csv')
    df.to_csv(summary_file, index=False)
    
    print(f"\n🎉 Analysis complete!")
    print(f"📊 Charts saved in: {output_dir}/")
    print(f"📈 Generated charts:")
    print(f"  - latency_comparison.png")
    print(f"  - throughput_comparison.png") 
    print(f"  - pod_scaling_analysis.png")
    print(f"📄 Report: {output_dir}/b1_b4_comparison_report.txt")
    print(f"📊 Raw data: {output_dir}/b1_b4_detailed_data.csv")

if __name__ == "__main__":
    main() 