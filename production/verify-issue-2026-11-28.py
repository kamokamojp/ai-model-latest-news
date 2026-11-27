#!/usr/bin/env python3
"""Validate the 2026-11-28 AI model radio issue (GitHub Pages edition, no dist mirror)."""
import json, hashlib, pathlib, re, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]; D = '2026-11-28'
def read(p): return p.read_text(encoding='utf-8')
def need(ok, msg):
    if not ok: raise SystemExit('FAIL: ' + msg)
idx = json.loads(read(ROOT / 'editions/index.json')); script = json.loads(read(ROOT / f'editions/{D}-script.json'))
research = json.loads(read(ROOT / f'production/{D}-research.json')); manifest = json.loads(read(ROOT / f'production/{D}-manifest.json'))
need(idx['latest_issue'] == D, 'latest issue ID')
rows = [x for x in idx['issues'] if x.get('id') == D]; need(len(rows) == 1, 'exactly one same-day index record'); row = rows[0]
need(row['issue_number'] == 42 and row['date'] == D, 'issue number/date')
need(manifest['idempotency']['same_day_record_count'] == 0, 'pre-authoring idempotency count')
need(research['same_day_existing_issue_count'] == 0, 'research idempotency count')
need(script['issue_id'] == D and script['issue_date'] == D and script['timezone'] == 'Asia/Tokyo', 'script date/timezone')
need(script['research_cutoff_utc'].endswith('Z') and script['research_cutoff'].endswith('+09:00'), 'cutoff formats')
need(script['scheduled_target_cutoff'] == '2026-11-28T08:00:00+09:00', 'scheduled cutoff')
need(script['previous_issue_cutoff'] == '2026-11-27T04:15:00+09:00', 'prior cutoff')
need(script['style'] == 'normal' and script['speed'] == 'standard', 'style/speed')
need(script['speaker_reference']['akari']['speaker_id'] == 10005 and script['speaker_reference']['naoto']['speaker_id'] == 10001, 'speaker IDs')
need(script['utterance_count'] == len(script['utterances']) > 0, 'utterance count')
for i, u in enumerate(script['utterances'], 1):
    need(u['order'] == i and u['speaker_id'] == (10005 if u['speaker'] == 'akari' else 10001), f'speaker ID line {i}')
    need(len(u['text']) <= 90 and u['characters'] == len(u['text']), f'90-char limit line {i}')
art = read(ROOT / f'editions/{D}.md'); page = read(ROOT / f'editions/{D}.html')
for kw in ['LingBot', 'DFly2', 'Raon-1 mini', 'Soma-1X Lite', 'Nemotron-Labs-Image']:
    need(kw in art, f'article story {kw}'); need(kw in page, f'page story {kw}')
need('2026年11月28日' in art and '04:11 JST' in art, 'date/cutoff in article')
need('前号' in art and 'タイムゾーンを推測していません' in art, 'date-only caveat')
need('../audio/2026-11-28.mp3' in page, 'detail audio URL')
need('<audio controls' in page, 'detail player')
for u in script['utterances']:
    need(u['text'] in page, f'transcript match: {u["order"]}')
top = read(ROOT / 'index.html')
need('2026-11-28' in top and '第42号' in top, 'top page date/number')
need('editions/2026-11-09.html' in top and 'editions/2026-11-27.html' in top and 'editions/2026-11-28.html' in top, 'top archive keeps old and adds No.42')
for p in [f'editions/{D}.md', f'editions/{D}-script.md', f'editions/{D}-script.json', f'editions/{D}.html', 'editions/index.json',
          f'production/{D}-research.json', f'production/{D}-research.md', f'production/{D}-manifest.json',
          'production/build-radio-2026-11-28.mjs', 'production/verify-issue-2026-11-28.py', 'index.html']:
    need((ROOT / p).exists(), f'required file {p}')
from urllib.parse import urlparse
ids = set(re.findall(r'\bid="([^"]+)"', page))
for a in re.findall(r'\bhref="#([^"]+)"', page): need(a in ids, f'broken anchor #{a}')
PAGES_TREE = {'../styles.css', '../app.js', '../index.html'}
for attr, url in re.findall(r'\b(href|src)="([^"]+)"', page):
    parsed = urlparse(url)
    if parsed.scheme or url.startswith('#') or url in PAGES_TREE or parsed.path.startswith('../assets/'): continue
    target = (ROOT / parsed.path[3:]).resolve() if parsed.path.startswith('../') else (ROOT / 'editions' / parsed.path).resolve()
    need(target.exists(), f'broken relative {attr} {url}')
synth = manifest['idempotency']['synthesis_input_script_sha256']
need(top.count(synth) == 2, f'top page SHA notes ({top.count(synth)} != 2)')
need('__SHA__' not in top and '__DURATION__' not in top, 'no placeholders left in top HTML')
need('__SHA__' not in page and '__DURATION__' not in page, 'no placeholders left in detail HTML')
need(manifest['audio']['sha256'] == row['audio_sha256'], 'manifest/index audio hash agree')
if script.get('audio_status') == 'available':
    audio = script.get('audio'); need(audio and audio['file'] == '../audio/2026-11-28.mp3', 'audio path')
    primary = ROOT / 'audio/2026-11-28.mp3'; backup = ROOT / 'audio/2026-11-28-backup.mp3'
    need(primary.exists() and backup.exists(), 'MP3s exist')
    h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    need(h(primary) == h(backup) == audio['sha256'] == audio['backup_sha256'], 'MP3 hashes')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate:stream=codec_name,sample_rate,channels', '-of', 'json', str(primary)]))
    st = probe['streams'][0]; need(st['codec_name'] == 'mp3' and st['sample_rate'] == '24000' and st['channels'] == 1, 'MP3 codec/sr/ch')
    need(abs(int(probe['format']['bit_rate']) - 96000) < 5000, '~96kbps')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(primary), '-f', 'null', '-'], check=True)
print('PASS: No.42 issue/date/TZ, idempotency, coverage, script limits/IDs, article/HTML, required files, local refs, top SHA notes, MP3 hash/decode/backup.')
