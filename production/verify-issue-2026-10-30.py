#!/usr/bin/env python3
"""Validate the 2026-10-30 AI model radio issue (GitHub Pages edition, no dist mirror)."""
import json, hashlib, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; D='2026-10-30'
def read(p): return p.read_text(encoding='utf-8')
def need(ok,msg):
    if not ok: raise SystemExit('FAIL: '+msg)
idx=json.loads(read(ROOT/'editions/index.json')); script=json.loads(read(ROOT/f'editions/{D}-script.json'))
research=json.loads(read(ROOT/f'production/{D}-research.json')); manifest=json.loads(read(ROOT/f'production/{D}-manifest.json'))
need(idx['latest_issue']==D,'latest issue ID')
rows=[x for x in idx['issues'] if x.get('id')==D]; need(len(rows)==1,'exactly one same-day index record'); row=rows[0]
need(row['issue_number']==13 and row['date']==D,'issue number/date')
need(manifest['idempotency']['same_day_record_count']==0,'pre-authoring idempotency count')
need(research['same_day_existing_issue_count']==0,'research idempotency count')
need(script['issue_id']==D and script['issue_date']==D and script['timezone']=='Asia/Tokyo','script date/timezone')
need(script['research_cutoff_utc'].endswith('Z') and script['research_cutoff'].endswith('+09:00'),'cutoff formats')
need(script['scheduled_target_cutoff']=='2026-10-30T08:00:00+09:00','scheduled cutoff')
need(script['previous_issue_cutoff']=='2026-10-29T08:40:27+09:00','prior cutoff')
need(script['style']=='normal' and script['speed']=='standard','style/speed')
need(script['speaker_reference']['akari']['speaker_id']==10005 and script['speaker_reference']['naoto']['speaker_id']==10001,'speaker IDs')
need(script['utterance_count']==len(script['utterances'])>0,'utterance count')
for i,u in enumerate(script['utterances'],1):
    need(u['order']==i and u['speaker_id']==(10005 if u['speaker']=='akari' else 10001),f'speaker ID line {i}')
    need(len(u['text'])<=90 and u['characters']==len(u['text']),f'90-char limit line {i}')
art=read(ROOT/f'editions/{D}.md'); page=read(ROOT/f'editions/{D}.html')
need('Ling-3.1-flash' in art and '128 MB' in art,'article key stories')
need('2026年10月30日' in art and '08:38:34 JST' in art and '23:38:34 UTC' in art,'date/cutoff in article')
need('前号' in art and '時刻・タイムゾーン' in art,'date-only caveat')
need('Ling-3.1-flash' in page and '128 MB' in page,'detail claims')
need('audio/2026-10-30.mp3' in page and '../audio/2026-10-30.mp3' in page,'detail audio URLs')
need('<audio controls' in page,'detail player')
for u in script['utterances']:
    need(u['text'] in page,f'transcript match: {u["order"]}')
for p in [f'editions/{D}.md',f'editions/{D}-script.md',f'editions/{D}-script.json',f'editions/{D}.html','editions/index.json',
          f'production/{D}-research.json',f'production/{D}-research.md',f'production/{D}-manifest.json',
          'production/build-radio-2026-10-30.mjs','production/verify-issue-2026-10-30.py']:
    need((ROOT/p).exists(),f'required file {p}')
# local relative links in detail page (../styles.css, ../app.js, ../assets/*, ../index.html live in the Pages tree, not staging)
from urllib.parse import urlparse
src=page; ids=set(re.findall(r'\bid="([^"]+)"',src))
for a in re.findall(r'\bhref="#([^"]+)"',src): need(a in ids,f'broken anchor #{a}')
PAGES_TREE={'../styles.css','../app.js','../index.html'}
for attr,url in re.findall(r'\b(href|src)="([^"]+)"',src):
    parsed=urlparse(url)
    if parsed.scheme or url.startswith('#') or url in PAGES_TREE or parsed.path.startswith('../assets/'): continue
    if parsed.path.startswith('../'): target=(ROOT/parsed.path[3:]).resolve()
    else: target=(ROOT/'editions'/parsed.path).resolve()
    need(target.exists(),f'broken relative {attr} {url}')
if script.get('audio_status')=='available':
    audio=script.get('audio'); need(audio and audio['file']=='../audio/2026-10-30.mp3','audio path')
    primary=ROOT/'audio/2026-10-30.mp3'; backup=ROOT/'audio/2026-10-30-backup.mp3'
    need(primary.exists() and backup.exists(),'MP3s exist')
    h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    need(h(primary)==h(backup)==audio['sha256']==audio['backup_sha256'],'MP3 hashes')
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,bit_rate:stream=codec_name,sample_rate,channels','-of','json',str(primary)]))
    st=probe['streams'][0]; need(st['codec_name']=='mp3' and st['sample_rate']=='24000' and st['channels']==1,'MP3 codec/sr/ch')
    need(abs(int(probe['format']['bit_rate'])-96000)<5000,'~96kbps')
    subprocess.run(['ffmpeg','-v','error','-i',str(primary),'-f','null','-'],check=True)
print('PASS: No.13 issue/date/TZ, idempotency, coverage, script limits/IDs, article/HTML, required files, local refs, MP3 hash/decode/backup.')
