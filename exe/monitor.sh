#!/bin/bash

# RUN THIS SCRIPT WITH SUDO
# Concise 2-Minute Torrent Performance Monitor

LOGFILE="torrent_monitor_$(date +%Y%m%d_%H%M%S).log"
DURATION=120  # seconds
INTERVAL=10   # sample every 10 seconds

echo "Starting 2-minute torrent monitoring..."
echo "Output file: $LOGFILE"

log_section() {
    echo "" >> "$LOGFILE"
    echo "====== $1 - $(date '+%H:%M:%S') ======" >> "$LOGFILE"
}

{
    echo "TORRENT MONITORING SESSION - $(date)"
    echo "Duration: ${DURATION}s | Interval: ${INTERVAL}s"
    echo "========================================"
    echo ""
    echo "=== SYSTEM INFO ==="
    echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "Load: $(uptime)"
    echo "Disk Space: $(df -h / | tail -1 | awk '{print $4 " free"}')"
    echo "Containers: $(docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -v NAMES)"
} > "$LOGFILE"

for i in $(seq 0 $((DURATION/INTERVAL))); do
    TIMESTAMP=$(date '+%H:%M:%S')

    echo "Progress: $((i*INTERVAL))/${DURATION}s"

    {
        log_section "SAMPLE $((i+1)) at $TIMESTAMP"

        echo "LOAD: $(cat /proc/loadavg)"
        echo "CPU%: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"

        echo "MEM: $(free | grep Mem | awk '{printf "Used: %.1fGB/%.1fGB (%.0f%%)", $3/1024/1024, $2/1024/1024, $3*100/$2}')"

        echo "CONTAINER: $(docker stats --no-stream --format '{{.Container}}: CPU {{.CPUPerc}} | MEM {{.MemUsage}}' 2>/dev/null)"

        CONNECTIONS=$(netstat -an 2>/dev/null | grep :6881 | wc -l)
        STATES=$(netstat -an 2>/dev/null | grep :6881 | awk '{print $6}' | sort | uniq -c | tr '\n' ' ')
        echo "NET: $CONNECTIONS connections | States: $STATES"

        DISK_IO=$(iostat -x 1 1 2>/dev/null | tail -1 | awk '{printf "r/s:%.0f w/s:%.0f util:%.0f%%", $4, $5, $10}')
        echo "DISK: $DISK_IO"

        TOTAL_FDS=$(lsof 2>/dev/null | wc -l)
        RTORRENT_PID=$(docker exec rtorrent pgrep rtorrent 2>/dev/null)
        if [ ! -z "$RTORRENT_PID" ]; then
            RTORRENT_FDS=$(docker exec rtorrent sh -c "ls /proc/$RTORRENT_PID/fd 2>/dev/null | wc -l")
            echo "FDS: Total:$TOTAL_FDS | rtorrent:$RTORRENT_FDS"
        else
            echo "FDS: Total:$TOTAL_FDS | rtorrent:N/A"
        fi

        TEMP=$(sensors 2>/dev/null | grep -i "core 0" | awk '{print $3}' | head -1)
        if [ ! -z "$TEMP" ]; then
            echo "TEMP: $TEMP"
        fi

        ERRORS=$(dmesg | tail -5 | grep -i error | wc -l)
        echo "ERRORS: $ERRORS recent kernel errors"

    } >> "$LOGFILE"

    if [ $i -lt $((DURATION/INTERVAL)) ]; then
        sleep $INTERVAL
    fi
done

{
    log_section "FINAL SUMMARY"
    echo "Monitoring completed at $(date)"
    echo "Final system state:"
    echo "LOAD: $(cat /proc/loadavg)"
    echo "MEM: $(free | grep Mem | awk '{printf "%.1fGB used of %.1fGB", $3/1024/1024, $2/1024/1024}')"
    echo "SWAP: $(free | grep Swap | awk '{if($2>0) printf "%.1fGB used of %.1fGB", $3/1024/1024, $2/1024/1024; else print "No swap"}')"
    echo "CONNECTIONS: $(netstat -an 2>/dev/null | grep :6881 | wc -l) active"
    echo "CONTAINERS: $(docker ps --format '{{.Names}}: {{.Status}}' | tr '\n' ' ')"

    echo ""
    echo "=== PERFORMANCE ASSESSMENT ==="
    FINAL_LOAD=$(cat /proc/loadavg | awk '{print $1}')
    if (( $(echo "$FINAL_LOAD < 2.0" | bc -l) )); then
        echo "CPU: GOOD (load: $FINAL_LOAD)"
    elif (( $(echo "$FINAL_LOAD < 4.0" | bc -l) )); then
        echo "CPU: MODERATE (load: $FINAL_LOAD)"
    else
        echo "CPU: HIGH (load: $FINAL_LOAD)"
    fi

    MEM_PERCENT=$(free | grep Mem | awk '{print $3*100/$2}')
    if (( $(echo "$MEM_PERCENT < 70" | bc -l) )); then
        echo "MEMORY: GOOD (${MEM_PERCENT}% used)"
    elif (( $(echo "$MEM_PERCENT < 85" | bc -l) )); then
        echo "MEMORY: MODERATE (${MEM_PERCENT}% used)"
    else
        echo "MEMORY: HIGH (${MEM_PERCENT}% used)"
    fi

    echo ""
    echo "Log file: $LOGFILE"
    echo "File size: $(du -h "$LOGFILE" | cut -f1)"

} >> "$LOGFILE"

echo ""
echo "Monitoring complete!"
echo "Results saved to: $LOGFILE"
echo "File size: $(du -h "$LOGFILE" | cut -f1)"
echo ""
echo "To share the results, just send the file: $LOGFILE"
