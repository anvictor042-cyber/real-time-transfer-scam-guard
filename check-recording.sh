#!/usr/bin/env bash
# 录完立刻自检：时长、分辨率、有没有声音、声音够不够大。
#
#   ./check-recording.sh                # 检查桌面上最新的 .mov
#   ./check-recording.sh 某文件.mov      # 检查指定文件

set -u

if [ $# -ge 1 ]; then
  F="$1"
else
  F=$(find "$HOME/Desktop" "$HOME/Movies" -maxdepth 1 -name "*.mov" -print0 2>/dev/null \
      | xargs -0 ls -t 2>/dev/null | head -1)
fi

if [ -z "${F:-}" ] || [ ! -f "$F" ]; then
  echo "找不到录像文件。用法：./check-recording.sh 路径.mov"
  exit 1
fi

echo ""
echo "文件: $(basename "$F")"
echo "──────────────────────────────────────────────"

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F" 2>/dev/null)
res=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "$F" 2>/dev/null | head -1)

printf "  时长        %s\n" "$(python3 -c "
d=float('${dur:-0}'); m=int(d//60); s=int(d%60)
print(f'{m}:{s:02d} ({d:.1f} 秒)')" 2>/dev/null || echo "$dur")"

printf "  分辨率      %s\n" "$(echo "$res" | awk -F, '{print $1" × "$2}')"

if [ "$(python3 -c "print(1 if float('${dur:-0}') < 180 else 0)")" = "1" ]; then
  echo "  时长判定    ✅ 在 3 分钟内"
else
  echo "  时长判定    ❌ 超过 3 分钟，需要裁剪"
fi

echo ""
if ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$F" 2>/dev/null | grep -q audio; then
  echo "  音轨        ✅ 存在"
  lv=$(ffmpeg -hide_banner -i "$F" -af volumedetect -f null - 2>&1)
  mean=$(echo "$lv" | grep -oE "mean_volume: [-0-9.]+" | grep -oE "[-0-9.]+$")
  max=$(echo "$lv" | grep -oE "max_volume: [-0-9.]+" | grep -oE "[-0-9.]+$")
  printf "  平均音量    %s dB\n" "${mean:-?}"
  printf "  最大音量    %s dB\n" "${max:-?}"
  echo ""
  if python3 -c "import sys; sys.exit(0 if float('${max:--99}') > -18 else 1)" 2>/dev/null; then
    echo "  声音判定    ✅ 有清晰人声，可以用"
  elif python3 -c "import sys; sys.exit(0 if float('${max:--99}') > -30 else 1)" 2>/dev/null; then
    echo "  声音判定    ⚠️ 太小，评委听不清 —— 调高输入音量重录"
  else
    echo "  声音判定    ❌ 基本是静音 —— 麦克风没录到，必须重录"
    echo ""
    echo "  怎么修："
    echo "    1. 系统设置 → 声音 → 输入 → 选「iMac麦克风」，对着说话看电平条是否跳动"
    echo "    2. 系统设置 → 隐私与安全性 → 麦克风 → 确认「截屏」已打开"
    echo "    3. ⌘⇧5 → 选项 → 麦克风 → 明确选「iMac麦克风」"
  fi
else
  echo "  音轨        ❌ 没有音轨"
  echo "  声音判定    ❌ 整条是哑的，必须重录"
  echo ""
  echo "  怎么修："
  echo "    ⌘⇧5 → 选项 → 麦克风 → 选「iMac麦克风」（默认是「无」）"
fi

echo "──────────────────────────────────────────────"
echo ""
