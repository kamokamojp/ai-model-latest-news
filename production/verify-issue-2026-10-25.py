#!/usr/bin/env python3
"""Reproducible local QA for the 2026-10-25 AI Model Latest Radio issue."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE = "2026-10-25"
EXPECTED_SPEAKERS = {"akari": ("あかり", 10005), "naoto": ("なおと", 10001)}
OLD_DATES = [f"2026-10-{day:02d}" for day in range(19, 25)]

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.audio=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get("id"): self.ids.append(a["id"])
        for attr in ("href", "src"):
            if a.get(attr): self.links.append(a[attr])
        if tag == "audio" and a.get("src"): self.audio.append(a["src"])

script_path=ROOT/"editions"/f"{ISSUE}-script.json"
article_path=ROOT/"editions"/f"{ISSUE}.md"
script_md_path=ROOT/"editions"/f"{ISSUE}-script.md"
page_path=ROOT/"editions"/f"{ISSUE}.html"
research_path=ROOT/"production"/f"{ISSUE}-research.json"
index_path=ROOT/"editions"/"index.json"
script=json.loads(script_path.read_text(encoding="utf-8"))
research=json.loads(research_path.read_text(encoding="utf-8"))
archive=json.loads(index_path.read_text(encoding="utf-8"))

require(script["issue_id"]==ISSUE and script["issue_date"]==ISSUE and script["issue_number"]==8, "script issue identity mismatch")
require(script["timezone"]=="Asia/Tokyo" and script["scheduled_target_cutoff"]=="2026-10-25T08:00+09:00", "scheduled JST cutoff mismatch")
require(script["research_cutoff"]=="2026-10-25T08:07+09:00", "research cutoff mismatch")
require(research["research_cutoff"]==script["research_cutoff"] and research["research_cutoff_utc"]=="2026-10-24T23:07:00Z", "research cutoff timezone mismatch")
require(research["previous_issue_id"]=="2026-10-24" and research["previous_issue_cutoff"]=="2026-10-24T08:10:58+09:00", "previous issue cutoff mismatch")
require("10月25日の発表とは呼ばず" in article_path.read_text(encoding="utf-8"), "date uncertainty warning absent")

utterances=script["utterances"]
require(len(utterances)==script["utterance_count"]==27, "utterance count mismatch")
for n,u in enumerate(utterances,1):
    role=u["speaker"]
    require(role in EXPECTED_SPEAKERS and (u["speaker_name"],u["speaker_id"])==EXPECTED_SPEAKERS[role], f"speaker mapping mismatch at line {n}")
    require(0<len(u["text"])<=90 and u["characters"]==len(u["text"]), f"utterance length/count invalid at line {n}")
    require(u["order"]==n, f"utterance order invalid at line {n}")
require(script["style"]=="normal" and script["speed"]=="standard", "nonstandard synthesis settings")

records=[x for x in archive["issues"] if x.get("date")==ISSUE or x.get("id")==ISSUE]
require(len(records)==1 and archive["latest_issue"]==ISSUE, "duplicate or non-latest same-day entry")
entry=records[0]
require(entry["issue_number"]==8 and entry["input_hash"], "archive identity/input hash absent")
input_script=dict(script); input_script.pop("audio",None); input_script.pop("audio_status",None)
expected_input_hash=hashlib.sha256(research_path.read_bytes()+article_path.read_bytes()+json.dumps(input_script,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
require(entry["input_hash"]==expected_input_hash, "same-day source/input hash mismatch")
require(entry["audio_status"]==script["audio_status"]=="available", "audio status mismatch")
audio=script["audio"]
primary=ROOT/"audio"/f"{ISSUE}.mp3"; backup=ROOT/"audio"/f"{ISSUE}-backup.mp3"
require(primary.is_file() and backup.is_file(), "primary or backup MP3 is missing")
require(sha(primary)==audio["sha256"]==entry["audio_sha256"], "primary MP3 SHA-256 mismatch")
require(sha(backup)==audio["backup_sha256"]==entry["audio_backup_sha256"]==sha(primary), "backup MP3 SHA-256 mismatch")
require(primary.stat().st_size==audio["file_size_bytes"]==entry["audio_file_size_bytes"], "MP3 size mismatch")
require(audio["codec"]=="mp3" and audio["bit_rate_bps"]==96000 and audio["sample_rate_hz"]==24000 and audio["channels"]==1, "MP3 media settings mismatch")
require(audio["engine"]=="VOICEVOX Nemo" and audio["engine_version"]=="0.24.0" and audio["speaker_ids"]=={"akari":10005,"naoto":10001}, "engine or voice metadata mismatch")
require(audio["human_listening_claimed"] is False and audio["full_ffmpeg_decode"]=="passed", "audio QA disclosure mismatch")
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size,bit_rate:stream=codec_name,sample_rate,channels","-of","json",str(primary)],text=True))
stream=probe["streams"][0]; fmt=probe["format"]
require(stream["codec_name"]=="mp3" and int(stream["sample_rate"])==24000 and int(stream["channels"])==1, "ffprobe stream metadata mismatch")
require(int(fmt["size"])==audio["file_size_bytes"] and abs(float(fmt["duration"])-audio["duration_seconds"])<0.02, "ffprobe duration/size mismatch")
subprocess.run(["ffmpeg","-v","error","-i",str(primary),"-f","null","-"],check=True)
subprocess.run(["ffmpeg","-v","error","-i",str(backup),"-f","null","-"],check=True)

required_providers={"OpenAI","Anthropic","Google","xAI","DeepSeek","Mistral","Cohere","Alibaba / Qwen","Meta","NVIDIA","MiniMax","Z.ai","Tencent","Baidu","Amazon Bedrock / AWS","Model-serving hosts"}
seen={x["provider"] for x in research["scope_checked"]}
require(required_providers<=seen, "research coverage list missing material provider(s)")
selected=research["selected_items"]
require(any("Kimi K3.1 Pro" in x.get("title","") or "Kimi K3.1 Pro" in x.get("finding","") for x in selected), "selected official Kimi source absent")

for path in [article_path,script_path,script_md_path,page_path,research_path,ROOT/"production"/f"{ISSUE}-research.md",ROOT/"production"/f"build-radio-{ISSUE}.mjs"]:
    require(path.is_file(), f"required production artifact absent: {path.name}")
for basename in ["index.html",f"editions/{ISSUE}.html",f"editions/{ISSUE}.md",f"editions/{ISSUE}-script.md",f"editions/{ISSUE}-script.json","editions/index.json","styles.css","app.js",f"audio/{ISSUE}.mp3",f"audio/{ISSUE}-backup.mp3"]:
    require((ROOT/"dist"/basename).is_file(), f"dist artifact missing: {basename}")
    require((ROOT/"dist"/basename).read_bytes()==(ROOT/basename).read_bytes(), f"dist/source diverged: {basename}")

for date in OLD_DATES:
    for suffix in [".md",".html","-script.md","-script.json"]:
        require((ROOT/"editions"/f"{date}{suffix}").is_file(), f"historical edition missing: {date}{suffix}")
        require((ROOT/"dist"/"editions"/f"{date}{suffix}").is_file(), f"historical dist edition missing: {date}{suffix}")
for old_audio in ["episode-001.mp3","2026-10-21.mp3",*[f"2026-10-{d:02d}{tail}.mp3" for d in range(22,25) for tail in ("","-backup")]]:
    require((ROOT/"audio"/old_audio).is_file() and (ROOT/"dist"/"audio"/old_audio).is_file(), f"historical audio missing: {old_audio}")
require((ROOT/"assets"/"ai-model-radio-hosts.png").is_file() and (ROOT/"dist"/"assets"/"ai-model-radio-hosts.png").is_file(), "existing host artwork missing")

for name in ["2026-10-25-manifest.json","2026-10-25-research.json","2026-10-25-research.md","build-radio-2026-10-25.mjs","verify-issue-2026-10-25.py","DAILY_RADIO_WORKFLOW.md"]:
    local=ROOT/"production"/name; published=ROOT/"dist"/"production"/name
    require(local.is_file() and published.is_file() and local.read_bytes()==published.read_bytes(), f"dist production artifact missing/diverged: {name}")

for filename in ["index.html",f"editions/{ISSUE}.html"]:
    source=ROOT/filename; parser=Links();parser.feed(source.read_text(encoding="utf-8"))
    require(len(parser.ids)==len(set(parser.ids)), f"duplicate HTML id in {filename}")
    for link in parser.links:
        if link.startswith(("https://","http://","mailto:","data:")): continue
        if link.startswith("#"):
            require(link[1:] in parser.ids, f"broken in-page anchor in {filename}: {link}"); continue
        resolved=(source.parent/link.split("#",1)[0].split("?",1)[0]).resolve()
        require(resolved.is_file(), f"broken local reference in {filename}: {link}")
    require(parser.audio and all("2026-10-25.mp3" in a for a in parser.audio), f"stale/missing latest audio player in {filename}")
    contents=source.read_text(encoding="utf-8")
    require("2026年10月25日" in contents and "2026-10-25" in contents, f"edition date missing in {filename}")
    for u in utterances:
        require(u["text"] in contents, f"transcript mismatch in {filename}: {u['order']}")

require("appgprj_6ad38fd59c0c819183ffff7e5b8fd482" in (ROOT/".openai"/"hosting.json").read_text(), "Site project identity changed")
manifest_path=ROOT/"production"/f"{ISSUE}-manifest.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
for name,digest in manifest["artifacts_sha256"].items():
    require((ROOT/name).is_file() and sha(ROOT/name)==digest, f"manifest artifact hash mismatch: {name}")
# Guard against accidental disclosure of environment/session paths or obvious secret material.
for filename in ["README.md", "index.html", "editions/2026-10-25.html", "editions/2026-10-25.md", "editions/2026-10-25-script.md", "editions/2026-10-25-script.json", "production/2026-10-25-manifest.json"]:
    text=(ROOT/filename).read_text(encoding="utf-8")
    require("/tmp/nemo_" not in text and "/home/agent/" not in text and "Bearer " not in text, f"local path or credential leaked in {filename}")
print("PASS: issue identity/date/cutoff, coverage, speakers/90-char limit, archive idempotency, references, MP3 hash/metadata/full decode, homepage/detail consistency, historical preservation and dist mirror")
