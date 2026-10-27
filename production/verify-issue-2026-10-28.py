#!/usr/bin/env python3
"""Validate issue 11 content, pending audio policy, links, index, and archive retention."""
import json,hashlib,pathlib,re,sys,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]; D='2026-10-28'; DIST=ROOT/'dist'
def read(p): return p.read_text(encoding='utf-8')
def need(x,msg):
    if not x: raise SystemExit('FAIL: '+msg)
idx=json.loads(read(ROOT/'editions/index.json')); rows=[x for x in idx['issues'] if x.get('id')==D]
need(len(rows)==1,'exactly one current issue row'); row=rows[0]
script=json.loads(read(ROOT/f'editions/{D}-script.json')); research=json.loads(read(ROOT/f'production/{D}-research.json')); manifest=json.loads(read(ROOT/f'production/{D}-manifest.json'))
need(idx['latest_issue']==D,'latest issue'); need(row['issue_number']==11,'issue number'); need(row['audio_status']=='pending' and row.get('audio') is None,'pending audio null')
need(script['issue_number']==11 and script['issue_date']==D and script['timezone']=='Asia/Tokyo','issue date/timezone')
need(script['research_cutoff'].endswith('+09:00') and script['research_cutoff_utc'].endswith('Z'),'cutoff with timezone')
need(script['style']=='normal' and script['speed']=='standard' and script['max_characters_per_utterance']==90,'voice config')
need(script['speaker_reference']['akari']['speaker_id']==10005 and script['speaker_reference']['naoto']['speaker_id']==10001,'voice IDs')
need(script['utterance_count']==len(script['utterances'])>0,'turn count')
for i,u in enumerate(script['utterances'],1):
    need(u['order']==i and u['speaker_id']==(10005 if u['speaker']=='akari' else 10001),f'speaker id/order {i}')
    need(u['characters']==len(u['text'])<=90,f'utterance length {i}')
art=read(ROOT/f'editions/{D}.md'); script_md=read(ROOT/f'editions/{D}-script.md'); page=read(ROOT/f'editions/{D}.html'); home=read(ROOT/'index.html')
need('2026年10月28日' in art and 'GPT-6.1 Terra' in art and 'DeepSeek' in art and 'Cohere' in art and 'Mistral' in art,'article headlines')
need('2026-10-28 08:04:15 JST' in art and '23:04:15 UTC' in art,'research cutoff')
need('pending' in row['audio_status'] and '音声は準備中' in page and '前号の音声はこの号のプレーヤーには使用していません' in page,'audio pending status')
need('<audio' not in page and '<audio' not in home and 'audio/2026-10-28.mp3' not in page+home,'no dead/old audio player')
for u in script['utterances']:
    need(u['text'].replace("`", "") in script_md.replace("`", "") and u['text'] in page and u['text'] in home,'script matches published HTML/MD')
need('ISSUE 011' in home and 'ISSUE 001' in home and 'episode-001.mp3' in home,'new + issue001 home')
need(len(idx['issues'])>=10,'old archive rows preserved')
need(any(x.get('id')=='2026-10-27' for x in idx['issues']),'previous issue preserved')
need(any(x.get('id')=='2026-10-17' for x in idx['issues']),'issue 001 record preserved')
need(len(research['items'])>=8 and all(x.get('primary_source') for x in research['items']),'source coverage & URLs')
need(any(x['company']=='Anthropic' and not x['selected'] for x in research['items']),'checked but not selected')
need(manifest['audio']['status']=='pending' and manifest['audio']['file'] is None,'manifest pending audio')
# required outputs
paths=['editions/2026-10-28.md','editions/2026-10-28-script.md','editions/2026-10-28-script.json','editions/2026-10-28.html','editions/index.json','production/2026-10-28-research.json','production/2026-10-28-research.md','production/2026-10-28-manifest.json','production/build-radio-2026-10-28.mjs','production/verify-issue-2026-10-28.py','index.html']
for p in paths:
    need((ROOT/p).exists(),f'missing {p}'); need((DIST/p).exists(),f'missing dist/{p}'); need((ROOT/p).read_bytes()==(DIST/p).read_bytes(),f'dist mirror differs: {p}')
# local links on homepage and issue page
from urllib.parse import urlparse
for file in [ROOT/'index.html',ROOT/f'editions/{D}.html']:
    src=read(file); ids=set(re.findall(r'\bid="([^"]+)"',src))
    for a in re.findall(r'\bhref="#([^"]+)"',src): need(a in ids,f'broken anchor {a} in {file.name}')
    for _,url in re.findall(r'\b(href|src)="([^"]+)"',src):
        q=urlparse(url)
        if q.scheme or url.startswith('#') or url.startswith('mailto:'): continue
        target=(file.parent/q.path).resolve()
        need(target.exists(),f'broken local reference {url} in {file.name}')
# ensure no accidental new/overwritten historical MP3
need(not (ROOT/'audio/2026-10-28.mp3').exists() and not (ROOT/'audio/2026-10-28-backup.mp3').exists(),'no stale/current MP3 present')
print('PASS: issue/date/cutoff, source record, script 90-char cap/voices, pending audio, HTML links, archive preservation, required files and dist sync.')
