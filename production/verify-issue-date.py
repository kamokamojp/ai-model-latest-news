#!/usr/bin/env python3
"""Validate the daily AI model radio issue and preservation of the existing archive."""
import json, hashlib, pathlib, re, sys, subprocess, shutil, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]; D='2026-10-27'; dist=ROOT/'dist'
def read(p): return p.read_text(encoding='utf-8')
def need(ok,msg):
 if not ok: raise SystemExit('FAIL: '+msg)
idx=json.loads(read(ROOT/'editions/index.json')); script=json.loads(read(ROOT/f'editions/{D}-script.json')); research=json.loads(read(ROOT/f'production/{D}-research.json')); manifest=json.loads(read(ROOT/f'production/{D}-manifest.json'))
need(idx['latest_issue']==D,'latest issue ID')
rows=[x for x in idx['issues'] if x.get('id')==D]; need(len(rows)==1,'exactly one same-day index record'); row=rows[0]
need(row['issue_number']==10 and row['date']==D,'issue number/date')
need(manifest['idempotency']['same_day_record_count']==0,'pre-authoring idempotency count')
need(research['same_day_existing_issue_count']==0,'research idempotency count')
need(script['issue_id']==D and script['issue_date']==D and script['timezone']=='Asia/Tokyo','script date and timezone')
need(script['research_cutoff_utc'].endswith('Z') and script['research_cutoff'].endswith('+09:00'),'research cutoff UTC and JST')
need(script['scheduled_target_cutoff']=='2026-10-27T08:00:00+09:00','scheduled JST cutoff')
need(script['previous_issue_cutoff']=='2026-10-26T08:14:18+09:00','prior issue cutoff')
need(script['style']=='normal' and script['speed']=='standard','standard style/rate')
need(script['speaker_reference']['akari']['speaker_id']==10005 and script['speaker_reference']['naoto']['speaker_id']==10001,'speaker IDs')
need(script['utterance_count']==len(script['utterances'])>0,'utterance count')
for i,u in enumerate(script['utterances'],1):
 need(u['order']==i and u['speaker_id']==(10005 if u['speaker']=='akari' else 10001),f'speaker/style ID at line {i}')
 need(len(u['text'])<=90 and u['characters']==len(u['text']),f'90-character limit/count line {i}')
art=read(ROOT/f'editions/{D}.md'); page=read(ROOT/f'editions/{D}.html'); home=read(ROOT/'index.html')
need('GPT-6.1 Terra' in art and 'Gemini API' in art and '10月26日' in art,'article key stories')
need('2026年10月27日' in art and '08:07:05 JST' in art and '23:07:05 UTC' in art,'date and cutoff in article')
need('前号' in art and '時刻・タイムゾーン' in art,'date-only chronology caveat')
need('gpt-6.1-terra' in page and 'store=false' in page and 'OpenMDW' in page,'detail claims')
need('audio/2026-10-27.mp3' in page and '../audio/2026-10-27.mp3' in page,'detail current audio URLs')
need('<audio controls' in page and '<audio controls' in home,'ready audio players')
for u in script['utterances']:
 need(u['text'] in page and u['text'] in home,f'article/transcript script match: {u["order"]}')
need('音声を聴く' in home and '音声準備中' not in home,'archive card shows ready issue audio')
need('ISSUE 010' in home and '2026-10-27' in home and '2026-10-26' in home,'homepage issue and archive')
need('ISSUE 001' in home and 'episode-001.mp3' in home,'issue 001 preservation')
need('NVIDIA' in research['coverage_inventory'][10]['provider'],'research coverage includes vendors')
need(len(research['coverage_inventory'])>=18,'coverage inventory breadth')
for path in ['editions/2026-10-27.md','editions/2026-10-27-script.md','editions/2026-10-27-script.json','editions/2026-10-27.html','editions/index.json','production/2026-10-27-research.json','production/2026-10-27-research.md','production/2026-10-27-manifest.json','production/build-radio-date.mjs','production/verify-issue-date.py']:
 need((ROOT/path).exists(),f'required file {path}')
 need((dist/path).exists(),f'dist mirror {path}')
 need((ROOT/path).read_bytes()==(dist/path).read_bytes(),f'root/dist mirror match {path}')
# Check local relative links/assets and in-page anchors on today's homepage and detail.
for file in [ROOT/'index.html',ROOT/f'editions/{D}.html']:
 src=read(file); ids=set(re.findall(r'\bid="([^"]+)"',src))
 for anchor in re.findall(r'\bhref="#([^"]+)"',src): need(anchor in ids,f'broken in-page anchor in {file.relative_to(ROOT)}: #{anchor}')
# Check local relative links/assets on today's homepage and detail. External and in-page links are exempt.
from urllib.parse import urlparse
for file in [ROOT/'index.html',ROOT/f'editions/{D}.html']:
 src=read(file)
 for attr,url in re.findall(r'\b(href|src)="([^"]+)"',src):
  parsed=urlparse(url)
  if parsed.scheme or url.startswith('#') or url.startswith('mailto:'): continue
  target=(file.parent/parsed.path).resolve()
  need(target.exists(),f'broken relative {attr} link in {file.relative_to(ROOT)}: {url}')
# Audio is optional only while status is pending; never substitute an old issue's MP3.
if script.get('audio_status')=='available':
 audio=script.get('audio'); need(audio and audio['file']=='../audio/2026-10-27.mp3','correct issue audio path')
 primary=ROOT/'audio/2026-10-27.mp3'; backup=ROOT/'audio/2026-10-27-backup.mp3'
 need(primary.exists() and backup.exists(),'primary and backup MP3 exist')
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 need(h(primary)==h(backup)==audio['sha256']==audio['backup_sha256'],'primary/backup MP3 hashes')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,bit_rate:stream=codec_name,sample_rate,channels','-of','json',str(primary)]))
 st=probe['streams'][0]; need(st['codec_name']=='mp3' and st['sample_rate']=='24000' and st['channels']==1,'MP3 codec/sample-rate/channels')
 need(abs(int(probe['format']['bit_rate'])-96000)<5000,'MP3 approximately 96 kbps')
 subprocess.run(['ffmpeg','-v','error','-i',str(primary),'-f','null','-'],check=True)
 for filename in ['2026-10-27.mp3','2026-10-27-backup.mp3']:
  need((dist/'audio'/filename).exists(),'dist audio exists: '+filename)
 need((dist/'audio/2026-10-27.mp3').read_bytes()==primary.read_bytes(),'dist primary audio identical')
 need('controls' in home and 'audio/2026-10-27.mp3' in home,'homepage player published only after audio')
 need('<audio controls' in page and 'audio/2026-10-27.mp3' in page,'detail player published only after audio')
else:
 need(script.get('audio') is None and row.get('audio') is None,'pending audio fields are null')
 print('AUDIO PENDING: publication must show explicit pending state; do not reuse prior audio.')
print('PASS: issue/date/TZ, idempotency, coverage, script limits/style IDs, source/article HTML, required files, old archive preservation and local references.')
if script.get('audio_status')=='available': print('PASS: MP3 metadata/hash/backup/full ffmpeg decode and dist audio.')
