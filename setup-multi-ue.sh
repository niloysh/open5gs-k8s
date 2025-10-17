#!/bin/bash

################################################################################
# setup-multi-ue.sh
#
# Automates the setup and configuration of multiple simulated 5G UEs for testing.
# This script:
#   1. Generates and loads a specified number of subscribers into MongoDB
#   2. Splits subscribers across two UE instances (ue1 and ue2)
#   3. Patches UERANSIM configuration files with proper IMSI endings and credentials
#   4. Updates wrapper scripts to set the correct number of simulated UEs
#   5. Creates backups of all modified files
#
# Environment Variables (optional):
#   TOTAL_AUTO_SUBS  - Total number of subscribers to generate (default: 100)
#   UE1_LAST3        - Last 3 digits of IMSI for ue1 (default: 101)
#   UE2_LAST3        - Last 3 digits of IMSI for ue2 (default: 201)
#   SUBS_KEY         - Subscriber key (default: 465B5CE8B199B49FAA5F0A2EE238A6BC)
#   SUBS_OPC         - Subscriber OPC (default: E8ED289DEBA952E4283B54E88E6183CA)
#   UERANSIM_DIR     - Path to UERANSIM directory (default: ueransim)
#
# Usage:
#   ./setup-multi-ue.sh
#   TOTAL_AUTO_SUBS=200 ./setup-multi-ue.sh
#
################################################################################

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

# -------------------- Configuration --------------------
TOTAL_AUTO_SUBS="${TOTAL_AUTO_SUBS:-100}"      # total auto subscribers to generate/load
UERANSIM_DIR="${UERANSIM_DIR:-ueransim}"       # path to ueransim dir
BACKUP_DIR="${BACKUP_DIR:-${UERANSIM_DIR}-bak}"

# Desired last-3 digits for SUPI/IMSI endings
UE1_LAST3="${UE1_LAST3:-101}"
UE2_LAST3="${UE2_LAST3:-201}"

# Subscription credentials to write into both ue1.yaml and ue2.yaml
SUBS_KEY="${SUBS_KEY:-465B5CE8B199B49FAA5F0A2EE238A6BC}"
SUBS_OPC="${SUBS_OPC:-E8ED289DEBA952E4283B54E88E6183CA}"

UE1_DIR="${UERANSIM_DIR}/ueransim-ue/ue1"
UE2_DIR="${UERANSIM_DIR}/ueransim-ue/ue2"
UE1_YAML="${UE1_DIR}/ue1.yaml"
UE2_YAML="${UE2_DIR}/ue2.yaml"
UE1_WRAP="${UE1_DIR}/wrapper.sh"
UE2_WRAP="${UE2_DIR}/wrapper.sh"

# -------------------- Derived: split counts across wrappers --------------------
UE1_COUNT=$(( (TOTAL_AUTO_SUBS + 1) / 2 ))  # ceil
UE2_COUNT=$(( TOTAL_AUTO_SUBS / 2 ))        # floor

# -------------------- Helper Functions --------------------
die() {
    print_error "$*"
    exit 1
}

need_file() {
    [[ -f "$1" ]] || die "Missing file: $1"
}

need_dir() {
    [[ -d "$1" ]] || die "Missing dir: $1"
}

# Replace the ENTIRE nr-ue line with a deterministic command, preserving indentation.
# Ensures EXACTLY:
#   /ueransim/nr-ue -c /ueransim/config/ueX.yaml -n COUNT
set_wrapper_cmd() {
    local file="$1" ue_name="$2" count="$3"
    local cmd="/ueransim/nr-ue -c /ueransim/config/${ue_name}.yaml -n ${count}"
    [[ -f "${file}.bak" ]] || cp -p "$file" "${file}.bak"

    # Normalize CRLF if present
    if grep -q $'\r' "$file"; then
        tr -d '\r' < "$file" > "${file}.unix" && mv "${file}.unix" "$file"
    fi

    awk -v desired="$cmd" '
        BEGIN{done=0}
        {
            if (!done && $0 ~ /nr-ue([[:space:]]|$)/) {
                match($0, /^([[:space:]]*)/, m); indent = (m[1] ? m[1] : "")
                print indent desired
                done=1
            } else {
                print
            }
        }
        END{ if (!done) exit 42 }
    ' "$file" > "${file}.tmp" || {
        rm -f "${file}.tmp"
        print_error "Could not locate an 'nr-ue' invocation in ${file}"
        exit 1
    }
    mv "${file}.tmp" "$file"
    chmod +x "$file" || true
}

# Replace the final 3 digits of SUPI/IMSI numeric string in YAML
patch_imsi_last3() {
    local file="$1" last3="$2"
    [[ -f "${file}.bak" ]] || cp -p "$file" "${file}.bak"
    if grep -q $'\r' "$file"; then
        tr -d '\r' < "$file" > "${file}.unix" && mv "${file}.unix" "$file"
    fi
    sed -E -i \
        -e "s/(supi:[[:space:]]*'?[Ii][Mm][Ss][Ii]-)([0-9]*)([0-9]{3})('?)/\1\2${last3}\4/" \
        -e "s/(imsi:[[:space:]]*')([0-9]*)([0-9]{3})(')/\1\2${last3}\4/" \
        -e "s/(imsi:[[:space:]]*)([0-9]*)([0-9]{3})/\1\2${last3}/" \
        "$file"
}

# Replace key/op/opc values (quoted or unquoted). We prefer 'opc' if present; if file has only 'op', we set that.
patch_key_opc() {
    local file="$1" key_val="$2" opc_val="$3"
    [[ -f "${file}.bak" ]] || cp -p "$file" "${file}.bak"
    if grep -q $'\r' "$file"; then
        tr -d '\r' < "$file" > "${file}.unix" && mv "${file}.unix" "$file"
    fi

    # key: ...
    # Matches: key: 'HEX' | key: "HEX" | key: HEX  (case-insensitive HEX)
    sed -E -i \
        -e "s/^([[:space:]]*key:[[:space:]]*)['\"]?[0-9A-Fa-f]+['\"]?/\1'${key_val}'/" \
        "$file"

    # opc: ...
    if grep -qiE '^[[:space:]]*opc:' "$file"; then
        sed -E -i \
            -e "s/^([[:space:]]*opc:[[:space:]]*)['\"]?[0-9A-Fa-f]+['\"]?/\1'${opc_val}'/I" \
            "$file"
    elif grep -qiE '^[[:space:]]*op:' "$file"; then
        # Fallback to 'op:' if 'opc:' not present
        sed -E -i \
            -e "s/^([[:space:]]*op:[[:space:]]*)['\"]?[0-9A-Fa-f]+['\"]?/\1'${opc_val}'/I" \
            "$file"
    else
        # If neither exists, append both (some templates omit them)
        printf "\nkey: '%s'\nopc: '%s'\n" "${key_val}" "${opc_val}" >> "$file"
    fi
}

# -------------------- Main Script --------------------
print_header "Setting up Multi-UE Environment"

# Sanity checks
print_subheader "Validating environment"
need_dir "$UERANSIM_DIR"
need_dir "$UE1_DIR"
need_dir "$UE2_DIR"
need_file "$UE1_YAML"
need_file "$UE2_YAML"
need_file "$UE1_WRAP"
need_file "$UE2_WRAP"
command -v python3 >/dev/null || die "python3 not found"
print_success "Environment validation complete."

# Generate & load subscribers
print_header "Generating and Loading Subscribers"
print_subheader "Generating ${TOTAL_AUTO_SUBS} auto-subscribers"
python3 mongo-tools/generate-data.py \
    --num-auto-generated-subscribers "${TOTAL_AUTO_SUBS}" \
    --subscribers-file "data/subscribers_${TOTAL_AUTO_SUBS}.yaml"
print_success "Subscriber data generated."

print_subheader "Loading subscribers into MongoDB"
python3 mongo-tools/add-subscribers.py \
    --subscribers-file "data/subscribers_${TOTAL_AUTO_SUBS}.yaml"
print_success "Subscribers loaded into MongoDB."

# One-time backup of entire ueransim tree
print_header "Creating Backup"
if [[ -e "$BACKUP_DIR" ]]; then
    echo "Backup already exists at '${BACKUP_DIR}'. Skipping full-tree backup."
else
    print_subheader "Backing up '${UERANSIM_DIR}' -> '${BACKUP_DIR}'"
    cp -a "$UERANSIM_DIR" "$BACKUP_DIR"
    print_success "Backup created successfully."
fi

# In-place patching
print_header "Patching Configuration Files"

print_subheader "Rewriting wrapper nr-ue lines"
set_wrapper_cmd "$UE1_WRAP" "ue1" "$UE1_COUNT"
set_wrapper_cmd "$UE2_WRAP" "ue2" "$UE2_COUNT"
print_success "Wrapper commands updated."

print_subheader "Patching SUPI/IMSI endings: ue1 -> ${UE1_LAST3}, ue2 -> ${UE2_LAST3}"
patch_imsi_last3 "$UE1_YAML" "$UE1_LAST3"
patch_imsi_last3 "$UE2_YAML" "$UE2_LAST3"
print_success "IMSI endings patched."

print_subheader "Setting key/opc credentials"
patch_key_opc "$UE1_YAML" "$SUBS_KEY" "$SUBS_OPC"
patch_key_opc "$UE2_YAML" "$SUBS_KEY" "$SUBS_OPC"
print_success "Credentials configured."

# Summary
print_header "Setup Complete"
echo "Multi-UE environment configured with the following parameters:"
echo "  • Total subscribers: ${TOTAL_AUTO_SUBS}"
echo "  • UE1 count: ${UE1_COUNT} (IMSI ending: ${UE1_LAST3})"
echo "  • UE2 count: ${UE2_COUNT} (IMSI ending: ${UE2_LAST3})"
echo ""
echo "Wrapper commands set to:"
echo "  • /ueransim/nr-ue -c /ueransim/config/ue1.yaml -n ${UE1_COUNT}"
echo "  • /ueransim/nr-ue -c /ueransim/config/ue2.yaml -n ${UE2_COUNT}"
echo ""
echo "Backups created:"
echo "  • ${UE1_YAML}.bak"
echo "  • ${UE2_YAML}.bak"
echo "  • ${BACKUP_DIR}"
echo ""
echo -e "\e[1;33mNext steps:\e[0m"
echo "1. Run ./deploy-ran.sh to deploy the RAN"
echo "2. Run ./ping-test-multiple.sh to test connectivity"
echo ""
echo "To restore the original configuration:"
echo "  rm -rf '${UERANSIM_DIR}' && cp -a '${BACKUP_DIR}' '${UERANSIM_DIR}'"