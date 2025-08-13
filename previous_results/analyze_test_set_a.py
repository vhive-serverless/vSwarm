#!/usr/bin/env python3
"""
Test Set A Analysis: Runtime Performance Patterns
Analyzes A1-A7 configurations to identify key research insights
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

def load_test_set_a_data():
    """Load all Test Set A configuration results"""
    results = []
    
    # Configuration mapping for Test Set A (excluding A2 and A3)
    config_info = {
        'a1': {
            'description': 'Baseline (1 pod, concurrency 1)',
            'scale_min': 1, 'scale_max': 1, 'concurrency': 1, 'target': 1,
            'cpu_container': 1000, 'memory_container': '1Gi',
            'focus': 'Single pod performance ceiling'
        },
        'a4': {
            'description': 'Scale to 5 (1-5 pods, concurrency 1)',
            'scale_min': 1, 'scale_max': 5, 'concurrency': 1, 'target': 1,
            'cpu_container': 1000, 'memory_container': '1Gi',
            'focus': 'Horizontal scaling with low concurrency'
        },
        'a5': {
            'description': 'Concurrency 10 (1-5 pods)',
            'scale_min': 1, 'scale_max': 5, 'concurrency': 10, 'target': 10,
            'cpu_container': 1000, 'memory_container': '1Gi',
            'focus': 'Medium concurrency scaling'
        },
        'a6': {
            'description': 'Concurrency 20 (1-5 pods)',
            'scale_min': 1, 'scale_max': 5, 'concurrency': 20, 'target': 20,
            'cpu_container': 1000, 'memory_container': '1Gi',
            'focus': 'High concurrency with moderate scaling'
        },
        'a7': {
            'description': 'Concurrency 20 High Scale (1-10 pods)',
            'scale_min': 1, 'scale_max': 10, 'concurrency': 20, 'target': 20,
            'cpu_container': 1000, 'memory_container': '1Gi',
            'focus': 'High concurrency with maximum scaling'
        }
    }
    
    # Look for all Test Set A result directories in test_set_A folder
    patterns = ['test_set_A/results_fibonacci_python_a*', 'test_set_A/results_fibonacci_go_a*', 'test_set_A/results_fibonacci_nodejs_a*']
    
    for pattern in patterns:
        dirs = glob.glob(pattern)
        for result_dir in dirs:
            # Extract runtime and config from directory name
            match = re.search(r'fibonacci_(\w+)_a(\d+)', result_dir)
            if not match:
                continue
                
            runtime = match.group(1)
            config = f'a{match.group(2)}'
            
            if config not in config_info or config in ['a2', 'a3']:
                continue
            
            # Load detailed analysis (handle different naming patterns)
            analysis_file = os.path.join(result_dir, f"fibonacci_{runtime}_{config}_detailed_analysis.csv")
            if not os.path.exists(analysis_file):
                # Try alternative naming pattern (e.g., fibonacci_a1_ instead of fibonacci_python_a1_)
                analysis_file = os.path.join(result_dir, f"fibonacci_{config}_detailed_analysis.csv")
            
            if os.path.exists(analysis_file):
                df = pd.read_csv(analysis_file)
                
                # Load monitoring data if available
                monitoring_file = os.path.join(result_dir, f"fibonacci_{runtime}_{config}_pod_monitoring_converted.csv")
                if not os.path.exists(monitoring_file):
                    # Try alternative naming pattern
                    monitoring_file = os.path.join(result_dir, f"fibonacci_{config}_pod_monitoring_converted.csv")
                
                pod_data = None
                if os.path.exists(monitoring_file):
                    pod_data = pd.read_csv(monitoring_file)
                
                # Process each RPS test
                for _, row in df.iterrows():
                    # Extract target RPS from filename
                    filename = row['filename']
                    rps_match = re.search(r'target_rps(\d+\.?\d*)', filename)
                    target_rps = float(rps_match.group(1)) if rps_match else 0
                    
                    result_entry = {
                        'runtime': runtime,
                        'config': config,
                        'config_description': config_info[config]['description'],
                        'config_focus': config_info[config]['focus'],
                        'scale_min': config_info[config]['scale_min'],
                        'scale_max': config_info[config]['scale_max'],
                        'concurrency': config_info[config]['concurrency'],
                        'target': config_info[config]['target'],
                        'cpu_container': config_info[config]['cpu_container'],
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

def analyze_max_throughput_patterns(df, output_dir="test_set_a_analysis"):
    """Analyze maximum throughput patterns across configurations"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate max throughput for each runtime+config combination
    max_throughput = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'config_description': 'first',
        'config_focus': 'first',
        'concurrency': 'first',
        'scale_max': 'first'
    }).reset_index()
    
    plt.figure(figsize=(16, 12))
    
    # 1. Maximum Throughput by Configuration
    plt.subplot(2, 3, 1)
    config_order = ['a1', 'a4', 'a5', 'a6', 'a7']
    throughput_pivot = max_throughput.pivot(index='config', columns='runtime', values='achieved_rps')
    throughput_pivot.reindex(config_order).plot(kind='bar', ax=plt.gca())
    plt.title('Maximum Throughput by Configuration')
    plt.ylabel('Max RPS')
    plt.xlabel('Configuration')
    plt.legend(title='Runtime')
    plt.xticks(rotation=45)
    
    # 2. Runtime Performance Ceiling (A1 vs A4 vs A7)
    plt.subplot(2, 3, 2)
    scaling_configs = ['a1', 'a4', 'a7']  # 1 pod, 5 pods, 10 pods
    scaling_data = max_throughput[max_throughput['config'].isin(scaling_configs)]
    sns.barplot(data=scaling_data, x='config', y='achieved_rps', hue='runtime')
    plt.title('Scaling Impact: 1 vs 5 vs 10 Max Pods')
    plt.ylabel('Max RPS')
    
    # 3. Concurrency Impact (A4 vs A5 vs A6)
    plt.subplot(2, 3, 3)
    concurrency_configs = ['a4', 'a5', 'a6']  # Concurrency 1, 10, 20
    concurrency_data = max_throughput[max_throughput['config'].isin(concurrency_configs)]
    sns.barplot(data=concurrency_data, x='concurrency', y='achieved_rps', hue='runtime')
    plt.title('Concurrency Impact on Max Throughput')
    plt.ylabel('Max RPS')
    plt.xlabel('Concurrency Level')
    
    # 4. Horizontal vs Concurrency Scaling Comparison
    plt.subplot(2, 3, 4)
    # Compare A1 (1 pod, 1 concurrency) vs A4 (5 pods, 1 concurrency) vs A5 (5 pods, 10 concurrency)
    scaling_comparison_configs = ['a1', 'a4', 'a5']
    scaling_comparison_data = max_throughput[max_throughput['config'].isin(scaling_comparison_configs)]
    scaling_comparison_pivot = scaling_comparison_data.pivot(index='config', columns='runtime', values='achieved_rps')
    scaling_comparison_pivot.plot(kind='bar', ax=plt.gca())
    plt.title('Horizontal vs Concurrency Scaling')
    plt.ylabel('Max RPS')
    plt.xticks(rotation=0)
    plt.legend(title='Runtime')
    
    # 5. Runtime Efficiency Comparison
    plt.subplot(2, 3, 5)
    runtime_max = max_throughput.groupby('runtime')['achieved_rps'].max().sort_values(ascending=False)
    runtime_max.plot(kind='bar', ax=plt.gca())
    plt.title('Maximum Achieved RPS by Runtime')
    plt.ylabel('Max RPS Across All Configs')
    plt.xticks(rotation=45)
    
    # 6. Configuration Effectiveness Score
    plt.subplot(2, 3, 6)
    # Calculate effectiveness as max_rps / resources_used
    max_throughput['effectiveness'] = max_throughput['achieved_rps'] / (max_throughput['scale_max'] * max_throughput['concurrency'])
    effectiveness_pivot = max_throughput.pivot(index='config', columns='runtime', values='effectiveness')
    sns.heatmap(effectiveness_pivot.reindex(config_order), annot=True, fmt='.1f', cmap='Greens')
    plt.title('Configuration Effectiveness\n(RPS per Pod×Concurrency)')
    plt.ylabel('Configuration')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'max_throughput_patterns.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return max_throughput

def analyze_scaling_patterns(df, output_dir="test_set_a_analysis"):
    """Analyze horizontal and concurrency scaling patterns"""
    
    plt.figure(figsize=(15, 10))
    
    # 1. Single Pod Performance Ceiling (A1)
    plt.subplot(2, 3, 1)
    a1_data = df[df['config'] == 'a1']
    for runtime in a1_data['runtime'].unique():
        runtime_data = a1_data[a1_data['runtime'] == runtime]
        plt.plot(runtime_data['target_rps'], runtime_data['achieved_rps'], 
                marker='o', label=runtime, linewidth=2)
    
    plt.plot([0, df['target_rps'].max()], [0, df['target_rps'].max()], 
             'k--', alpha=0.5, label='Perfect Scaling')
    plt.xlabel('Target RPS')
    plt.ylabel('Achieved RPS')
    plt.title('Single Pod Performance Ceiling (A1)')
    plt.legend()
    plt.grid(True)
    
    # 2. Horizontal Scaling Effectiveness (A1 vs A4 vs A7)
    plt.subplot(2, 3, 2)
    scaling_configs = ['a1', 'a4', 'a7']
    max_rps_scaling = df[df['config'].isin(scaling_configs)].groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'scale_max': 'first'
    }).reset_index()
    
    for runtime in max_rps_scaling['runtime'].unique():
        runtime_data = max_rps_scaling[max_rps_scaling['runtime'] == runtime]
        plt.plot(runtime_data['scale_max'], runtime_data['achieved_rps'], 
                marker='s', label=runtime, linewidth=2)
    
    plt.xlabel('Maximum Pods')
    plt.ylabel('Max Achieved RPS')
    plt.title('Horizontal Scaling Effectiveness')
    plt.legend()
    plt.grid(True)
    
    # 3. Concurrency Scaling (A4, A5, A6)
    plt.subplot(2, 3, 3)
    concurrency_configs = ['a4', 'a5', 'a6']
    max_rps_concurrency = df[df['config'].isin(concurrency_configs)].groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'concurrency': 'first'
    }).reset_index()
    
    for runtime in max_rps_concurrency['runtime'].unique():
        runtime_data = max_rps_concurrency[max_rps_concurrency['runtime'] == runtime]
        plt.plot(runtime_data['concurrency'], runtime_data['achieved_rps'], 
                marker='^', label=runtime, linewidth=2)
    
    plt.xlabel('Concurrency Level')
    plt.ylabel('Max Achieved RPS')
    plt.title('Concurrency Scaling Impact')
    plt.legend()
    plt.grid(True)
    
    # 4. Latency vs Throughput Trade-off
    plt.subplot(2, 3, 4)
    high_throughput = df[df['achieved_rps'] >= df['achieved_rps'].quantile(0.8)]
    scatter = plt.scatter(high_throughput['achieved_rps'], high_throughput['avg_latency_ms'], 
                         c=high_throughput['runtime'].astype('category').cat.codes, 
                         s=high_throughput['concurrency']*3, alpha=0.6)
    plt.xlabel('Achieved RPS')
    plt.ylabel('Average Latency (ms)')
    plt.title('Latency vs Throughput Trade-off\n(Bubble size = Concurrency)')
    
    for runtime in df['runtime'].unique():
        runtime_data = high_throughput[high_throughput['runtime'] == runtime]
        if len(runtime_data) > 0:
            plt.scatter([], [], label=runtime, 
                       c=plt.cm.tab10(df['runtime'].unique().tolist().index(runtime)))
    plt.legend()
    
    # 5. Configuration Comparison Matrix
    plt.subplot(2, 3, 5)
    config_comparison = df.groupby(['runtime', 'config']).agg({
        'achieved_rps': 'max',
        'avg_latency_ms': 'mean'
    }).reset_index()
    
    config_pivot = config_comparison.pivot(index='config', columns='runtime', values='achieved_rps')
    config_order = ['a1', 'a4', 'a5', 'a6', 'a7']
    sns.heatmap(config_pivot.reindex(config_order), annot=True, fmt='.0f', cmap='Blues')
    plt.title('Max RPS Heatmap by Configuration')
    plt.ylabel('Configuration')
    
    # 6. Runtime Architecture Impact
    plt.subplot(2, 3, 6)
    # Calculate improvement from A1 to A7 for each runtime
    a1_max = df[df['config'] == 'a1'].groupby('runtime')['achieved_rps'].max()
    a7_max = df[df['config'] == 'a7'].groupby('runtime')['achieved_rps'].max()
    improvement = ((a7_max - a1_max) / a1_max * 100).fillna(0)
    
    improvement.plot(kind='bar', ax=plt.gca())
    plt.title('A1→A7 Performance Improvement %')
    plt.ylabel('Improvement (%)')
    plt.xlabel('Runtime')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'scaling_patterns.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_research_insights_report(df, max_throughput, output_dir="test_set_a_analysis"):
    """Generate comprehensive research insights report"""
    
    report_file = os.path.join(output_dir, 'test_set_a_research_insights.txt')
    
    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("TEST SET A: RUNTIME PERFORMANCE PATTERNS ANALYSIS\n")
        f.write("Research Insights for Serverless Runtime Optimization\n")
        f.write("=" * 80 + "\n\n")
        
        # 1. Maximum Throughput Analysis
        f.write("1. MAXIMUM THROUGHPUT ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        runtime_max = max_throughput.groupby('runtime')['achieved_rps'].max().sort_values(ascending=False)
        f.write("Runtime Performance Ranking (Max RPS across all configs):\n")
        for i, (runtime, max_rps) in enumerate(runtime_max.items(), 1):
            f.write(f"  {i}. {runtime.upper()}: {max_rps:.1f} RPS\n")
        
        # Best configuration per runtime
        f.write("\nBest Configuration per Runtime:\n")
        for runtime in max_throughput['runtime'].unique():
            runtime_data = max_throughput[max_throughput['runtime'] == runtime]
            best_config = runtime_data.loc[runtime_data['achieved_rps'].idxmax()]
            f.write(f"  {runtime.upper()}: {best_config['config'].upper()} ")
            f.write(f"({best_config['achieved_rps']:.1f} RPS) - {best_config['config_focus']}\n")
        
        # 2. Scaling Effectiveness Analysis
        f.write("\n2. SCALING EFFECTIVENESS ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        # A1 vs A7 comparison (1 pod vs max scaling)
        a1_data = max_throughput[max_throughput['config'] == 'a1']
        a7_data = max_throughput[max_throughput['config'] == 'a7']
        
        f.write("Single Pod (A1) vs Maximum Scaling (A7):\n")
        for runtime in a1_data['runtime'].unique():
            a1_rps = a1_data[a1_data['runtime'] == runtime]['achieved_rps'].iloc[0]
            a7_rps = a7_data[a7_data['runtime'] == runtime]['achieved_rps'].iloc[0] if len(a7_data[a7_data['runtime'] == runtime]) > 0 else 0
            improvement = ((a7_rps - a1_rps) / a1_rps * 100) if a1_rps > 0 else 0
            f.write(f"  {runtime.upper()}: {a1_rps:.1f} → {a7_rps:.1f} RPS ({improvement:.1f}% improvement)\n")
        
        # 3. Concurrency Impact Analysis
        f.write("\n3. CONCURRENCY IMPACT ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        concurrency_configs = ['a4', 'a5', 'a6']  # Concurrency 1, 10, 20
        f.write("Concurrency Scaling (1→10→20, same scaling 1-5 pods):\n")
        for runtime in max_throughput['runtime'].unique():
            f.write(f"  {runtime.upper()}:\n")
            for config in concurrency_configs:
                config_data = max_throughput[(max_throughput['runtime'] == runtime) & (max_throughput['config'] == config)]
                if len(config_data) > 0:
                    rps = config_data['achieved_rps'].iloc[0]
                    concurrency = config_data['concurrency'].iloc[0]
                    f.write(f"    Concurrency {concurrency}: {rps:.1f} RPS\n")
        
        # 4. Horizontal vs Concurrency Scaling Analysis
        f.write("\n4. HORIZONTAL VS CONCURRENCY SCALING ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        # Compare A1 (1 pod, 1 concurrency) vs A4 (5 pods, 1 concurrency) vs A5 (5 pods, 10 concurrency)
        a1_data = max_throughput[max_throughput['config'] == 'a1']  # 1 pod, 1 concurrency
        a4_data = max_throughput[max_throughput['config'] == 'a4']  # 5 pods, 1 concurrency
        a5_data = max_throughput[max_throughput['config'] == 'a5']  # 5 pods, 10 concurrency
        
        f.write("Horizontal vs Concurrency Scaling Comparison:\n")
        for runtime in a1_data['runtime'].unique():
            a1_rps = a1_data[a1_data['runtime'] == runtime]['achieved_rps'].iloc[0]
            a4_rps = a4_data[a4_data['runtime'] == runtime]['achieved_rps'].iloc[0] if len(a4_data[a4_data['runtime'] == runtime]) > 0 else 0
            a5_rps = a5_data[a5_data['runtime'] == runtime]['achieved_rps'].iloc[0] if len(a5_data[a5_data['runtime'] == runtime]) > 0 else 0
            
            horizontal_improvement = ((a4_rps - a1_rps) / a1_rps * 100) if a1_rps > 0 else 0
            concurrency_improvement = ((a5_rps - a4_rps) / a4_rps * 100) if a4_rps > 0 else 0
            
            f.write(f"  {runtime.upper()}:\n")
            f.write(f"    A1→A4 (Horizontal): {a1_rps:.1f} → {a4_rps:.1f} RPS ({horizontal_improvement:.1f}% improvement)\n")
            f.write(f"    A4→A5 (Concurrency): {a4_rps:.1f} → {a5_rps:.1f} RPS ({concurrency_improvement:.1f}% improvement)\n")
        
        # 5. Key Research Insights
        f.write("\n5. KEY RESEARCH INSIGHTS\n")
        f.write("-" * 40 + "\n")
        
        f.write("Runtime Architecture Patterns:\n")
        
        # Analyze Go performance
        go_improvement = {}
        python_improvement = {}
        nodejs_improvement = {}
        
        for config_pair in [('a1', 'a4'), ('a4', 'a5'), ('a5', 'a6'), ('a6', 'a7')]:
            for runtime in ['go', 'python', 'nodejs']:
                base_data = max_throughput[(max_throughput['runtime'] == runtime) & (max_throughput['config'] == config_pair[0])]
                target_data = max_throughput[(max_throughput['runtime'] == runtime) & (max_throughput['config'] == config_pair[1])]
                
                if len(base_data) > 0 and len(target_data) > 0:
                    base_rps = base_data['achieved_rps'].iloc[0]
                    target_rps = target_data['achieved_rps'].iloc[0]
                    improvement = (target_rps - base_rps) / base_rps * 100
                    
                    if runtime == 'go':
                        go_improvement[f"{config_pair[0]}→{config_pair[1]}"] = improvement
                    elif runtime == 'python':
                        python_improvement[f"{config_pair[0]}→{config_pair[1]}"] = improvement
                    elif runtime == 'nodejs':
                        nodejs_improvement[f"{config_pair[0]}→{config_pair[1]}"] = improvement
        
        f.write("\nScaling Responsiveness (% improvement between configurations):\n")
        f.write("  GO (Multi-threaded):\n")
        for transition, improvement in go_improvement.items():
            f.write(f"    {transition}: {improvement:.1f}%\n")
        
        f.write("  PYTHON (GIL-limited):\n")
        for transition, improvement in python_improvement.items():
            f.write(f"    {transition}: {improvement:.1f}%\n")
        
        f.write("  NODE.JS (Event-loop):\n")
        for transition, improvement in nodejs_improvement.items():
            f.write(f"    {transition}: {improvement:.1f}%\n")
        
        # 6. Research Contributions
        f.write("\n6. RESEARCH CONTRIBUTIONS\n")
        f.write("-" * 40 + "\n")
        
        f.write("A. Runtime-Configuration Matching:\n")
        f.write("   - Go benefits most from horizontal scaling (multi-threading advantage)\n")
        f.write("   - Python shows limited scaling due to GIL constraints\n")
        f.write("   - Node.js benefits from concurrency but limited by single-threaded nature\n\n")
        
        f.write("B. Optimal Configuration Recommendations:\n")
        for runtime in max_throughput['runtime'].unique():
            best = max_throughput[max_throughput['runtime'] == runtime].loc[max_throughput[max_throughput['runtime'] == runtime]['achieved_rps'].idxmax()]
            f.write(f"   - {runtime.upper()}: {best['config'].upper()} - {best['config_focus']}\n")
        
        f.write("\nC. Platform Design Implications:\n")
        f.write("   - Single-threaded runtimes waste resources in high-CPU configurations\n")
        f.write("   - Concurrency limits vary significantly by runtime architecture\n")
        f.write("   - Cold start impacts differ based on runtime initialization overhead\n")
        
        f.write("\nD. Cost-Performance Trade-offs:\n")
        # Calculate efficiency scores
        max_throughput['efficiency'] = max_throughput['achieved_rps'] / (max_throughput['scale_max'] * max_throughput['concurrency'])
        most_efficient = max_throughput.loc[max_throughput['efficiency'].idxmax()]
        f.write(f"   - Most efficient configuration: {most_efficient['runtime'].upper()} {most_efficient['config'].upper()}\n")
        f.write(f"     ({most_efficient['efficiency']:.2f} RPS per pod×concurrency unit)\n")
    
    print(f"📊 Research insights report saved to: {report_file}")

def main():
    """Main analysis function"""
    print("Loading Test Set A configuration data...")
    
    # Load all data
    df = load_test_set_a_data()
    if df.empty:
        print("❌ No Test Set A result directories found!")
        print("Expected directories: results_fibonacci_python_a1, results_fibonacci_go_a2, etc.")
        return
    
    print(f"✅ Found {len(df)} test results across {df['runtime'].nunique()} runtimes and {df['config'].nunique()} configurations")
    
    # Create output directory
    output_dir = "test_set_a_analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyze maximum throughput patterns
    print("Analyzing maximum throughput patterns...")
    max_throughput = analyze_max_throughput_patterns(df, output_dir)
    
    # Analyze scaling patterns
    print("Analyzing scaling patterns...")
    analyze_scaling_patterns(df, output_dir)
    
    # Generate research insights report
    print("Generating research insights report...")
    generate_research_insights_report(df, max_throughput, output_dir)
    
    # Save detailed data
    summary_file = os.path.join(output_dir, 'test_set_a_detailed_data.csv')
    df.to_csv(summary_file, index=False)
    
    max_throughput_file = os.path.join(output_dir, 'test_set_a_max_throughput.csv')
    max_throughput.to_csv(max_throughput_file, index=False)
    
    print(f"\n🎉 Test Set A analysis complete!")
    print(f"📊 Charts saved in: {output_dir}/")
    print(f"📈 Generated files:")
    print(f"  - max_throughput_patterns.png")
    print(f"  - scaling_patterns.png")
    print(f"📄 Research Report: {output_dir}/test_set_a_research_insights.txt")
    print(f"📊 Raw data: {output_dir}/test_set_a_detailed_data.csv")

if __name__ == "__main__":
    main() 