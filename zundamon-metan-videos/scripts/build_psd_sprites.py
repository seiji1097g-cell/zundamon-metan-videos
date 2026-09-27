"""（予備）坂本アヒルさんの立ち絵PSD（ずんだもん・四国めたん）から、表情×口×目の立ち絵PNGを img/ に作る。
立ち絵セットのArtifactを読めないときだけ使う。
使い方：python3 build_psd_sprites.py ずんだもん立ち絵素材.zip 四国めたん立ち絵素材.zip   （ZIPでもPSDでもよい）
komugi＝ずんだもん（聞き役・右）、azuki＝四国めたん（解説役・左）。1枚2〜3秒、全部で3分ほどかかる。"""
import glob, os, sys, zipfile
from psd_tools import PSDImage   # pip install psd-tools


def find(g, path):
    for name in path.split("/"):
        g = next(l for l in g if l.name == name)
    return g


class Char:
    def __init__(self, path):
        self.psd = PSDImage.open(path)
        self.default = {id(l): l.visible for l in self.psd.descendants()}

    def compose(self, radio=None, show=()):
        """radio：{"グループのパス": "表示する子レイヤー名"}（PSDToolの * は1つだけ表示するグループ）"""
        for l in self.psd.descendants(): l.visible = self.default[id(l)]
        for gp, child in (radio or {}).items():
            g = find(self.psd, gp)
            for l in g:
                if l.name.startswith("*"): l.visible = (l.name == child)
            find(g, child).visible = True
        for p in show: find(self.psd, p).visible = True
        return self.psd.composite(force=True).convert("RGBA")


def extract(paths):
    """ZIP（日本語のファイル名はcp932）を assets/ に展開して、PSDの一覧を返す"""
    psds = []
    for p in paths:
        if p.lower().endswith(".psd"): psds.append(p); continue
        with zipfile.ZipFile(p) as z:
            for i in z.infolist():
                name = i.filename if i.flag_bits & 0x800 else i.filename.encode("cp437").decode("cp932", "replace")
                if name.endswith("/"): continue
                out = os.path.join("assets", name); os.makedirs(os.path.dirname(out), exist_ok=True)
                open(out, "wb").write(z.read(i))
                if out.lower().endswith(".psd"): psds.append(out)
    return psds


SCALE = 0.58
CFG = {
  "komugi": {  # ずんだもん
    "crop": (230, 100, 985, 1100),
    "base": {"!眉": "*普通眉", "!目": "*目セット", "!目/*目セット/!黒目": "*普通目", "!顔色": "*ほっぺ",
             "*服装1/!右腕": "*基本", "*服装1/!左腕": "*基本"},
    "blink": {"!目": "*UU"},
    "faces": {
      "normal":   {"radio": {}, "mouth": ["*むふ", "*ほあ", "*ほあー"]},
      "smile":    {"radio": {"!目": "*にっこり2", "*服装1/!右腕": "*手を挙げる"}, "mouth": ["*むふ", "*ほあ", "*ほあー"], "blink": None},
      "surprise": {"radio": {"!目": "*〇〇", "!眉": "*上がり眉"}, "mouth": ["*お", "*お", "*おほお"]},
      "trouble":  {"radio": {"!眉": "*困り眉1", "!目/*目セット/!黒目": "*目逸らし"}, "mouth": ["*んへー", "*んあー", "*んあー"], "show": ["記号など/汗1"]},
      "think":    {"radio": {"!目": "*ジト目", "*服装1/!左腕": "*考える"}, "mouth": ["*むー", "*ほあ", "*ほあー"]},
    }},
  "azuki": {   # 四国めたん
    "crop": (100, 15, 985, 1090),
    "base": {"!眉": "*ごきげん", "!目": "*目セット", "!目/*目セット/!黒目": "*カメラ目線", "!顔色": "*普通2",
             "*白ロリ服/!右腕": "*普通", "*白ロリ服/!左腕": "*普通"},
    "blink": {"!目": "*目閉じ2"},
    "faces": {
      "normal":   {"radio": {}, "mouth": ["*ほほえみ", "*▽", "*わあー"]},
      "smile":    {"radio": {"!目": "*目閉じ2", "*白ロリ服/!右腕": "*指差す"}, "mouth": ["*ほほえみ", "*▽", "*わあー"], "blink": None},
      "surprise": {"radio": {"!目": "*見上げ2"}, "mouth": ["*お", "*お", "*わあー"]},
      "trouble":  {"radio": {"!眉": "*こまり", "!目/*目セット/!黒目": "*目そらし"}, "mouth": ["*んー", "*いー", "*うえー"], "show": ["記号など/汗"]},
      "think":    {"radio": {"!眉": "*ややおこ", "!目/*目セット/!黒目": "*目そらし2", "*白ロリ服/!左腕": "*口元に指"}, "mouth": ["*む", "*▽", "*わあー"]},
    }},
}
MOUTHS = ["closed", "half", "open"]
psds = extract(sys.argv[1:])
for n, key in (("komugi", "ずんだもん"), ("azuki", "四国めたん")):
    CFG[n]["psd"] = next((p for p in psds if key in os.path.basename(p)), None)
    if not CFG[n]["psd"]: raise SystemExit(f"{key}のPSDが見つかりません")
os.makedirs("img", exist_ok=True)
for n, c in CFG.items():
    ch = Char(c["psd"])
    for fc, spec in c["faces"].items():
        for mi, m in enumerate(MOUTHS):
            for e in ["open", "closed"]:
                radio = dict(c["base"]); radio.update(spec["radio"]); radio["!口"] = spec["mouth"][mi]
                if e == "closed":
                    if spec.get("blink", "x") is None: continue            # 目を閉じた表情はまばたきしない
                    radio.update(c["blink"]); radio.pop("!目/*目セット/!黒目", None)
                im = ch.compose(radio, show=spec.get("show", ())).crop(c["crop"])
                im = im.resize((int(im.width * SCALE), int(im.height * SCALE)), 1)
                p = f"img/{n}_{fc}_{m}_{e}.png"; im.save(p, optimize=True); print(p, flush=True)
print("立ち絵を img/ に作りました")
