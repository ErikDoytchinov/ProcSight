#!/usr/bin/env bash
set -euo pipefail

# Simple self-contained workload to test ProcSight.
# Generates CPU, memory, and disk I/O within a single process (via embedded Python).
#
# Usage:
#   ./scripts/stress.sh [-d <seconds>] [-m <mem_mb>] [-i <io_mb_per_iter>]
# Defaults: duration=30s, mem_mb=256, io_mb_per_iter=64
#
# After starting, this script prints the worker PID that you can monitor with ProcSight.
# Example:
#   pid=$(./scripts/stress.sh -d 60 -m 512 -i 128 &>/dev/stdout | sed -n 's/^PID=//p' | tail -1)
#   procsight --pid "$pid" --samples 120 --save-plots ./plots --no-show

DURATION=30
MEM_MB=256
IO_MB=64

while getopts ":d:m:i:h" opt; do
  case "$opt" in
    d) DURATION="$OPTARG" ;;
    m) MEM_MB="$OPTARG" ;;
    i) IO_MB="$OPTARG" ;;
    h)
      echo "Usage: $0 [-d seconds] [-m mem_mb] [-i io_mb_per_iter]";
      exit 0;
      ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 2 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; exit 2 ;;
  esac
done

# Ensure python3 exists
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH" >&2
  exit 1
fi

# Run a single Python worker to concentrate CPU, memory, and I/O in one PID.
# IMPORTANT: pass parameters via environment to the Python process (must be set BEFORE launching).
STRESS_DURATION="$DURATION" STRESS_MEM_MB="$MEM_MB" STRESS_IO_MB="$IO_MB" \
python3 - <<'PY' &
import os, time, tempfile, hashlib, sys

# Parameters passed via environment variables from bash
DURATION = int(os.environ.get('STRESS_DURATION', '30'))
MEM_MB = int(os.environ.get('STRESS_MEM_MB', '256'))
IO_MB = int(os.environ.get('STRESS_IO_MB', '64'))

# We purposefully do NOT print the PID here to avoid duplicate/confusing outputs.

# Allocate memory
buf = bytearray(MEM_MB * 1024 * 1024)

# Prepare temp file for I/O
fd, path = tempfile.mkstemp(prefix='procsight_stress_', suffix='.bin')
os.close(fd)

end = time.time() + DURATION
try:
    with open(path, 'wb+', buffering=0) as f:
        while time.time() < end:
            # CPU: hash the buffer a few times
            h = hashlib.sha256(buf).digest()
            h = hashlib.sha256(h).digest()
            
            # I/O: write IO_MB MB of zeros, fsync, then rewind
            size = IO_MB * 1024 * 1024
            chunk = b"\0" * (1024 * 1024)
            written = 0
            while written < size:
                f.write(chunk)
                written += len(chunk)
            f.flush()
            os.fsync(f.fileno())
            f.seek(0)

            # small sleep to vary scheduling
            time.sleep(0.05)
finally:
    try:
        os.remove(path)
    except Exception:
        pass
PY
child_pid=$!

# Wait a moment for the Python process to start and print its PID
sleep 0.2

# Canonical output for ProcSight: a single unambiguous PID line
echo "PID=$child_pid"
echo "[stress] started python worker pid=$child_pid (duration=${DURATION}s, mem=${MEM_MB}MB, io_iter=${IO_MB}MB)"

# Forward Ctrl+C and ensure cleanup
term() { kill -TERM "$child_pid" 2>/dev/null || true; }
trap term INT TERM

wait "$child_pid"
