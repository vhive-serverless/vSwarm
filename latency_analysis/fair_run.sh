#!/usr/bin/env bash

set -euo pipefail

# fair_run.sh - Pin CPUs, log mpstat/iostat, run run_test.py, and capture system snapshot
# Usage:
#   ./fair_run.sh --title <name> --service <svc> [--namespace default] [--cpus 2-3]
#                 [--mpstat-int 1] [--iostat-int 1] [--sudo-prompt]
#                 [--pre-wait] [--load-threshold <float>] [--max-wait <sec>] [--skip-udev] [--tame-udev]
#                 [--require-udev-pause] [--udev-pause-timeout <sec>]
# Example:
#   ./fair_run.sh --title fibonacci_python --service fibonacci-python --cpus 2-3

# Defaults
NAMESPACE="default"
CPUS=""
MPSTAT_INT=1
IOSTAT_INT=1
SUDO_PROMPT=0
PRE_WAIT=0
LOAD_THRESHOLD=""
MAX_WAIT=180
SKIP_UDEV=0
TAME_UDEV=0
REQUIRE_UDEV_PAUSE=0
UDEV_PAUSE_TIMEOUT=20

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --title) TITLE="$2"; shift 2;;
    --service) SERVICE="$2"; shift 2;;
    --namespace) NAMESPACE="$2"; shift 2;;
    --cpus) CPUS="$2"; shift 2;;
    --mpstat-int) MPSTAT_INT="$2"; shift 2;;
    --iostat-int) IOSTAT_INT="$2"; shift 2;;
    --sudo-prompt) SUDO_PROMPT=1; shift 1;;
    --pre-wait) PRE_WAIT=1; shift 1;;
    --load-threshold) LOAD_THRESHOLD="$2"; shift 2;;
    --max-wait) MAX_WAIT="$2"; shift 2;;
    --skip-udev) SKIP_UDEV=1; shift 1;;
    --tame-udev) TAME_UDEV=1; shift 1;;
    --require-udev-pause) REQUIRE_UDEV_PAUSE=1; shift 1;;
    --udev-pause-timeout) UDEV_PAUSE_TIMEOUT="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 --title <name> --service <svc> [--namespace default] [--cpus 2-3] [--mpstat-int 1] [--iostat-int 1] [--sudo-prompt] [--pre-wait] [--load-threshold <float>] [--max-wait <sec>] [--skip-udev] [--tame-udev] [--require-udev-pause] [--udev-pause-timeout <sec>]";
      exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "${TITLE:-}" || -z "${SERVICE:-}" ]]; then
  echo "Error: --title and --service are required" >&2
  exit 1
fi

# Prepare output dirs
RESULTS_DIR="results_${TITLE}"
METRICS_DIR="${RESULTS_DIR}/system_metrics"
mkdir -p "${METRICS_DIR}"
TS=$(date +%Y%m%d_%H%M%S)

# Optional sudo elevation (if password is required) and keep-alive
SUDO_KEEPALIVE_PID=""
if command -v sudo >/dev/null 2>&1 && [[ ${SUDO_PROMPT} -eq 1 ]]; then
  if ! sudo -n true >/dev/null 2>&1; then
    echo "Elevating privileges for udev pause/resume (you may be prompted)..."
    sudo -v
    # Keep sudo session alive until script exits
    ( while true; do sudo -n true; sleep 30; done ) & SUDO_KEEPALIVE_PID=$!
    trap '[[ -n "${SUDO_KEEPALIVE_PID}" ]] && kill ${SUDO_KEEPALIVE_PID} >/dev/null 2>&1 || true' EXIT
  fi
fi

# Optionally pause udev rule execution during the run (best-effort, with optional strict mode)
UDEV_PAUSED=0
if [[ ${SKIP_UDEV} -eq 1 ]]; then
  echo "Skipping udev control (--skip-udev)"
else
  if command -v udevadm >/dev/null 2>&1; then
    if sudo -n true >/dev/null 2>&1; then
      # Pre-pause: only de-prioritize to help responsiveness, but DO NOT throttle CPU yet
      if [[ ${TAME_UDEV} -eq 1 ]]; then
        for p in $(pgrep systemd-udevd || true); do
          sudo timeout 2 renice +10 -p "$p" >/dev/null 2>&1 || true
          sudo timeout 2 ionice -c3 -p "$p" >/dev/null 2>&1 || true
        done
      fi
      # Try to ensure queue is quiescent first (give more time)
      sudo timeout 20 udevadm settle >/dev/null 2>&1 || true
      echo "Pausing udev rule execution"
      if [[ ${REQUIRE_UDEV_PAUSE} -eq 1 ]]; then
        DEADLINE=$(( $(date +%s) + UDEV_PAUSE_TIMEOUT ))
        while true; do
          if sudo timeout 5 udevadm control --stop-exec-queue; then
            UDEV_PAUSED=1
            break
          fi
          [[ $(date +%s) -ge ${DEADLINE} ]] && break
          sleep 1
        done
        if [[ ${UDEV_PAUSED} -ne 1 ]]; then
          echo "Failed to pause udev within ${UDEV_PAUSE_TIMEOUT}s (--require-udev-pause set); aborting." >&2
          exit 1
        fi
      else
        if sudo timeout 5 udevadm control --stop-exec-queue; then
          UDEV_PAUSED=1
        else
          echo "udev pause skipped (daemon busy or timed out)"
        fi
      fi
      # Post-pause: now throttle and limit children to keep it quiet during the test
      if [[ ${TAME_UDEV} -eq 1 && ${UDEV_PAUSED} -eq 1 ]]; then
        sudo timeout 3 systemctl set-property --runtime systemd-udevd.service CPUAccounting=yes CPUQuota=15% || true
        sudo timeout 2 udevadm control --children-max=1 >/dev/null 2>&1 || true
      fi
    else
      echo "Skipping udev pause (sudo not available non-interactively; pass --sudo-prompt to allow it)"
    fi
  fi
fi
# Ensure we resume on any exit
trap 'if [[ "${UDEV_PAUSED}" == "1" ]]; then sudo timeout 3 udevadm control --start-exec-queue >/dev/null 2>&1 || true; fi' EXIT

# Optional pre-wait until load is below threshold
get_1min_load() {
  uptime | awk -F'load average: ' '{print $2}' | cut -d',' -f1 | tr -d ' '
}

if [[ ${PRE_WAIT} -eq 1 ]]; then
  # Compute default threshold if not provided: max(1.0, 0.8 * nproc)
  if [[ -z "${LOAD_THRESHOLD}" ]]; then
    NPROC=$(nproc 2>/dev/null || echo 1)
    LOAD_THRESHOLD=$(awk -v n="${NPROC}" 'BEGIN{t=n*0.8; if (t<1) t=1; print t;}')
  fi
  echo "Pre-wait enabled: waiting up to ${MAX_WAIT}s for 1-min load ≤ ${LOAD_THRESHOLD}"
  SECS=0
  while true; do
    L=$(get_1min_load || echo 9999)
    # If parsing fails, break to avoid infinite loop
    if [[ -z "$L" ]]; then L=9999; fi
    awk -v l="$L" -v th="$LOAD_THRESHOLD" 'BEGIN{exit !(l<=th)}'
    if [[ $? -eq 0 ]]; then
      echo "Current 1-min load ${L} ≤ ${LOAD_THRESHOLD}; proceeding"
      break
    fi
    if [[ ${SECS} -ge ${MAX_WAIT} ]]; then
      echo "Timed out waiting for load to drop (currently ${L}); proceeding anyway"
      break
    fi
    sleep 5
    SECS=$((SECS+5))
  done
fi

# Tools checks (best-effort)
command -v mpstat >/dev/null 2>&1 || echo "⚠️ mpstat not found (install sysstat)"
command -v iostat >/dev/null 2>&1 || echo "⚠️ iostat not found (install sysstat)"

# Start background telemetry
MPSTAT_OUT="${METRICS_DIR}/mpstat_${TS}.log"
IOSTAT_OUT="${METRICS_DIR}/iostat_${TS}.log"
LOAD_OUT="${METRICS_DIR}/load_${TS}.log"

echo "Starting telemetry: mpstat ${MPSTAT_INT}s, iostat ${IOSTAT_INT}s"
if command -v mpstat >/dev/null 2>&1; then
  mpstat -P ALL ${MPSTAT_INT} > "${MPSTAT_OUT}" 2>&1 &
  MPSTAT_PID=$!
else
  MPSTAT_PID=""
fi
if command -v iostat >/dev/null 2>&1; then
  iostat -xz ${IOSTAT_INT} > "${IOSTAT_OUT}" 2>&1 &
  IOSTAT_PID=$!
else
  IOSTAT_PID=""
fi

# Also sample load in background
(
  while true; do
    echo "$(date -Is) $(uptime)" >> "${LOAD_OUT}";
    sleep 5;
  done
) & LOAD_PID=$!

# Run test with optional CPU pinning
CMD=(python3 run_test.py --title "${TITLE}" --service "${SERVICE}" --namespace "${NAMESPACE}")
if [[ -n "${CPUS}" ]]; then
  echo "Running with CPU pinning: taskset -c ${CPUS} ${CMD[*]}"
  taskset -c "${CPUS}" "${CMD[@]}"
else
  echo "Running without CPU pinning: ${CMD[*]}"
  "${CMD[@]}"
fi
TEST_RC=$?

# Stop telemetry
echo "Stopping telemetry..."
[[ -n "${MPSTAT_PID}" ]] && kill ${MPSTAT_PID} >/dev/null 2>&1 || true
[[ -n "${IOSTAT_PID}" ]] && kill ${IOSTAT_PID} >/dev/null 2>&1 || true
kill ${LOAD_PID} >/dev/null 2>&1 || true

# Resume udev rule execution explicitly before snapshot
if [[ "${UDEV_PAUSED}" == "1" ]]; then
  echo "Resuming udev rule execution"
  sudo timeout 3 udevadm control --start-exec-queue >/dev/null 2>&1 || true
  UDEV_PAUSED=0
fi

# Capture a post-test system snapshot
if [[ -x ./check_system_state.sh ]]; then
  ./check_system_state.sh > "${METRICS_DIR}/post_check_${TS}.log" 2>&1 || true
else
  echo "⚠️ check_system_state.sh not found; skipping snapshot" | tee -a "${METRICS_DIR}/post_check_${TS}.log" >/dev/null
fi

echo "Telemetry saved to: ${METRICS_DIR}"
exit ${TEST_RC} 