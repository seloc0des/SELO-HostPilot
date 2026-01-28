#!/bin/bash
# Script to check and install missing system diagnostic tools for Ollama ToolChat

echo "Checking for required system tools..."

# List of tools to check (package_name:command_name)
TOOLS=(
    "coreutils:uname"
    "coreutils:hostname"
    "coreutils:whoami"
    "coreutils:id"
    "coreutils:env"
    "systemd:timedatectl"
    "libc-bin:locale"
    "coreutils:df"
    "coreutils:du"
    "util-linux:lsblk"
    "util-linux:findmnt"
    "procps:ps"
    "procps:free"
    "procps:vmstat"
    "sysstat:iostat"
    "procps:uptime"
    "systemd:journalctl"
    "util-linux:dmesg"
    "pciutils:lspci"
    "usbutils:lsusb"
    "util-linux:lscpu"
    "lm-sensors:sensors"
    "procps:top"
    "sysstat:pidstat"
    "iproute2:ss"
    "iproute2:ip"
    "network-manager:nmcli"
    "iputils-ping:ping"
    "systemd:resolvectl"
    "ufw:ufw"
    "apparmor-utils:aa-status"
    "systemd:loginctl"
    "lsof:lsof"
    "psmisc:fuser"
    "file:file"
    "libc-bin:ldd"
    "util-linux:last"
    "findutils:find"
    "fd-find:fdfind"
    "ripgrep:rg"
    "tree:tree"
)

MISSING_PACKAGES=()

for tool in "${TOOLS[@]}"; do
    package="${tool%%:*}"
    command="${tool##*:}"
    
    if ! command -v "$command" &> /dev/null; then
        echo "❌ Missing: $command (package: $package)"
        MISSING_PACKAGES+=("$package")
    else
        echo "✓ Found: $command"
    fi
done

# Check for nvidia-smi (optional)
if ! command -v nvidia-smi &> /dev/null; then
    echo "ℹ️  Optional: nvidia-smi not found (install nvidia-driver if you have NVIDIA GPU)"
else
    echo "✓ Found: nvidia-smi"
fi

# Remove duplicates from missing packages
UNIQUE_PACKAGES=($(printf "%s\n" "${MISSING_PACKAGES[@]}" | sort -u))

if [ ${#UNIQUE_PACKAGES[@]} -eq 0 ]; then
    echo ""
    echo "✅ All required tools are installed!"
else
    echo ""
    echo "📦 Missing packages to install:"
    printf '%s\n' "${UNIQUE_PACKAGES[@]}"
    echo ""
    echo "To install missing packages, run:"
    echo "sudo apt update && sudo apt install -y ${UNIQUE_PACKAGES[*]}"
fi

echo ""
echo "Tool check complete!"
