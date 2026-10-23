#!/usr/bin/env python3
"""Verify issue #7 source, date caveats, script, references, archive and mirrors."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-24'
CUTOFF='2026-10-24T08:10:58+09:00'
CUTOFF_UTC='2026-10-23T23:10:58Z'
PREVIOUS='2026-10-23T08:42:19+09:00'
SITE='https://ai-model-latest-radio.kamokamojp.chatgpt.site'

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.audio=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for k in ('href','src'):
            if a.get(k): self.refs.append(a[k])
        if tag=='audio': self.audio.append(a)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check_refs(page):
    q=RefParser(); q.feed(page.read_text(encoding='utf-8'))
    for ref in q.refs:
        u=urlparse(ref)
        if u.scheme or ref.startswith('#') or not u.path: continue
        assert (page.parent/u.path).resolve().exists(), f'broken local reference {page.relative_to(ROOT)}: {ref}'
    return q

def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))

idx=load('editions/index.json')
researchp=ROOT/f'production/{DATE}-research.json'; research=json.loads(researchp.read_text(encoding='utf-8'))
scriptp=ROOT/f'editions/{DATE}-script.json'; script=json.loads(scriptp.read_text(encoding='utf-8'))
manifestp=ROOT/f'production/{DATE}-manifest.json'; manifest=json.loads(manifestp.read_text(encoding='utf-8'))
article=ROOT/f'editions/{DATE}.md'; smd=ROOT/f'editions/{DATE}-script.md'; detail=ROOT/f'editions/{DATE}.html'; home=ROOT/'index.html'
articletext=article.read_text(encoding='utf-8'); smdtext=smd.read_text(encoding='utf-8')
htmltext=detail.read_text(encoding='utf-8'); hometext=home.read_text(encoding='utf-8')

# Dates and timezones are distinct fields; date-only Oct 23 items remain unordered against the prior cutoff.
assert idx['generated_at']==CUTOFF and idx['latest_issue']==DATE
assert [x['id'] for x in idx['issues']]==[DATE,'2026-10-23','2026-10-22','2026-10-21','2026-10-20','2026-10-19','2026-10-17']
assert len([x for x in idx['issues'] if x['id']==DATE])==1
cur=idx['issues'][0]
assert cur['issue_number']==7 and cur['audio_status'] in ('pending','available')
assert cur['input_hash']==sha(researchp)
assert research['issue_id']==DATE and research['issue_number']==7 and research['timezone']=='Asia/Tokyo'
assert research['research_cutoff']==CUTOFF and research['research_cutoff_utc']==CUTOFF_UTC
assert research['previous_issue_cutoff']==PREVIOUS and research['previous_issue_id']=='2026-10-23'
assert research['items'] and len(research['scope_checked'])>=10
assert all(x.get('checked_at')==CUTOFF for x in research['items'])
for x in research['items']:
    if x.get('official_page_publication_date')=='2026-10-23':
        assert 'date only' in x.get('official_page_publication_time_or_timezone','').lower()
        assert 'cannot be ordered' in ' '.join(x.get('limitations',[])).lower() or 'cannot be ordered' in x.get('limitations',[]).__str__().lower() or 'chronology' in ' '.join(x.get('limitations',[])).lower()
assert any(x['provider']=='OpenAI' for x in research['scope_checked'])
assert any(x['provider']=='Amazon Web Services' for x in research['scope_checked'])
assert any(x['provider']=='UK AI Security Institute' for x in research['items'])

# Issue metadata and every utterance must be internally consistent and below the per-turn ceiling.
assert script['issue_id']==DATE and script['issue_number']==7 and script['issue_date']==DATE
assert script['timezone']=='Asia/Tokyo' and script['research_cutoff']==CUTOFF
assert script['style']=='normal' and script['speed']=='standard' and script['max_characters_per_utterance']==90
assert script['utterance_count']==len(script['utterances'])==44
assert max(len(x['text']) for x in script['utterances'])<=90
assert all(x['characters']==len(x['text']) for x in script['utterances'])
assert all(x['speaker_id']==(10005 if x['speaker']=='akari' else 10001) for x in script['utterances'])
assert all(x['speaker_name']==('あかり' if x['speaker']=='akari' else 'なおと') for x in script['utterances'])
assert all(script['utterances'][i]['speaker']!=script['utterances'][i+1]['speaker'] for i in range(len(script['utterances'])-1))
assert script['utterances'][0]['speaker']=='akari' and script['utterances'][0]['text'].startswith('こんにちは。')
assert script['utterances'][1]['speaker']=='naoto' and '高瀬直人' in script['utterances'][1]['text']
for u in script['utterances']:
    assert u['text'] in smdtext and u['text'] in htmltext and u['text'] in hometext, f"utterance missing from copy: {u['order']}"
assert '08:10:58 JST' in smdtext and CUTOFF in researchp.read_text(encoding='utf-8')

# Source-critical article checks: provider attribution, classification and limitations.
for text in (articletext,htmltext,hometext):
    for phrase in ('2026-10-24','2026-10-23','SageMaker','Amazon Polly','Gemini 4 Argon','Muse Glimmer 30B','Anthropic','08:10:58 JST'):
        assert phrase in text, f'missing required topic/timestamp {phrase}'
for phrase in ('導入価格','11月30日','12月1日','入力4米ドル','出力20米ドル','APIの料金表','前後関係を確定できません','9回','43回','現実世界の被害は生じなかった','別途公開されたAISI'):
    assert phrase in articletext and phrase in htmltext, f'missing caveat/source wording: {phrase}'
required_urls=[
 'https://aws.amazon.com/blogs/machine-learning/announcing-new-ways-to-customize-models-with-sagemaker-ai-without-managing-gpus/',
 'https://aws.amazon.com/about-aws/whats-new/2026/10/training-session-apis-on-sagemaker-ai/',
 'https://aws.amazon.com/blogs/machine-learning/amazon-polly-delivers-a-major-upgrade-to-its-generative-engine/',
 'https://blog.google/products-and-platforms/products/gemini/gemini-4-argon-builders/',
 'https://ai.google.dev/gemini-api/docs/pricing',
 'https://ai.meta.com/research/publications/muse-glimmer-30b-an-on-device-agentic-model/',
 'https://www.anthropic.com/research/alignment-assessment-ukaisi',
 'https://www.aisi.gov.uk/blog/investigating-alignment-failures-in-aisis-incident'
]
for url in required_urls:
    assert url in articletext and url in htmltext, f'missing official primary source {url}'
assert 'census of all AI announcements' in ' '.join(research['scope_limits'])
assert 'no global absence claim' in json.dumps(research,ensure_ascii=False).lower()

# Pending is a valid draft state; after the audio operator supplies metadata, verify the published state too.
assert manifest['issue_id']==DATE and manifest['issue_number']==7 and manifest['edition_date_jst']==DATE
assert manifest['timezone']=='Asia/Tokyo' and manifest['research_cutoff']==CUTOFF
assert manifest['input_hash']==cur['input_hash']==sha(researchp)
assert manifest['final_script_sha256']==manifest['synthesis_input_script_sha256']
assert manifest['checked_outputs']['utterance_count']==script['utterance_count']
assert manifest['checked_outputs']['maximum_utterance_characters']==max(len(x['text']) for x in script['utterances'])
status=script['audio_status']; assert status in ('pending','available') and manifest['audio']['status']==status and cur['audio_status']==status
if status=='pending':
    assert script['audio'] is None and cur.get('audio') is None
    assert manifest['audio']['sha256'] is None and manifest['audio']['synthesis_input_script_sha256']==manifest['final_script_sha256']
    assert not RefParser().audio
    assert not re.search(r'(?:src|href)=\"[^\"]*2026-10-24(?:-backup)?\.mp3', htmltext+hometext)
else:
    audio=script['audio']; a=manifest['audio']; AUDIO_SHA=a['sha256']; input_sha=a['synthesis_input_script_sha256']
    assert audio['sha256']==AUDIO_SHA and audio['backup_sha256']==AUDIO_SHA
    assert a['status']=='available' and a['generated_at_time_precision'].startswith('approximate')
    assert audio['file_size_bytes']==a['file_size_bytes'] and audio['duration_seconds']==a['duration_seconds']
    assert input_sha==manifest['final_script_sha256'] and audio['synthesis_input_script_sha256']==input_sha
    assert audio['public_url']==f'{SITE}/audio/{DATE}.mp3' and audio['backup_public_url']==f'{SITE}/audio/{DATE}-backup.mp3'
    assert cur['audio']==f'../audio/{DATE}.mp3' and cur['audio_backup']==f'../audio/{DATE}-backup.mp3'
    assert cur['audio_sha256']==AUDIO_SHA and cur['audio_backup_sha256']==AUDIO_SHA
    assert a['file_size_bytes']>0 and a['duration_seconds']>0 and a['codec']=='mp3'
    for rel in (f'audio/{DATE}.mp3',f'audio/{DATE}-backup.mp3',f'dist/audio/{DATE}.mp3',f'dist/audio/{DATE}-backup.mp3'):
        p=ROOT/rel; assert p.exists() and sha(p)==AUDIO_SHA and p.stat().st_size==a['file_size_bytes']
    assert (ROOT/f'audio/{DATE}.mp3').read_bytes()==(ROOT/f'audio/{DATE}-backup.mp3').read_bytes()
    assert (ROOT/f'dist/audio/{DATE}.mp3').read_bytes()==(ROOT/f'audio/{DATE}.mp3').read_bytes()
    assert (ROOT/f'dist/audio/{DATE}-backup.mp3').read_bytes()==(ROOT/f'audio/{DATE}.mp3').read_bytes()
    for p in (detail,home):
        parser=check_refs(p); assert parser.audio
    assert a['full_ffmpeg_decode']=='passed' and a['human_listening_claimed'] is False
    assert manifest['published_script_json_sha256']==sha(scriptp) and manifest['audio_metadata_updated_after_synthesis'] is True
    assert len(RefParser().audio)==0
    detail_audio=check_refs(detail).audio; home_audio=check_refs(home).audio
    assert len(detail_audio)==1 and detail_audio[0].get('src')==f'../audio/{DATE}.mp3'
    assert len(home_audio)==2 and all(x.get('src')==f'audio/{DATE}.mp3' for x in home_audio)
    assert '音声未完了' not in htmltext
    current_sections=hometext[hometext.index('<section class="listen"'):hometext.index('</section><div class="cover-grid"')] + hometext[hometext.index('<section class="radio"'):hometext.index('<div class="radio-actions"')] + hometext[hometext.index('<li class="issue-card"'):hometext.index('</li>')]
    assert '音声未完了' not in current_sections and 'audio-status' not in current_sections
    assert 'ISSUE 006' in hometext and 'audio/2026-10-23.mp3' in hometext
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(ROOT/f'audio/{DATE}.mp3')],text=True))
    stream=probe['streams'][0]
    assert stream['codec_name']=='mp3' and int(stream['sample_rate'])==a['sample_rate_hz'] and int(stream['channels'])==a['channels']
    assert int(probe['format']['size'])==a['file_size_bytes'] and abs(float(probe['format']['duration'])-a['duration_seconds'])<0.002
    subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/f'audio/{DATE}.mp3'),'-f','null','-'],check=True)

# All local references, retained prior editions/audio and the canonical dist copies.
check_refs(detail); check_refs(home)
for d in ('2026-10-23','2026-10-22','2026-10-21','2026-10-20','2026-10-19'):
    for ext in ('.html','.md','-script.md','-script.json'):
        assert (ROOT/f'editions/{d}{ext}').exists(), f'old edition missing: {d}{ext}'
for rel in ('audio/2026-10-23.mp3','audio/2026-10-23-backup.mp3','audio/2026-10-22.mp3','audio/2026-10-21.mp3','audio/episode-001.mp3','styles.css','app.js','assets/ai-model-radio-hosts.png','AI-model-latest-radio-issue-001.html'):
    assert (ROOT/rel).exists() and (ROOT/'dist'/rel).exists(), f'legacy asset missing {rel}'
for rel in (f'editions/{DATE}.md',f'editions/{DATE}-script.md',f'editions/{DATE}-script.json',f'editions/{DATE}.html',f'production/{DATE}-research.json',f'production/{DATE}-research.md',f'production/{DATE}-manifest.json',f'production/build-radio-{DATE}.mjs',f'production/verify-issue-{DATE}.py','editions/index.json','index.html'):
    assert (ROOT/rel).read_bytes()==(ROOT/'dist'/rel).read_bytes(), f'dist mirror mismatch: {rel}'
assert (ROOT/'dist/editions/index.json').read_bytes()==(ROOT/'editions/index.json').read_bytes()
for rel,digest in manifest['files_sha256'].items(): assert sha(ROOT/rel)==digest, f'manifest hash mismatch: {rel}'

# Public output scan for credentials or local machine paths.
patterns=[re.compile(x,re.I) for x in (r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'Bearer\s+[A-Za-z0-9._~-]{16,}',r'Authorization\s*:',r'/home/[^/\s]+/[^\s]+',r'https?://[^\s]*token=[^\s]+')]
for p in (home,detail,article,smd,scriptp,researchp,ROOT/f'production/{DATE}-research.md',manifestp,ROOT/f'production/build-radio-{DATE}.mjs'):
    body=p.read_text(encoding='utf-8'); assert not any(x.search(body) for x in patterns), f'secret/internal-path scan failed: {p.name}'

print(f'PASS: issue #7 dates/caveats, {len(script["utterances"])} alternating <=90-char utterances, official source citations, pending/available audio state, archive preservation, local refs, exact dist mirrors, manifest hashes and public-output scan')
