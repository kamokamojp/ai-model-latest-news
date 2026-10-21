#!/usr/bin/env python3
"""Verify the 2026-10-22 edition, archive links, script, and MP3 package."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-22'

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.text=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        for key in ('href','src'):
            if attrs.get(key): self.refs.append(attrs[key])
    def handle_data(self, data): self.text.append(data)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

idx_path=ROOT/'editions/index.json'
idx=json.loads(idx_path.read_text())
assert idx['latest_issue']==DATE and idx['generated_at']=='2026-10-22T08:17:39+09:00'
assert [x['id'] for x in idx['issues']]==[DATE,'2026-10-21','2026-10-20','2026-10-19','2026-10-17']
cur=idx['issues'][0]
assert cur['issue_number']==5 and cur['date']==DATE and cur['audio_status']=='available'
assert cur['audio']=='../audio/2026-10-22.mp3' and cur['audio_backup']=='../audio/2026-10-22-backup.mp3'
research=json.loads((ROOT/f'production/{DATE}-research.json').read_text())
assert research['issue_id']==DATE and research['issue_number']==5 and research['timezone']=='Asia/Tokyo'
assert research['research_cutoff']=='2026-10-22T08:17:39+09:00'
assert research['commercial_and_api_notes']['google_cloud_model_garden']['availability'].startswith('private preview')
assert research['commercial_and_api_notes']['direct_openai_api_separate_channel']['model_ids']['GPT-6 Astra']=='gpt-6-astra'
assert research['items'] and all(x['checked_on']=='2026-10-22' for x in research['items'])
script_path=ROOT/f'editions/{DATE}-script.json'
script=json.loads(script_path.read_text())
assert script['issue_id']==DATE and script['issue_date']==DATE and script['timezone']=='Asia/Tokyo'
assert script['research_cutoff']==research['research_cutoff']
assert script['style']=='normal' and script['speed']=='standard' and script['audio_status']=='available'
assert script['utterance_count']==len(script['utterances'])==28
assert max(len(u['text']) for u in script['utterances'])<=90
assert all(u['characters']==len(u['text']) for u in script['utterances'])
assert all(u['speaker_id']==(10005 if u['speaker']=='akari' else 10001) for u in script['utterances'])
assert all(u['speaker_name']==('あかり' if u['speaker']=='akari' else 'なおと') for u in script['utterances'])
assert {u['speaker'] for u in script['utterances']}=={'akari','naoto'}
assert script['audio']['file']=='../audio/2026-10-22.mp3'
assert script['audio']['backup_file']=='../audio/2026-10-22-backup.mp3'
assert script['audio']['backup_sha256']==script['audio']['sha256']

article_md=(ROOT/f'editions/{DATE}.md').read_text()
script_md=(ROOT/f'editions/{DATE}-script.md').read_text()
html_path=ROOT/f'editions/{DATE}.html'
home_path=ROOT/'index.html'
for txt in (article_md,script_md,html_path.read_text(),home_path.read_text()):
    assert DATE in txt
for u in script['utterances']:
    assert u['text'] in script_md
    assert u['text'] in html_path.read_text()
    assert u['text'] in home_path.read_text()
for x in research['items']:
    assert x['url'] in html_path.read_text()
assert '第5号の音声' in html_path.read_text() and '第5号の台本' in home_path.read_text()
assert 'VOICEVOX Nemo' in html_path.read_text() and 'audio/2026-10-22.mp3' in home_path.read_text()
assert 'audio/2026-10-22-backup.mp3' in html_path.read_text() and 'audio/2026-10-22-backup.mp3' in home_path.read_text()
assert (ROOT/'assets/ai-model-radio-hosts.png').exists()

# Resolve all local HTML references; external URLs, data URIs and in-page anchors are excluded.
for page in (home_path,html_path):
    parser=RefParser(); parser.feed(page.read_text())
    for ref in parser.refs:
        parsed=urlparse(ref)
        if parsed.scheme or ref.startswith('#') or not parsed.path: continue
        target=(page.parent/parsed.path).resolve()
        assert target.exists(), f'broken ref in {page.relative_to(ROOT)}: {ref}'

# New files and mirrored package must match; historical files and their original audio stay present.
for rel in [f'editions/{DATE}.md',f'editions/{DATE}-script.md',f'editions/{DATE}-script.json',f'editions/{DATE}.html',f'production/{DATE}-research.json',f'production/{DATE}-research.md',f'production/{DATE}-manifest.json',f'production/build-radio-{DATE}.mjs',f'production/verify-issue-{DATE}.py']:
    assert (ROOT/rel).exists(), f'missing {rel}'
    mirrored=ROOT/'dist'/rel
    assert mirrored.exists() and (ROOT/rel).read_bytes()==mirrored.read_bytes(), f'dist mismatch: {rel}'
for rel in ['index.html','editions/index.json','audio/2026-10-22-provenance.json']:
    assert (ROOT/'dist'/rel).read_bytes()==(ROOT/rel).read_bytes(), f'dist mismatch: {rel}'
for d in ['2026-10-19','2026-10-20','2026-10-21']:
    assert (ROOT/f'editions/{d}.html').exists() and (ROOT/f'dist/editions/{d}.html').exists()
assert (ROOT/'audio/2026-10-21.mp3').exists() and (ROOT/'dist/audio/2026-10-21.mp3').exists()
assert (ROOT/'audio/episode-001.mp3').exists() and (ROOT/'dist/audio/episode-001.mp3').exists()

mp3=ROOT/f'audio/{DATE}.mp3'; dist_mp3=ROOT/f'dist/audio/{DATE}.mp3'
backup=ROOT/f'audio/{DATE}-backup.mp3'; dist_backup=ROOT/f'dist/audio/{DATE}-backup.mp3'
assert mp3.exists() and dist_mp3.exists() and mp3.read_bytes()==dist_mp3.read_bytes()
assert backup.exists() and dist_backup.exists() and backup.read_bytes()==mp3.read_bytes()==dist_backup.read_bytes()
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,format_name:stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(mp3)]))
stream=info['streams'][0]
assert stream['codec_name']=='mp3' and stream['sample_rate']=='24000' and stream['channels']==1 and stream['bit_rate']=='96000'
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(mp3),'-f','null','-'],check=True)
subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(backup),'-f','null','-'],check=True)
assert sha(mp3)==script['audio']['sha256']==sha(backup)==script['audio']['backup_sha256']
manifest=json.loads((ROOT/f'production/{DATE}-manifest.json').read_text())
assert manifest['audio']['sha256']==sha(mp3) and manifest['audio']['full_ffmpeg_decode']=='passed'
assert manifest['audio']['backup_path']=='audio/2026-10-22-backup.mp3'
assert manifest['audio']['backup_sha256']==sha(backup) and manifest['audio']['backup_status']=='available'
assert manifest['audio']['public_url']=='https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-22.mp3'
assert manifest['audio']['backup_public_url']=='https://ai-model-latest-radio.kamokamojp.chatgpt.site/audio/2026-10-22-backup.mp3'
assert manifest['input_hash']==idx['issues'][0]['input_hash']
for name,digest in manifest['files_sha256'].items():
    candidates=[ROOT/name, ROOT/'editions'/name, ROOT/'production'/name, ROOT/'audio'/name]
    file=next((p for p in candidates if p.exists()),None)
    assert file is not None and sha(file)==digest, f'manifest hash mismatch: {name}'
secret_patterns=[re.compile(p,re.I) for p in [r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'Bearer\s+[A-Za-z0-9._~-]{16,}',r'Authorization\s*:',r'/home/agent/[^\s]+',r'https?://[^\s]*token=[^\s]+']]
public_files=[ROOT/'index.html',ROOT/f'editions/{DATE}.html',ROOT/f'editions/{DATE}.md',ROOT/f'editions/{DATE}-script.md',ROOT/f'editions/{DATE}-script.json',ROOT/f'production/{DATE}-research.json',ROOT/f'production/{DATE}-research.md',ROOT/f'production/{DATE}-manifest.json',ROOT/f'production/build-radio-{DATE}.mjs']
for f in public_files:
    text=f.read_text()
    assert not any(p.search(text) for p in secret_patterns), f'secret/internal-path pattern in {f.name}'
print('PASS: issue/date/timezone, source links, script/speakers, primary+backup MP3 metadata/decode/hash, history, mirrors, and public-output scan')
