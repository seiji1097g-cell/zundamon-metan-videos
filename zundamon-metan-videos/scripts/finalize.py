"""書き出し後に、台本（script.md）と概要欄（description.txt）を作り、納品フォルダにそろえる。
使い方：python3 finalize.py script.json 出力フォルダ 納品フォルダ"""
import json, os, shutil, sys

SCRIPT, OUT, DEST = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(DEST, exist_ok=True)
sc = json.load(open(SCRIPT, encoding="utf-8"))
tl = json.load(open("work/timeline.json", encoding="utf-8"))
NM = {"komugi": "ずんだもん", "azuki": "四国めたん"}
mmss = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"

rows = ["# " + sc["title"], "", "| 開始 | 話し手 | セリフ |", "|---|---|---|"]
rows += [f"| {mmss(l['start'])} | {NM[l['speaker']]} | {l['text']} |" for l in tl]
open(f"{DEST}/script.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")

chapters = open("work/chapters.txt", encoding="utf-8").read().strip()
src = "\n".join(f"・{s['title']}\n  {s['url']}" for s in sc.get("sources", []))
desc = f"""{sc['title']}

{sc.get('summary', '').strip()}

■チャプター
{chapters}

■出典
{src}

■クレジット
VOICEVOX:ずんだもん
VOICEVOX:四国めたん
立ち絵：坂本アヒル（ずんだもん立ち絵素材／四国めたん立ち絵素材）
"""
open(f"{DEST}/description.txt", "w", encoding="utf-8").write(desc)
for f in ["video.mp4", "subtitles.srt", "thumbnail.png"]:
    shutil.copy(os.path.join(OUT, f), os.path.join(DEST, f))
print("納品フォルダ：", DEST, sorted(os.listdir(DEST)))
