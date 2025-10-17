#!/bin/bash

################################################################################
# ping-test-multiple.sh
#
# Parallel multi-UE ping tester that validates connectivity across all simulated
# UE interfaces in the deployed UERANSIM pods.
#
# This script:
#   1. Discovers all UE pods in the specified namespace
#   2. Identifies all uesimtun* interfaces within each pod
#   3. Runs parallel ping tests from each interface to a target host
#   4. Provides per-pod and global summaries with success/failure statistics
#
# Environment Variables (optional):
#   NAMESPACE            - Kubernetes namespace (default: open5gs)
#   POD_SELECTOR_SUBSTR  - Pod name pattern to match (default: ueransim-ue)
#   TARGET               - Ping target host (default: www.google.ca)
#   COUNT                - Number of pings per test (default: 3)
#   TIMEOUT              - Ping timeout per request in seconds (default: 2)
#   IP_FAMILY            - IP version: 4 or 6 (default: 4)
#   REQUEST_TIMEOUT      - kubectl exec timeout (default: 5s)
#   JOBS                 - Max concurrent ping jobs (default: 16)
#   DEBUG                - Enable debug output: 0 or 1 (default: 0)
#
# Usage:
#   ./ping-test-multiple.sh
#   TARGET=8.8.8.8 COUNT=5 ./ping-test-multiple.sh
#   DEBUG=1 JOBS=32 ./ping-test-multiple.sh
#
################################################################################

# Function to print in color for better visibility
print_header() {
    echo -e "\n\e[1;34m############################### $1 ###############################\e[0m"
}

print_success() {
    echo -e "\e[1;32m$1\e[0m"
}

print_error() {
    echo -e "\e[1;31mERROR: $1\e[0m"
}

print_subheader() {
    echo -e "\e[1;36m--- $1 ---\e[0m"
}

print_warning() {
    echo -e "\e[1;33m$1\e[0m"
}

debug_log() {
    [[ "$DEBUG" == "1" ]] && echo -e "\e[2m[DEBUG]\e[0m $*"
}

# ===================== Configuration =====================
NAMESPACE="${NAMESPACE:-open5gs}"
POD_SELECTOR_SUBSTR="${POD_SELECTOR_SUBSTR:-ueransim-ue}"
TARGET="${TARGET:-www.google.ca}"
COUNT="${COUNT:-3}"
TIMEOUT="${TIMEOUT:-2}"           # ping per-request timeout (seconds)
IP_FAMILY="${IP_FAMILY:-4}"       # 4 or 6
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-5s}"  # kubectl exec timeout
DEBUG="${DEBUG:-0}"
JOBS="${JOBS:-16}"                # max concurrent pings across all pods+ifaces
# ========================================================

# -------------------- Discover UE Pods --------------------
print_header "Multi-UE Connectivity Test"
print_subheader "Scanning namespace '$NAMESPACE' for pods matching '$POD_SELECTOR_SUBSTR'"

mapfile -t PODS < <(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null \
  | awk '{print $1}' | grep -E "$POD_SELECTOR_SUBSTR" || true)

if [[ ${#PODS[@]} -eq 0 ]]; then
    print_error "No pods found containing '$POD_SELECTOR_SUBSTR' in namespace '$NAMESPACE'."
    exit 1
fi

print_success "Found ${#PODS[@]} pod(s):"
printf '  • %s\n' "${PODS[@]}"

# -------------------- Build Test Targets --------------------
print_header "Preparing Test Environment"

TMPDIR="$(mktemp -d -t ue-ping-XXXXXX)"
RESULTS="$TMPDIR/results.tsv"   # POD<TAB>IFACE<TAB>STATUS<TAB>LOSS<TAB>RTT
DETAILS="$TMPDIR/details.log"   # freeform logs per job
trap 'rm -rf "$TMPDIR"' EXIT

> "$RESULTS"
> "$DETAILS"

# Build list of test targets
TARGETS=()  # each entry: POD|CONTAINER|IFACE
print_subheader "Discovering uesimtun* interfaces in each pod"

for POD in "${PODS[@]}"; do
    CONTAINER="$(kubectl get pod "$POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[0].name}' 2>/dev/null || true)"
    if [[ -z "$CONTAINER" ]]; then
        print_warning "Pod $POD: failed to get container name; skipping."
        continue
    fi

    IFACES="$(kubectl exec -n "$NAMESPACE" "$POD" -c "$CONTAINER" \
                --request-timeout="$REQUEST_TIMEOUT" -- sh -lc \
                'ls -1 /sys/class/net 2>/dev/null | grep -E "^uesimtun[0-9]+$" || true' 2>/dev/null || true)"
    if [[ -z "$IFACES" ]]; then
        print_warning "Pod $POD: no uesimtun* interfaces found; skipping."
        continue
    fi

    iface_count=$(echo "$IFACES" | wc -l)
    echo "  • $POD: found $iface_count interface(s)"
    
    while IFS= read -r IFACE; do
        [[ -z "$IFACE" ]] && continue
        TARGETS+=("${POD}|${CONTAINER}|${IFACE}")
    done <<< "$IFACES"
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    print_warning "No uesimtun* interfaces were found in any pod."
    exit 0
fi

print_success "Total interfaces to test: ${#TARGETS[@]}"

# -------------------- Run Parallel Tests --------------------
print_header "Running Parallel Ping Tests"
echo "Configuration:"
echo "  • Target: $TARGET (IPv$IP_FAMILY)"
echo "  • Ping count: $COUNT"
echo "  • Timeout: ${TIMEOUT}s per ping"
echo "  • Concurrency: $JOBS parallel jobs"
echo ""

# Use a named pipe as semaphore for job control
SEM="$TMPDIR/sem.fifo"
mkfifo "$SEM"
exec 9<> "$SEM"
rm "$SEM"
# seed tokens
for ((i=0;i<JOBS;i++)); do echo >&9; done

run_one() {
    local pod="$1" container="$2" iface="$3"

    local ping_cmd
    if [[ "$IP_FAMILY" == "6" ]]; then
        ping_cmd="ping -6 -I $iface -c $COUNT -W $TIMEOUT $TARGET"
    else
        ping_cmd="ping -4 -I $iface -c $COUNT -W $TIMEOUT $TARGET"
    fi

    # Run, capture output and success/fail
    local output
    if output=$(kubectl exec -n "$NAMESPACE" "$pod" -c "$container" \
          --request-timeout="$REQUEST_TIMEOUT" -- sh -lc "$ping_cmd" 2>&1); then
        
        # Extract stats from ping output
        local packet_loss rtt_avg
        packet_loss=$(echo "$output" | grep -oP '\d+(?=% packet loss)' || echo "?")
        rtt_avg=$(echo "$output" | grep -oP 'min/avg/max[^=]*=\s*[\d.]+/([\d.]+)' | grep -oP '\d+\.\d+' | head -1 || echo "?")
        
        echo -e "${pod}\t${iface}\tOK\t${packet_loss}\t${rtt_avg}" >> "$RESULTS"
        [[ "$DEBUG" == "1" ]] && echo "[OK] $pod $iface (loss: ${packet_loss}%, rtt: ${rtt_avg}ms)" >> "$DETAILS"
    else
        echo -e "${pod}\t${iface}\tFAIL\t-\t-" >> "$RESULTS"
        {
            echo "[FAIL] $pod $iface"
            echo "  Command: $ping_cmd"
            echo "  Output: $output"
            echo ""
        } >> "$DETAILS"
    fi
}

# Spawn jobs
for item in "${TARGETS[@]}"; do
    # wait for a token
    read -r -u 9
    IFS='|' read -r POD CONTAINER IFACE <<< "$item"
    {
        run_one "$POD" "$CONTAINER" "$IFACE"
        # return token
        echo >&9
    } &
done
wait  # wait for all jobs to finish

# -------------------- Per-Pod Summary --------------------
print_header "Per-Pod Results"

# Sort results by pod + iface numeric and display with stats
sort -k1,1 -k2,2V "$RESULTS" | awk -F'\t' '
{
    pod=$1; iface=$2; st=$3; loss=$4; rtt=$5;
    pods[pod]++;
    
    if (st=="OK") {
        ok[pod]++;
        # Format the interface result line
        printf("  \033[1;32m✓\033[0m %-20s %-12s", pod, "[" iface "]");
        if (loss != "?") printf("  loss: %3s%%", loss);
        if (rtt != "?")  printf("  rtt: %6sms", rtt);
        print "";
    } else {
        fail[pod]++;
        failed_list[pod]=(failed_list[pod] ? failed_list[pod] ", " : "") iface;
        printf("  \033[1;31m✗\033[0m %-20s %-12s  \033[2mFAILED\033[0m\n", pod, "[" iface "]");
    }
}
END{
    print "";
    print "\033[1;36m" "Pod Statistics:" "\033[0m";
    print "─────────────────────────────────────────────────────────";
    
    for (p in pods) {
        okc = ok[p] + 0; 
        total = pods[p]; 
        failc = fail[p] + 0;
        rate = (total ? (okc*100.0/total) : 0);
        
        if (okc == total)
            printf("  \033[1;32m%-20s\033[0m  %2d/%2d interfaces  (%.0f%% success)\n", p, okc, total, rate);
        else
            printf("  \033[1;31m%-20s\033[0m  %2d/%2d interfaces  (%.0f%% success)\n", p, okc, total, rate);
        
        if (failc > 0)
            printf("    \033[2m↳ Failed: %s\033[0m\n", failed_list[p]);
    }
}'

# -------------------- Global Summary --------------------
print_header "Test Summary"

total_ifaces=$(wc -l < "$RESULTS")
total_ok=$(awk -F'\t' '$3=="OK"{c++} END{print c+0}' "$RESULTS")
total_fail=$(( total_ifaces - total_ok ))
rate=$(awk -v ok="$total_ok" -v tot="$total_ifaces" 'BEGIN{if(tot==0){print "0.0"}else{printf("%.1f",(ok*100.0)/tot)}}')

echo ""
if [[ $total_ok -eq $total_ifaces ]]; then
    print_success "✓ ALL TESTS PASSED"
    echo "  • $total_ok/$total_ifaces interfaces successful (${rate}%)"
else
    print_error "✗ SOME TESTS FAILED"
    echo "  • $total_ok/$total_ifaces interfaces successful (${rate}%)"
    echo "  • $total_fail interface(s) failed"
fi

if [[ $total_fail -gt 0 ]]; then
    echo ""
    print_subheader "Failed Interfaces"
    awk -F'\t' '$3=="FAIL"{printf("  • %s : %s\n", $1, $2)}' "$RESULTS" | sort
fi

echo ""

# Show debug details if enabled
if [[ "$DEBUG" == "1" ]]; then
    print_header "Debug Details"
    sed 's/^/  | /' "$DETAILS"
    echo ""
fi

print_success "Connectivity test complete."