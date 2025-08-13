#!/bin/bash

echo "System State Checker"
echo "======================"

# Check system load
echo -e "\n System Load:"
uptime

# Check memory
echo -e "\n Memory Usage:"
free -h

# Check CPU usage
echo -e "\n  Top CPU Processes:"
ps aux --sort=-%cpu | head -10

# Check Kubernetes state
echo -e "\n  Kubernetes Pods:"
kubectl get pods -A --field-selector=status.phase!=Running

# Check node resources
echo -e "\n Node Resources:"
kubectl top nodes

# Check for high CPU processes
echo -e "\n  High CPU Processes (>50%):"
ps aux | awk '$3 > 50 {print $3"%", $11}' | head -5

# Check udevd processes
UDEVD_COUNT=$(pgrep -c systemd-udevd)
echo -e "\n🔧 systemd-udevd Processes:"
echo "Count: $UDEVD_COUNT"
if [ "$UDEVD_COUNT" -gt 5 ]; then
    echo " TOO MANY UDEVD PROCESSES - Need to fix"
else
    echo " udevd processes are normal"
fi

# Check system load threshold
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
LOAD_NUM=$(echo $LOAD | sed 's/,//')

echo -e "\n Load Analysis:"
echo "Current load: $LOAD"
if (( $(echo "$LOAD_NUM > 2.0" | bc -l) )); then
    echo " HIGH LOAD DETECTED - Consider restarting system"
else
    echo " Load is acceptable"
fi

# Check available memory
AVAIL_MEM=$(free -g | awk 'NR==2{print $7}')
echo -e "\n Memory Analysis:"
echo "Available memory: ${AVAIL_MEM}GB"
if [ "$AVAIL_MEM" -lt 8 ]; then
    echo " LOW MEMORY DETECTED - Consider cleanup"
else
    echo " Memory is sufficient"
fi

echo -e "\n System check complete!" 