#!/usr/bin/env python3
"""
Cross-Runtime Performance Comparison Analysis
Analyzes and compares Python, Go, and Node.js performance across B1-B5 configurations
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

def load_all_runtime_data():
    """Load all runtime data (Python, Go, Node.js) across B1-B5 configurations"""
    results = []
    
    # Configuration mapping - corrected based on actual pod counts
    config_info = {
        'b1': {'pods': 1, 'cpu_per_pod': 1000, 'memory': '1Gi', 'concurrency': 100, 'description': 'Single Pod (1 pod, 1000m)'},
        'b2': {'pods': 2, 'cpu_per_pod': 500, 'memory': '1Gi', 'concurrency': 100, 'description': 'Dual Pod (2 pods, 500m)'},
        'b3': {'pods': 4, 'cpu_per_pod': 250, 'memory': '1Gi', 'concurrency': 100, 'description': 'Quad Pod (4 pods, 250m)'},
        'b4': {'pods': 8, 'cpu_per_pod': 125, 'memory': '1Gi', 'concurrency': 100, 'description': 'Octa Pod (8 pods, 125m)'},
        'b5': {'pods': 10, 'cpu_per_pod': 100, 'memory': '1Gi', 'concurrency': 100, 'description': 'Deca Pod (10 pods, 100m)'}
    }
    
    # Look for all runtime result directories
    runtimes = ['python', 'go', 'nodejs']
    patterns = [f'results_fibonacci_{runtime}_b*' for runtime in runtimes]
    
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

def create_runtime_comparison_charts(df, output_dir="cross_runtime_charts"):
    """Create comprehensive runtime comparison charts"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up color palette for runtimes
    runtime_colors = {'python': '#377eb8', 'go': '#4daf4a', 'nodejs': '#ff7f00'}
    
    plt.figure(figsize=(20, 16))
    
    # 1. Maximum Throughput by Runtime and Configuration
    plt.subplot(3, 3, 1)
    max_throughput = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max'
    }).reset_index()
    
    # Create pivot for heatmap
    throughput_pivot = max_throughput.pivot(index='config', columns='runtime', values='achieved_rps')
    sns.heatmap(throughput_pivot, annot=True, fmt='.1f', cmap='YlOrRd')
    plt.title('Maximum Throughput by Runtime and Configuration (RPS)')
    plt.ylabel('Configuration')
    
    # 2. Runtime Performance Comparison (Max Throughput)
    plt.subplot(3, 3, 2)
    runtime_max = df.groupby(['runtime']).agg({
        'achieved_rps': 'max'
    }).reset_index()
    
    bars = plt.bar(runtime_max['runtime'], runtime_max['achieved_rps'], 
                   color=[runtime_colors.get(r, '#666666') for r in runtime_max['runtime']])
    plt.title('Maximum Throughput by Runtime')
    plt.ylabel('Max RPS')
    
    # Add value labels on bars
    for bar, value in zip(bars, runtime_max['achieved_rps']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{value:.1f}', ha='center', va='bottom')
    
    # 3. Throughput vs Target RPS by Runtime
    plt.subplot(3, 3, 3)
    for runtime in ['python', 'go', 'nodejs']:
        runtime_data = df[df['runtime'] == runtime]
        if len(runtime_data) > 0:
            # Get average across all configs for each target RPS
            avg_data = runtime_data.groupby('target_rps')['achieved_rps'].mean().reset_index()
            plt.plot(avg_data['target_rps'], avg_data['achieved_rps'], 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.plot([0, 300], [0, 300], 'k--', alpha=0.5, label='Perfect Scaling')
    plt.xlabel('Target RPS')
    plt.ylabel('Achieved RPS')
    plt.title('Throughput Performance by Runtime')
    plt.legend()
    plt.grid(True)
    
    # 4. Latency Comparison at High Load
    plt.subplot(3, 3, 4)
    high_load = df[df['target_rps'] >= 200]
    if len(high_load) > 0:
        sns.boxplot(data=high_load, x='runtime', y='avg_latency_ms')
        plt.title('Average Latency at High Load (200+ RPS)')
        plt.ylabel('Average Latency (ms)')
        plt.xticks(rotation=45)
    
    # 5. P95 Latency Comparison
    plt.subplot(3, 3, 5)
    if len(high_load) > 0:
        sns.boxplot(data=high_load, x='runtime', y='p95_latency_ms')
        plt.title('P95 Latency at High Load (200+ RPS)')
        plt.ylabel('P95 Latency (ms)')
        plt.xticks(rotation=45)
    
    # 6. Runtime Efficiency (RPS per CPU)
    plt.subplot(3, 3, 6)
    efficiency_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'total_cpu_m': 'first'
    }).reset_index()
    efficiency_data['rps_per_cpu'] = efficiency_data['achieved_rps'] / efficiency_data['total_cpu_m'] * 1000
    
    sns.boxplot(data=efficiency_data, x='runtime', y='rps_per_cpu')
    plt.title('Efficiency: RPS per 1000m CPU')
    plt.ylabel('RPS per 1000m CPU')
    plt.xticks(rotation=45)
    
    # 7. Horizontal Scaling Efficiency by Runtime
    plt.subplot(3, 3, 7)
    scaling_data = df.groupby(['runtime', 'pods']).agg({
        'achieved_rps': 'max'
    }).reset_index()
    
    for runtime in ['python', 'go', 'nodejs']:
        runtime_scaling = scaling_data[scaling_data['runtime'] == runtime]
        if len(runtime_scaling) > 0:
            plt.plot(runtime_scaling['pods'], runtime_scaling['achieved_rps'], 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Number of Pods')
    plt.ylabel('Maximum RPS')
    plt.title('Horizontal Scaling Efficiency by Runtime')
    plt.legend()
    plt.grid(True)
    
    # 8. Performance Consistency (Standard Deviation)
    plt.subplot(3, 3, 8)
    consistency_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'std'
    }).reset_index()
    
    sns.boxplot(data=consistency_data, x='runtime', y='achieved_rps')
    plt.title('Performance Consistency (Lower is Better)')
    plt.ylabel('Standard Deviation of RPS')
    plt.xticks(rotation=45)
    
    # 9. Resource Utilization Comparison
    plt.subplot(3, 3, 9)
    if 'avg_cpu_percent' in df.columns:
        resource_data = df[df['target_rps'] >= 200]
        if len(resource_data) > 0:
            plt.scatter(resource_data['avg_cpu_percent'], resource_data['achieved_rps'], 
                       c=resource_data['runtime'].map(runtime_colors), 
                       s=resource_data['total_cpu_m']/10, alpha=0.6)
            plt.xlabel('CPU Utilization %')
            plt.ylabel('Achieved RPS')
            plt.title('CPU Utilization vs Performance\n(Bubble size = Total CPU)')
            
            # Add runtime labels
            for runtime in ['python', 'go', 'nodejs']:
                plt.scatter([], [], label=runtime.capitalize(), 
                          c=runtime_colors.get(runtime, '#666666'))
            plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'runtime_comparison_overview.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_detailed_runtime_analysis(df, output_dir="cross_runtime_charts"):
    """Create detailed runtime-specific analysis charts"""
    
    runtime_colors = {'python': '#377eb8', 'go': '#4daf4a', 'nodejs': '#ff7f00'}
    
    plt.figure(figsize=(20, 16))
    
    # 1. Throughput Saturation Analysis by Runtime
    plt.subplot(3, 3, 1)
    for runtime in ['python', 'go', 'nodejs']:
        runtime_data = df[df['runtime'] == runtime]
        if len(runtime_data) > 0:
            # Calculate saturation point for each config
            saturation_points = []
            for config in ['b1', 'b2', 'b3', 'b4', 'b5']:
                config_data = runtime_data[runtime_data['config'] == config]
                if len(config_data) > 0:
                    # Find where achieved RPS starts to plateau
                    saturation = config_data[config_data['achieved_rps'] < config_data['target_rps'] * 0.95]
                    if len(saturation) > 0:
                        saturation_points.append(saturation['target_rps'].min())
            
            if saturation_points:
                plt.hist(saturation_points, alpha=0.7, label=runtime.capitalize(), 
                        color=runtime_colors.get(runtime, '#666666'), bins=10)
    
    plt.xlabel('Saturation Point (Target RPS)')
    plt.ylabel('Frequency')
    plt.title('Throughput Saturation Points by Runtime')
    plt.legend()
    
    # 2. Latency Distribution at Peak Load
    plt.subplot(3, 3, 2)
    peak_data = df[df['target_rps'] == df['target_rps'].max()]
    if len(peak_data) > 0:
        sns.violinplot(data=peak_data, x='runtime', y='avg_latency_ms')
        plt.title(f'Latency Distribution at Peak Load ({peak_data["target_rps"].iloc[0]} RPS)')
        plt.ylabel('Average Latency (ms)')
        plt.xticks(rotation=45)
    
    # 3. Configuration Performance Ranking by Runtime
    plt.subplot(3, 3, 3)
    ranking_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max'
    }).reset_index()
    
    for runtime in ['python', 'go', 'nodejs']:
        runtime_ranking = ranking_data[ranking_data['runtime'] == runtime]
        if len(runtime_ranking) > 0:
            plt.plot(runtime_ranking['config'], runtime_ranking['achieved_rps'], 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Configuration')
    plt.ylabel('Maximum RPS')
    plt.title('Configuration Performance Ranking by Runtime')
    plt.legend()
    plt.grid(True)
    
    # 4. Efficiency vs Pod Count by Runtime
    plt.subplot(3, 3, 4)
    efficiency_data = df.groupby(['runtime', 'pods']).agg({
        'achieved_rps': 'max',
        'total_cpu_m': 'first'
    }).reset_index()
    efficiency_data['efficiency'] = efficiency_data['achieved_rps'] / efficiency_data['total_cpu_m'] * 1000
    
    for runtime in ['python', 'go', 'nodejs']:
        runtime_efficiency = efficiency_data[efficiency_data['runtime'] == runtime]
        if len(runtime_efficiency) > 0:
            plt.plot(runtime_efficiency['pods'], runtime_efficiency['efficiency'], 
                    marker='s', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Number of Pods')
    plt.ylabel('Efficiency (RPS per 1000m CPU)')
    plt.title('Efficiency vs Pod Count by Runtime')
    plt.legend()
    plt.grid(True)
    
    # 5. P99 Latency Comparison
    plt.subplot(3, 3, 5)
    high_load = df[df['target_rps'] >= 200]
    if len(high_load) > 0:
        sns.boxplot(data=high_load, x='runtime', y='p99_latency_ms')
        plt.title('P99 Latency at High Load (200+ RPS)')
        plt.ylabel('P99 Latency (ms)')
        plt.xticks(rotation=45)
    
    # 6. Performance Degradation Analysis
    plt.subplot(3, 3, 6)
    for runtime in ['python', 'go', 'nodejs']:
        runtime_data = df[df['runtime'] == runtime]
        if len(runtime_data) > 0:
            # Calculate performance degradation (achieved/target ratio)
            runtime_data['degradation'] = runtime_data['achieved_rps'] / runtime_data['target_rps']
            avg_degradation = runtime_data.groupby('target_rps')['degradation'].mean()
            plt.plot(avg_degradation.index, avg_degradation.values, 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Target RPS')
    plt.ylabel('Performance Ratio (Achieved/Target)')
    plt.title('Performance Degradation by Runtime')
    plt.legend()
    plt.grid(True)
    
    # 7. Memory Utilization Comparison
    plt.subplot(3, 3, 7)
    if 'avg_memory_percent' in df.columns:
        memory_data = df[df['target_rps'] >= 200]
        if len(memory_data) > 0:
            sns.boxplot(data=memory_data, x='runtime', y='avg_memory_percent')
            plt.title('Memory Utilization at High Load (200+ RPS)')
            plt.ylabel('Memory Utilization %')
            plt.xticks(rotation=45)
    
    # 8. Throughput Stability Analysis
    plt.subplot(3, 3, 8)
    stability_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': ['mean', 'std']
    }).reset_index()
    stability_data.columns = ['runtime', 'config', 'mean_rps', 'std_rps']
    stability_data['cv'] = stability_data['std_rps'] / stability_data['mean_rps']  # Coefficient of variation
    
    sns.boxplot(data=stability_data, x='runtime', y='cv')
    plt.title('Throughput Stability (Lower CV = More Stable)')
    plt.ylabel('Coefficient of Variation')
    plt.xticks(rotation=45)
    
    # 9. Overall Performance Score
    plt.subplot(3, 3, 9)
    # Calculate composite performance score
    score_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'avg_latency_ms': lambda x: x[df['target_rps'] >= 200].mean() if len(x[df['target_rps'] >= 200]) > 0 else x.mean()
    }).reset_index()
    
    # Normalize and create composite score
    max_rps = score_data['achieved_rps'].max()
    min_latency = score_data['avg_latency_ms'].min()
    score_data['performance_score'] = (score_data['achieved_rps'] / max_rps) / (score_data['avg_latency_ms'] / min_latency)
    
    sns.boxplot(data=score_data, x='runtime', y='performance_score')
    plt.title('Overall Performance Score\n(Throughput/Latency Ratio)')
    plt.ylabel('Performance Score')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'detailed_runtime_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def create_stress_test_analysis(df, output_dir="cross_runtime_charts"):
    """Create stress testing analysis charts"""
    
    runtime_colors = {'python': '#377eb8', 'go': '#4daf4a', 'nodejs': '#ff7f00'}
    
    plt.figure(figsize=(20, 12))
    
    # 1. Stress Test Performance Comparison
    plt.subplot(2, 3, 1)
    stress_data = df[df['target_rps'] >= 200]  # Focus on stress test range
    if len(stress_data) > 0:
        sns.boxplot(data=stress_data, x='runtime', y='achieved_rps')
        plt.title('Stress Test Performance (200+ Target RPS)')
        plt.ylabel('Achieved RPS')
        plt.xticks(rotation=45)
    
    # 2. Bottleneck Analysis
    plt.subplot(2, 3, 2)
    # Show how performance plateaus under stress
    for runtime in ['python', 'go', 'nodejs']:
        runtime_data = df[df['runtime'] == runtime]
        if len(runtime_data) > 0:
            max_per_config = runtime_data.groupby('config')['achieved_rps'].max()
            plt.plot(max_per_config.index, max_per_config.values, 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Configuration')
    plt.ylabel('Maximum Achieved RPS')
    plt.title('Bottleneck Analysis: Max Performance by Config')
    plt.legend()
    plt.grid(True)
    
    # 3. Concurrency Bottleneck Visualization
    plt.subplot(2, 3, 3)
    # Show how the 100 concurrent request limit affects performance
    bottleneck_data = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'concurrency': 'first'
    }).reset_index()
    
    plt.scatter(bottleneck_data['concurrency'], bottleneck_data['achieved_rps'], 
               c=bottleneck_data['runtime'].map(runtime_colors), s=100, alpha=0.7)
    plt.xlabel('Total Cluster Concurrency')
    plt.ylabel('Maximum Achieved RPS')
    plt.title('Concurrency Bottleneck Effect')
    
    # Add runtime labels
    for runtime in ['python', 'go', 'nodejs']:
        plt.scatter([], [], label=runtime.capitalize(), 
                   c=runtime_colors.get(runtime, '#666666'))
    plt.legend()
    
    # 4. Performance Degradation Under Stress
    plt.subplot(2, 3, 4)
    for runtime in ['python', 'go', 'nodejs']:
        runtime_data = df[df['runtime'] == runtime]
        if len(runtime_data) > 0:
            # Calculate efficiency loss under stress
            runtime_data['efficiency'] = runtime_data['achieved_rps'] / runtime_data['target_rps']
            avg_efficiency = runtime_data.groupby('target_rps')['efficiency'].mean()
            plt.plot(avg_efficiency.index, avg_efficiency.values, 
                    marker='o', label=runtime.capitalize(), 
                    color=runtime_colors.get(runtime, '#666666'), linewidth=2)
    
    plt.xlabel('Target RPS')
    plt.ylabel('Efficiency (Achieved/Target)')
    plt.title('Performance Degradation Under Stress')
    plt.legend()
    plt.grid(True)
    
    # 5. Resource Utilization Under Stress
    plt.subplot(2, 3, 5)
    if 'avg_cpu_percent' in df.columns:
        stress_resource = df[df['target_rps'] >= 200]
        if len(stress_resource) > 0:
            plt.scatter(stress_resource['avg_cpu_percent'], stress_resource['achieved_rps'], 
                       c=stress_resource['runtime'].map(runtime_colors), 
                       s=stress_resource['total_cpu_m']/10, alpha=0.6)
            plt.xlabel('CPU Utilization %')
            plt.ylabel('Achieved RPS')
            plt.title('Resource Utilization Under Stress\n(Bubble size = Total CPU)')
            
            # Add runtime labels
            for runtime in ['python', 'go', 'nodejs']:
                plt.scatter([], [], label=runtime.capitalize(), 
                          c=runtime_colors.get(runtime, '#666666'))
            plt.legend()
    
    # 6. Stress Test Summary
    plt.subplot(2, 3, 6)
    stress_summary = df[df['target_rps'] >= 200].groupby('runtime').agg({
        'achieved_rps': ['mean', 'std'],
        'avg_latency_ms': 'mean'
    }).reset_index()
    stress_summary.columns = ['runtime', 'mean_rps', 'std_rps', 'mean_latency']
    
    # Create a stress performance score
    stress_summary['stress_score'] = stress_summary['mean_rps'] / stress_summary['mean_latency']
    
    bars = plt.bar(stress_summary['runtime'], stress_summary['stress_score'],
                   color=[runtime_colors.get(r, '#666666') for r in stress_summary['runtime']])
    plt.title('Stress Test Performance Score\n(Throughput/Latency)')
    plt.ylabel('Performance Score')
    
    # Add value labels
    for bar, value in zip(bars, stress_summary['stress_score']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'stress_test_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_cross_runtime_report(df, output_dir="cross_runtime_charts"):
    """Generate comprehensive cross-runtime comparison report"""
    
    report_file = os.path.join(output_dir, 'cross_runtime_comparison_report.txt')
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("CROSS-RUNTIME PERFORMANCE COMPARISON REPORT\n")
        f.write("Python, Go, and Node.js Analysis Across B1-B5 Configurations\n")
        f.write("=" * 80 + "\n\n")
        
        # Runtime Summary
        f.write("RUNTIME SUMMARY\n")
        f.write("-" * 40 + "\n")
        runtimes = df['runtime'].unique()
        for runtime in runtimes:
            runtime_data = df[df['runtime'] == runtime]
            f.write(f"{runtime.upper()}: {len(runtime_data)} test results\n")
        f.write("\n")
        
        # Maximum Performance Analysis
        f.write("MAXIMUM PERFORMANCE ANALYSIS\n")
        f.write("-" * 40 + "\n")
        max_performance = df.groupby(['runtime']).agg({
            'achieved_rps': 'max',
            'avg_latency_ms': lambda x: x[df['target_rps'] >= 200].mean() if len(x[df['target_rps'] >= 200]) > 0 else x.mean()
        }).reset_index()
        
        for _, row in max_performance.iterrows():
            f.write(f"{row['runtime'].upper()}: {row['achieved_rps']:.1f} RPS max, ")
            f.write(f"{row['avg_latency_ms']:.1f}ms avg latency at high load\n")
        
        # Performance Ranking
        f.write("\n\nPERFORMANCE RANKING\n")
        f.write("-" * 40 + "\n")
        ranking = max_performance.sort_values('achieved_rps', ascending=False)
        for i, (_, row) in enumerate(ranking.iterrows(), 1):
            f.write(f"{i}. {row['runtime'].upper()}: {row['achieved_rps']:.1f} RPS\n")
        
        # Efficiency Analysis
        f.write("\n\nEFFICIENCY ANALYSIS\n")
        f.write("-" * 40 + "\n")
        efficiency_data = df.groupby(['runtime', 'config']).agg({
            'achieved_rps': 'max',
            'total_cpu_m': 'first'
        }).reset_index()
        efficiency_data['rps_per_cpu'] = efficiency_data['achieved_rps'] / efficiency_data['total_cpu_m'] * 1000
        
        runtime_efficiency = efficiency_data.groupby('runtime')['rps_per_cpu'].mean()
        for runtime, efficiency in runtime_efficiency.items():
            f.write(f"{runtime.upper()}: {efficiency:.2f} RPS per 1000m CPU\n")
        
        # Horizontal Scaling Analysis
        f.write("\n\nHORIZONTAL SCALING ANALYSIS\n")
        f.write("-" * 40 + "\n")
        scaling_data = df.groupby(['runtime', 'pods']).agg({
            'achieved_rps': 'max'
        }).reset_index()
        
        for runtime in ['python', 'go', 'nodejs']:
            runtime_scaling = scaling_data[scaling_data['runtime'] == runtime]
            if len(runtime_scaling) > 0:
                min_pods = runtime_scaling['pods'].min()
                max_pods = runtime_scaling['pods'].max()
                min_rps = runtime_scaling[runtime_scaling['pods'] == min_pods]['achieved_rps'].iloc[0]
                max_rps = runtime_scaling[runtime_scaling['pods'] == max_pods]['achieved_rps'].iloc[0]
                scaling_factor = max_rps / min_rps
                pod_factor = max_pods / min_pods
                
                f.write(f"{runtime.upper()}: {min_pods}→{max_pods} pods, ")
                f.write(f"{min_rps:.1f}→{max_rps:.1f} RPS, ")
                f.write(f"Scaling: {scaling_factor:.2f}x (vs {pod_factor:.1f}x pods)\n")
        
        # Stress Test Analysis
        f.write("\n\nSTRESS TEST ANALYSIS\n")
        f.write("-" * 40 + "\n")
        stress_data = df[df['target_rps'] >= 200]
        if len(stress_data) > 0:
            stress_summary = stress_data.groupby('runtime').agg({
                'achieved_rps': ['mean', 'std'],
                'avg_latency_ms': 'mean'
            }).reset_index()
            stress_summary.columns = ['runtime', 'mean_rps', 'std_rps', 'mean_latency']
            
            for _, row in stress_summary.iterrows():
                f.write(f"{row['runtime'].upper()}: {row['mean_rps']:.1f}±{row['std_rps']:.1f} RPS, ")
                f.write(f"{row['mean_latency']:.1f}ms avg latency\n")
        
        # Key Insights
        f.write("\n\nKEY INSIGHTS\n")
        f.write("-" * 40 + "\n")
        
        # Best performers
        best_throughput = max_performance.loc[max_performance['achieved_rps'].idxmax()]
        best_efficiency = runtime_efficiency.idxmax()
        
        f.write(f"• Best Maximum Throughput: {best_throughput['runtime'].upper()} ({best_throughput['achieved_rps']:.1f} RPS)\n")
        f.write(f"• Most Efficient: {best_efficiency.upper()} ({runtime_efficiency[best_efficiency]:.2f} RPS/1000m CPU)\n")
        
        # Performance gaps
        max_rps = max_performance['achieved_rps'].max()
        min_rps = max_performance['achieved_rps'].min()
        performance_gap = (max_rps - min_rps) / max_rps * 100
        
        f.write(f"• Performance Gap: {performance_gap:.1f}% between best and worst runtime\n")
        
        # Consistency analysis
        consistency_data = df.groupby(['runtime', 'config']).agg({
            'achieved_rps': 'std'
        }).reset_index()
        runtime_consistency = consistency_data.groupby('runtime')['achieved_rps'].mean()
        most_consistent = runtime_consistency.idxmin()
        
        f.write(f"• Most Consistent: {most_consistent.upper()} (lowest performance variance)\n")
        
        # Recommendations
        f.write("\n\nRECOMMENDATIONS\n")
        f.write("-" * 40 + "\n")
        f.write(f"• For Maximum Throughput: Use {best_throughput['runtime'].upper()}\n")
        f.write(f"• For Resource Efficiency: Use {best_efficiency.upper()}\n")
        f.write(f"• For Consistency: Use {most_consistent.upper()}\n")
        f.write("• For Stress Testing: All runtimes show similar bottleneck behavior under high concurrency\n")
    
    print(f"📊 Cross-runtime report saved to: {report_file}")

def main():
    """Main cross-runtime comparison function"""
    print("Loading cross-runtime data (Python, Go, Node.js)...")
    
    # Load all data
    df = load_all_runtime_data()
    if df.empty:
        print("❌ No runtime result directories found!")
        print("Expected directories: results_fibonacci_python_b*, results_fibonacci_go_b*, results_fibonacci_nodejs_b*")
        return
    
    print(f"✅ Found {len(df)} test results across {df['runtime'].nunique()} runtimes and {df['config'].nunique()} configurations")
    print(f"Runtimes found: {sorted(df['runtime'].unique())}")
    print(f"Configurations found: {sorted(df['config'].unique())}")
    
    # Create output directory
    output_dir = "cross_runtime_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all charts
    print("Creating runtime comparison charts...")
    create_runtime_comparison_charts(df, output_dir)
    
    print("Creating detailed runtime analysis...")
    create_detailed_runtime_analysis(df, output_dir)
    
    print("Creating stress test analysis...")
    create_stress_test_analysis(df, output_dir)
    
    # Generate comprehensive report
    print("Generating cross-runtime report...")
    generate_cross_runtime_report(df, output_dir)
    
    # Save detailed data
    summary_file = os.path.join(output_dir, 'cross_runtime_detailed_data.csv')
    df.to_csv(summary_file, index=False)
    
    print(f"\n🎉 Cross-runtime analysis complete!")
    print(f"📊 Charts saved in: {output_dir}/")
    print(f"📈 Generated charts:")
    print(f"  - runtime_comparison_overview.png")
    print(f"  - detailed_runtime_analysis.png")
    print(f"  - stress_test_analysis.png")
    print(f"📄 Report: {output_dir}/cross_runtime_comparison_report.txt")
    print(f"📊 Raw data: {output_dir}/cross_runtime_detailed_data.csv")

if __name__ == "__main__":
    main() 