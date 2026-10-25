#!/usr/bin/env python3
"""Local reproducible QA for AI Model Latest Radio issue 2026-10-26."""
from __future__ import annotations
import hashlib, json, subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-26'; NUM=9
SPEAKERS={'akari':('あかり',10005),'naoto':('なおと',10001)}
def require(ok,msg):
    if not ok: raise AssertionError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.refs=[]; self.audios=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        for k in ('href','src'):
            if a.get(k): self.refs.append(a[k])
        if tag=='audio' and a.get('src'): self.audios.append(a['src'])
script=json.loads((ROOT/'editions'/f'{DATE}-script.json').read_text(encoding='utf-8'))
research=json.loads((ROOT/'production'/f'{DATE}-research.json').read_text(encoding='utf-8'))
archive=json.loads((ROOT/'editions/index.json').read_text(encoding='utf-8'))
article=(ROOT/'editions'/f'{DATE}.md').read_text(encoding='utf-8')
require(script['issue_id']==DATE and script['issue_date']==DATE and script['issue_number']==NUM,'issue identity mismatch')
require(script['timezone']=='Asia/Tokyo' and script['scheduled_target_cutoff']=='2026-10-26T08:00+09:00','date/timezone mismatch')
require(script['research_cutoff']==research['research_cutoff']=='2026-10-26T08:14:18+09:00','research cutoff mismatch')
require(research['research_cutoff_utc']=='2026-10-25T23:14:18Z','UTC cutoff mismatch')
require(research['previous_issue_cutoff']=='2026-10-25T08:07+09:00','previous issue cutoff mismatch')
require('10月24日' in article and '時刻・タイムゾーン' in article,'date uncertainty treatment missing')
require(len(script['utterances'])==script['utterance_count'] and len(script['utterances'])>0,'utterance count mismatch')
for i,u in enumerate(script['utterances'],1):
    role=u['speaker']; require(role in SPEAKERS and (u['speaker_name'],u['speaker_id'])==SPEAKERS[role],f'speaker mismatch line {i}')
    require(0<len(u['text'])<=90 and u['characters']==len(u['text']),f'utterance length/count line {i}')
    require(u['order']==i,f'utterance order line {i}')
require(script['style']=='normal' and script['speed']=='standard','synthesis settings mismatch')
records=[e for e in archive['issues'] if e.get('date')==DATE or e.get('id')==DATE]
require(len(records)==1 and archive['latest_issue']==DATE,'duplicate/non-latest archive entry')
entry=records[0]; require(entry['issue_number']==NUM,'archive issue number mismatch')
input_script=dict(script); input_script.pop('audio',None); input_script.pop('audio_status',None); input_script.pop('audio_run_not_claimed_as_listened',None)
input_hash=hashlib.sha256((ROOT/'production'/f'{DATE}-research.json').read_bytes()+(ROOT/'editions'/f'{DATE}.md').read_bytes()+json.dumps(input_script,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
require(entry['input_hash']==input_hash,'source/input hash mismatch')
require(script['audio_status']==entry['audio_status']=='available','audio status mismatch')
a=script['audio']; primary=ROOT/'audio'/f'{DATE}.mp3'; backup=ROOT/'audio'/f'{DATE}-backup.mp3'
require(primary.is_file() and backup.is_file(),'missing primary/backup audio')
require(sha(primary)==a['sha256']==entry['audio_sha256'],'primary SHA mismatch')
require(sha(backup)==a['backup_sha256']==entry['audio_backup_sha256']==sha(primary),'backup SHA mismatch')
require(primary.stat().st_size==a['file_size_bytes']==entry['audio_file_size_bytes'],'audio size mismatch')
require(a['codec']=='mp3' and a['bit_rate_bps']==96000 and a['sample_rate_hz']==24000 and a['channels']==1,'audio media settings mismatch')
require(a['engine']=='VOICEVOX Nemo' and a['engine_version']=='0.24.0' and a['speaker_ids']=={'akari':10005,'naoto':10001},'engine/voices mismatch')
require(a['short_sample_full_decode']=='passed' and a['full_ffmpeg_decode']=='passed' and a['human_listening_claimed'] is False,'audio QA claim mismatch')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,sample_rate,channels','-of','json',str(primary)],text=True))
stream=probe['streams'][0]; fmt=probe['format']
require(stream['codec_name']=='mp3' and int(stream['sample_rate'])==24000 and int(stream['channels'])==1,'ffprobe stream mismatch')
require(int(fmt['size'])==a['file_size_bytes'] and abs(float(fmt['duration'])-a['duration_seconds'])<0.02,'ffprobe size/duration mismatch')
subprocess.run(['ffmpeg','-v','error','-i',str(primary),'-f','null','-'],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(backup),'-f','null','-'],check=True)
required={'OpenAI','Anthropic','Google','xAI','DeepSeek','Mistral','Cohere','Alibaba / Qwen','Moonshot AI / Kimi','Meta','NVIDIA','MiniMax','Z.ai','Tencent','Baidu','Amazon Bedrock / AWS','Volcengine / Ark','Model-serving hosts'}
require(required<={x['provider'] for x in research['scope_checked']},'scope inventory incomplete')
selected=research['selected_items']
require(any('Anthropic' in x['publisher'] for x in selected) and any('Volcengine' in x['publisher'] for x in selected),'selected primary evidence missing')
for file in [f'editions/{DATE}.md',f'editions/{DATE}-script.md',f'editions/{DATE}-script.json',f'editions/{DATE}.html',f'production/{DATE}-research.json',f'production/{DATE}-research.md',f'production/build-radio-{DATE}.mjs']:
    require((ROOT/file).is_file(),f'required production artifact absent: {file}')
for file in ['index.html',f'editions/{DATE}.html',f'editions/{DATE}.md',f'editions/{DATE}-script.md',f'editions/{DATE}-script.json','editions/index.json','styles.css','app.js',f'audio/{DATE}.mp3',f'audio/{DATE}-backup.mp3',f'production/{DATE}-research.json',f'production/{DATE}-research.md',f'production/{DATE}-manifest.json',f'production/build-radio-{DATE}.mjs',f'production/verify-issue-{DATE}.py']:
    dist=ROOT/'dist'/file; local=ROOT/file
    require(dist.is_file() and dist.read_bytes()==local.read_bytes(),f'dist missing/diverged: {file}')
# Preserve previous editions and MP3s.
for day in range(19,26):
    d=f'2026-10-{day:02d}'
    for suffix in ('.md','.html','-script.md','-script.json'):
        require((ROOT/'editions'/f'{d}{suffix}').is_file(),f'historical edition missing: {d}{suffix}')
        require((ROOT/'dist/editions'/f'{d}{suffix}').is_file(),f'historical dist edition missing: {d}{suffix}')
for name in ['episode-001.mp3','2026-10-21.mp3',*[f'2026-10-{d:02d}{tail}.mp3' for d in range(22,26) for tail in ('','-backup')]]:
    require((ROOT/'audio'/name).is_file() and (ROOT/'dist/audio'/name).is_file(),f'historical audio missing: {name}')
require((ROOT/'assets/ai-model-radio-hosts.png').is_file() and (ROOT/'dist/assets/ai-model-radio-hosts.png').is_file(),'issue 001 host artwork missing')
for file in ['index.html',f'editions/{DATE}.html']:
    p=ROOT/file; parser=Links(); text=p.read_text(encoding='utf-8'); parser.feed(text)
    require(len(parser.ids)==len(set(parser.ids)),f'duplicate HTML id in {file}')
    for ref in parser.refs:
        if ref.startswith(('https://','http://','mailto:','data:')): continue
        if ref.startswith('#'):
            require(ref[1:] in parser.ids,f'broken local anchor {file}: {ref}'); continue
        target=(p.parent/ref.split('#',1)[0].split('?',1)[0]).resolve()
        require(target.is_file(),f'broken local reference {file}: {ref}')
    require(parser.audios and all(f'{DATE}.mp3' in src for src in parser.audios),f'wrong/missing current player in {file}')
    require('2026年10月26日' in text and '2026-10-26' in text,f'issue date missing in {file}')
    for u in script['utterances']: require(u['text'] in text,f'transcript mismatch {file} line {u["order"]}')
print('PASS: issue identity, JST/UTC cutoffs, research scope, utterance IDs/lengths, archive idempotency, source/input hash, audio SHA/metadata/full decode, local links, homepage/detail transcript, historical preservation, and dist mirror')
