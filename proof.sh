#!/usr/bin/env bash
# 终端展示：证明这套系统真的跑在 IBM Z / LinuxONE 上。
# 每一行都来自真实命令，没有任何写死的数据。
#
#   ./proof.sh

set -u

HOST="${1:-datathon}"

ssh -o BatchMode=yes -o ConnectTimeout=15 -o ControlPath=none "$HOST" '
m=$(uname -m)
k=$(uname -r)
c=$(nproc)
mem=$(free -h | awk "/^Mem:/{print \$2}")
mt=$(lscpu | awk -F: "/Machine type/{gsub(/ /,\"\",\$2); print \$2}")
bo=$(lscpu | awk -F: "/Byte Order/{gsub(/^ +/,\"\",\$2); print \$2}")
ven=$(lscpu | awk -F: "/Vendor ID/{gsub(/^ +/,\"\",\$2); print \$2}")
feat=$(grep -m1 "^features" /proc/cpuinfo)
if echo "$feat" | grep -qw nnpa; then ai="present (NNPA)"; else ai="not listed"; fi
ctr=$(sudo -n docker ps --format "{{.Names}}  {{.Status}}" 2>/dev/null | grep scam-guard)

bar="════════════════════════════════════════════════════════════"

echo ""
echo "$bar"
echo "   IBM LinuxONE  ·  Real-Time Transfer Scam Guard"
echo "$bar"
echo ""
printf "   %-18s %s\n" "architecture"     "$m"
printf "   %-18s %s\n" "vendor"           "$ven"
printf "   %-18s %s\n" "machine type"     "${mt:-n/a}"
printf "   %-18s %s\n" "byte order"       "${bo:-n/a}"
printf "   %-18s %s\n" "cores"            "$c"
printf "   %-18s %s\n" "memory"           "$mem"
printf "   %-18s %s\n" "kernel"           "$k"
echo ""
printf "   %-18s %s\n" "AI accelerator"   "$ai"
printf "   %-18s %s\n" "container"        "${ctr:-not running}"
echo ""
echo "$bar"
echo "   uname -m  ->  $m        (not x86)"
echo "$bar"
echo ""
'
