#!/bin/bash
# Check CPU Utilization Test Status

echo "=== CPU Utilization Test Status ==="
echo

# Check if test result directories exist
echo "1. Test Result Directories:"
echo "----------------------------------------"
for config in c1 c2 c3 c4 c5 c6 c7 c8 c9; do
    pattern="results_fibonacci_*_${config}"
    count=$(ls -d ${pattern} 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ Configuration ${config}: Found $(ls -d ${pattern} 2>/dev/null | tr '\n' ' ')"
    else
        echo "❌ Configuration ${config}: Not found"
    fi
done

echo
echo "2. Service Configurations:"
echo "----------------------------------------"
# Check current Knative service configurations
kubectl get ksvc fibonacci-python -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null && echo " <- Python resources"
kubectl get ksvc fibonacci-nodejs -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null && echo " <- Node.js resources"  
kubectl get ksvc fibonacci-go -o jsonpath='{.spec.template.spec.containers[0].resources}' 2>/dev/null && echo " <- Go resources"

echo
echo "3. Current Concurrency Settings:"
echo "----------------------------------------"
kubectl get ksvc fibonacci-python -o jsonpath='{.spec.template.metadata.annotations.autoscaling\.knative\.dev/target}' 2>/dev/null && echo " <- Python concurrency"
kubectl get ksvc fibonacci-nodejs -o jsonpath='{.spec.template.metadata.annotations.autoscaling\.knative\.dev/target}' 2>/dev/null && echo " <- Node.js concurrency"
kubectl get ksvc fibonacci-go -o jsonpath='{.spec.template.metadata.annotations.autoscaling\.knative\.dev/target}' 2>/dev/null && echo " <- Go concurrency"

echo
echo "4. Pod Status:"
echo "----------------------------------------"
kubectl get pods | grep fibonacci

echo
echo "5. Quick Performance Preview (if results exist):"
echo "----------------------------------------"
for result_dir in results_fibonacci_*_c*; do
    if [ -d "$result_dir" ]; then
        analysis_file="${result_dir}/${result_dir}_detailed_analysis.csv"
        if [ -f "$analysis_file" ]; then
            runtime=$(echo $result_dir | sed 's/results_fibonacci_\([^_]*\)_c\([0-9]*\)/\1/')
            config=$(echo $result_dir | sed 's/results_fibonacci_\([^_]*\)_c\([0-9]*\)/\2/')
            max_rps=$(tail -n +2 "$analysis_file" | cut -d',' -f9 | sort -n | tail -1)
            echo "${runtime} C${config}: ${max_rps} max RPS"
        fi
    fi
done

echo
echo "=== Next Steps ==="
echo "Once all tests complete, run:"
echo "  cd ~/vswarm/latency_analysis"
echo "  python3 analyze_cpu_utilization.py" 