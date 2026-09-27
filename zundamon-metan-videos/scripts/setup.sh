#!/bin/bash
# VOICEVOX Core（ずんだもん・四国めたんの声）と、動画づくりに使うライブラリを入れる。作業フォルダで実行する。
set -e
VV=${VV_DIR:-vv}; mkdir -p "$VV"; cd "$VV"
V=0.16.4                      # VOICEVOX Core の版
ORT=1.17.3                    # VOICEVOX 用 ONNX Runtime の版
GH=https://github.com/VOICEVOX
WHL=voicevox_core-$V-cp310-abi3-manylinux_2_34_x86_64.whl
[ -f "$WHL" ] || curl -fsSL --retry 3 -o "$WHL" "$GH/voicevox_core/releases/download/$V/$WHL"
[ -d voicevox_onnxruntime-linux-x64-$ORT ] || curl -fsSL --retry 3 "$GH/onnxruntime-builder/releases/download/voicevox_onnxruntime-$ORT/voicevox_onnxruntime-linux-x64-$ORT.tgz" | tar xz
[ -f 0.vvm ] || curl -fsSL --retry 3 -o 0.vvm "$GH/voicevox_vvm/releases/download/$V/0.vvm"   # ずんだもん・四国めたんなど
[ -d open_jtalk_dic_utf_8-1.11 ] || curl -fsSL --retry 3 https://github.com/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-1.11.tar.gz | tar xz
cd - >/dev/null
PIP="pip install -q --break-system-packages"
python3 -c "import voicevox_core" 2>/dev/null || $PIP "$VV/$WHL"
python3 -c "import pyopenjtalk" 2>/dev/null || $PIP pyopenjtalk      # 字幕の改行位置を決めるのに使う（初回は1分ほどかかる）
python3 -c "import numpy, PIL" 2>/dev/null || $PIP numpy pillow
which ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
fc-list :lang=ja | grep -q "Noto Sans CJK" || apt-get install -y -qq fonts-noto-cjk
python3 - <<'PY'
import glob, os
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
vv = os.environ.get("VV_DIR", "vv")
syn = Synthesizer(Onnxruntime.load_once(filename=sorted(glob.glob(f"{vv}/voicevox_onnxruntime-*/lib/libvoicevox_onnxruntime.so*"))[0]),
                  OpenJtalk(sorted(glob.glob(f"{vv}/open_jtalk_dic_utf_8-*"))[0]))
with VoiceModelFile.open(f"{vv}/0.vvm") as m:
    syn.load_voice_model(m)
    print("声：", {c.name: [(s.name, s.id) for s in c.styles] for c in m.metas if c.name in ("ずんだもん", "四国めたん")})
print("VOICEVOX の準備ができました")
PY
