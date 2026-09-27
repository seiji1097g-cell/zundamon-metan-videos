"""ずんだもん・四国めたんの立ち絵PNG（スキルの assets/img、または build_psd_sprites.py で作ったもの）を読み込む。
render.py から使う：CHAR, FACES, find_font, build_all, sheet"""
import os, subprocess
from PIL import Image

CHAR = {"komugi": "ずんだもん", "azuki": "四国めたん"}
FACES = ["normal", "smile", "surprise", "trouble", "think"]
MOUTHS = ["closed", "half", "open"]
EYES = ["open", "closed"]


def find_font(weight="Bold"):
    """Noto Sans CJK JP を探す。.ttc は index=0 が日本語"""
    for d in ("/usr/share/fonts/opentype/noto", "/usr/share/fonts/noto-cjk", "/usr/share/fonts/google-noto-cjk",
              "/usr/share/fonts/truetype/noto", os.path.expanduser("~/.fonts"), os.path.expanduser("~/.local/share/fonts")):
        for name in (f"NotoSansCJK-{weight}.ttc", f"NotoSansCJKjp-{weight}.otf", f"NotoSansJP-{weight}.otf", f"NotoSansJP-{weight}.ttf"):
            if os.path.exists(os.path.join(d, name)):
                return os.path.join(d, name)
    out = subprocess.run(["fc-list", ":lang=ja", "file"], capture_output=True, text=True).stdout.split()
    files = [f.rstrip(":") for f in out if "Sans" in f] or [f.rstrip(":") for f in out]
    if not files:
        raise SystemExit("日本語フォントが見つかりません。fonts-noto-cjk を入れてください（例：apt-get install -y fonts-noto-cjk）")
    return files[0]


def build_all(character_images=None, base_dir="."):
    """(キャラ, 表情, 口, 目) → 画像。目を閉じた差分がない表情（笑顔など）は目を開けた画像で代用する"""
    d = os.path.join(base_dir, (character_images or {}).get("dir", "img"))
    sp = {}
    for n in CHAR:
        for fc in FACES:
            for m in MOUTHS:
                for e in EYES:
                    p = os.path.join(d, f"{n}_{fc}_{m}_{e}.png")
                    if not os.path.exists(p): p = os.path.join(d, f"{n}_{fc}_{m}_open.png")
                    sp[(n, fc, m, e)] = Image.open(p).convert("RGBA")
    return sp


def sheet(path, sprites):
    """全表情を1枚に並べた確認用画像（上段：口を閉じる、下段：口を開ける／まばたき）"""
    w = max(im.width for im in sprites.values()); h = max(im.height for im in sprites.values())
    im = Image.new("RGBA", (w * 5, h * 4), (190, 225, 250, 255))
    for j, n in enumerate(CHAR):
        for i, fc in enumerate(FACES):
            a = sprites[(n, fc, "closed", "open")]
            b = sprites[(n, fc, "open" if i % 2 == 0 else "half", "closed" if i in (0, 3) else "open")]
            im.alpha_composite(a, (i * w, j * 2 * h + h - a.height))
            im.alpha_composite(b, (i * w, (j * 2 + 1) * h + h - b.height))
    im.convert("RGB").resize((w * 5 // 2, h * 2)).save(path)
