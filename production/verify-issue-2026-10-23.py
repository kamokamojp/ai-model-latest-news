#!/usr/bin/env python3
"""Verify Oct. 23 model-radio issue source, date caveats, deliverables, and pending audio."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-23'; CUTOFF='2026-10-23T08:42:19+09:00'; SITE='https://ai-model-latest-radio.kamokamojp.chatgpt.site'
class RefParser(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]; self.audio=[]
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
idx=json.loads((ROOT/'editions/index.json').read_text(encoding='utf-8'))
researchp=ROOT/f'production/{DATE}-research.json'; research=json.loads(researchp.read_text(encoding='utf-8'))
scriptp=ROOT/f'editions/{DATE}-script.json'; script=json.loads(scriptp.read_text(encoding='utf-8'))
manifestp=ROOT/f'production/{DATE}-manifest.json'; manifest=json.loads(manifestp.read_text(encoding='utf-8'))
assert idx['generated_at']==CUTOFF and idx['latest_issue']==DATE
assert [x['id'] for x in idx['issues']]==[DATE,'2026-10-22','2026-10-21','2026-10-20','2026-10-19','2026-10-17']
assert len([x for x in idx['issues'] if x['id']==DATE])==1
cur=idx['issues'][0]; assert cur['issue_number']==6 and cur['audio_status']=='available'
assert cur['audio']=='../audio/2026-10-23.mp3' and cur['audio_backup']=='../audio/2026-10-23-backup.mp3'
assert cur['input_hash']==sha(researchp)
assert research['issue_id']==DATE and research['issue_number']==6 and research['timezone']=='Asia/Tokyo'
assert research['research_cutoff']==CUTOFF and research['research_cutoff_utc']=='2026-10-22T23:42:19Z'
assert research['confirmed_in_window_story']['company']=='NVIDIA'
assert 'Minerva' in research['confirmed_in_window_story']['topic'] and 'not availability' in research['confirmed_in_window_story']['why_in_window']
assert research['confirmed_in_window_story']['deployment_pricing_caveat']
assert any(x['title']=='NVIDIA Unveils Minerva to Bring End-to-End Observability for AI Factories' and x['publisher_page_date']=='2026-10-22' and x['publisher_page_time_or_timezone'].startswith('date only') and x['selected_for_public_issue'] for x in research['items'])
minfeed=next(x for x in research['items'] if x['title']=='GTC Berlin 2026 live news feed (Minerva listing)')
assert minfeed['live_feed_listing_timestamp']['jst']=='2026-10-23T00:00:00+09:00'
assert 'not product availability' in minfeed['live_feed_listing_timestamp']['meaning']
assert any(x['title']=='NVIDIA Minerva product and deployment page' and 'regional site' in x['notes'] for x in research['items'])
cosmos=research['additional_confirmed_story']; assert cosmos['company']=='NVIDIA' and 'not product availability' in cosmos['why_in_window']
assert any(x['company']=='OpenAI API' and 'ambiguous' in x.get('status','') for x in research['items'])
assert any(x['company']=='Cohere' and 'ambiguous' in x.get('status','') for x in research['items'])
assert script['issue_id']==DATE and script['issue_number']==6 and script['issue_date']==DATE
assert script['timezone']=='Asia/Tokyo' and script['research_cutoff']==CUTOFF
assert script['style']=='normal' and script['speed']=='standard' and script['audio_status']=='available'
audio=script['audio']; AUDIO_SHA='e419a1d3975aba7e6946dad36fb0da51e0d5f37fde5cef4082d9cc1177e6e28f'
SYNTHESIS_INPUT_SHA='0bf6c522057d5fd9564a690d7991041583a43118c2c4958874bcb61ecb5492be'
assert audio['sha256']==audio['backup_sha256']==AUDIO_SHA
assert audio['synthesis_input_script_sha256']==SYNTHESIS_INPUT_SHA
assert audio['public_url']==f'{SITE}/audio/{DATE}.mp3' and audio['backup_public_url']==f'{SITE}/audio/{DATE}-backup.mp3'
assert audio['file_size_bytes']==2078828 and audio['duration_seconds']==173.208
assert audio['codec']=='mp3' and audio['sample_rate_hz']==24000 and audio['channels']==1 and audio['bit_rate_bps']==96000
assert audio['engine']=='VOICEVOX Nemo' and audio['engine_version']=='0.24.0'
assert audio['generated_at_jst']=='2026-10-23T08:48:52.344328+09:00' and audio['human_listening_claimed'] is False
assert script['utterance_count']==len(script['utterances'])==33 and script['max_characters_per_utterance']==90
assert max(len(x['text']) for x in script['utterances'])<=90
assert all(x['characters']==len(x['text']) for x in script['utterances'])
assert all(x['speaker_id']==(10005 if x['speaker']=='akari' else 10001) for x in script['utterances'])
assert all(x['speaker_name']==('あかり' if x['speaker']=='akari' else 'なおと') for x in script['utterances'])
assert all(script['utterances'][i]['speaker']!=script['utterances'][i+1]['speaker'] for i in range(len(script['utterances'])-1))
assert script['utterances'][0]['speaker']=='akari' and '水野あかり' in script['utterances'][0]['text']
assert script['utterances'][1]['speaker']=='naoto' and '高瀬直人' in script['utterances'][1]['text']
article=ROOT/f'editions/{DATE}.md'; smd=ROOT/f'editions/{DATE}-script.md'; detail=ROOT/f'editions/{DATE}.html'; home=ROOT/'index.html'
articletext=article.read_text(encoding='utf-8'); smdtext=smd.read_text(encoding='utf-8'); htmltext=detail.read_text(encoding='utf-8'); hometext=home.read_text(encoding='utf-8')
for t in (articletext,smdtext,htmltext,hometext): assert DATE in t and 'Minerva' in t and 'Cosmos' in t
for phrase in ['2026-10-22','本日開始','提供開始時刻','独立評価','IREN','オンプレミス','SaaS']:
    assert phrase in articletext and phrase in htmltext
for u in script['utterances']:
    assert u['text'] in smdtext and u['text'] in htmltext and u['text'] in hometext
required=['https://blogs.nvidia.com/blog/minerva-platform-infrastructure/','https://blogs.nvidia.com/gtc-berlin-2026-news/','https://www.nvidia.com/en-us/networking/products/software/minerva/','https://blogs.nvidia.com/blog/cosmos-open-train-evaluate-deploy-world-models/','https://github.com/NVIDIA/cosmos-data-factory']
for url in required: assert url in articletext and url in htmltext and url in hometext
assert not re.search(r'音声未完了|旧ドラフト音声|audio-pending',htmltext)
current_home_listen=hometext[hometext.index('<section class="listen"'):hometext.index('</section><div class="cover-grid"')]
current_home_radio=hometext[hometext.index('<section class="radio" id="radio"'):hometext.index('</section><section class="sources"')]
current_home_card=hometext[hometext.index('<li class="issue-card"'):hometext.index('</li>')]
assert not re.search(r'音声未完了|旧ドラフト音声|audio-pending',current_home_listen+current_home_radio+current_home_card)
assert f'<audio controls preload="metadata" src="../audio/{DATE}.mp3">' in htmltext
assert f'<audio controls preload="metadata" src="audio/{DATE}.mp3">' in hometext
assert f'href="../audio/{DATE}-backup.mp3"' in htmltext and f'href="audio/{DATE}-backup.mp3"' in hometext
parser=check_refs(detail); homeparser=check_refs(home); assert parser.audio and homeparser.audio
for d in ['2026-10-22','2026-10-21','2026-10-20','2026-10-19']:
    assert (ROOT/f'editions/{d}.html').exists() and (ROOT/f'dist/editions/{d}.html').exists()
for f in ['audio/2026-10-22.mp3','audio/2026-10-21.mp3','audio/episode-001.mp3','styles.css','app.js','assets/ai-model-radio-hosts.png','AI-model-latest-radio-issue-001.html']:
    assert (ROOT/f).exists() and (ROOT/'dist'/f).exists()
# The generated audio is cryptographically bound to the exact pre-metadata final script and mirrored byte-for-byte.
assert manifest['audio']['status']=='available' and manifest['audio']['sha256']==AUDIO_SHA
assert manifest['audio']['synthesis_input_script_sha256']==SYNTHESIS_INPUT_SHA
assert manifest['final_script_sha256']==SYNTHESIS_INPUT_SHA
assert manifest['published_script_json_sha256']==sha(scriptp)
assert manifest['audio']['superseded_draft_sha256']=='3e2ab41a2dfbdae70768fb78c185f1f87a15cd0b746eef5715305ea596aba7f9'
for rel in ['audio/2026-10-23.mp3','audio/2026-10-23-backup.mp3','dist/audio/2026-10-23.mp3','dist/audio/2026-10-23-backup.mp3']:
    assert sha(ROOT/rel)==AUDIO_SHA and (ROOT/rel).stat().st_size==2078828
    assert ROOT/rel==ROOT/'audio/2026-10-23.mp3' or (ROOT/rel).read_bytes()==(ROOT/'audio/2026-10-23.mp3').read_bytes()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,sample_rate,channels,bit_rate','-of','json',str(ROOT/'audio/2026-10-23.mp3')],text=True))
stream=probe['streams'][0]
assert stream['codec_name']=='mp3' and stream['sample_rate']=='24000' and stream['channels']==1 and stream['bit_rate']=='96000'
assert float(probe['format']['duration'])==173.208 and int(probe['format']['size'])==2078828
subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/'audio/2026-10-23.mp3'),'-f','null','-'],check=True)
assert manifest['audio']['full_ffmpeg_decode']=='passed' and manifest['audio']['human_listening_claimed'] is False
assert manifest['input_hash']==cur['input_hash']==sha(researchp)
rels=[f'editions/{DATE}.md',f'editions/{DATE}-script.md',f'editions/{DATE}-script.json',f'editions/{DATE}.html',f'production/{DATE}-research.json',f'production/{DATE}-research.md','editions/index.json','index.html',f'production/build-radio-{DATE}.mjs',f'production/verify-issue-{DATE}.py',f'audio/{DATE}.mp3',f'audio/{DATE}-backup.mp3']
for rel in rels: assert (ROOT/rel).read_bytes()==(ROOT/'dist'/rel).read_bytes(), f'dist mismatch {rel}'
assert (ROOT/'dist/production'/f'{DATE}-manifest.json').read_bytes()==manifestp.read_bytes()
assert (ROOT/'dist/editions/index.json').read_bytes()==(ROOT/'editions/index.json').read_bytes()
for rel,digest in manifest['files_sha256'].items(): assert sha(ROOT/rel)==digest, f'manifest hash mismatch {rel}'
assert manifest['checked_outputs']['utterance_count']==script['utterance_count'] and manifest['checked_outputs']['maximum_utterance_characters']==max(len(x['text']) for x in script['utterances'])
patterns=[re.compile(x,re.I) for x in [r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'Bearer\s+[A-Za-z0-9._~-]{16,}',r'Authorization\s*:',r'/home/[^/\s]+/[^\s]+',r'https?://[^\s]*token=[^\s]+']]
for p in [home,detail,article,smd,scriptp,researchp,ROOT/f'production/{DATE}-research.md',manifestp,ROOT/f'production/build-radio-{DATE}.mjs']:
    body=p.read_text(encoding='utf-8'); assert not any(x.search(body) for x in patterns), f'secret/internal path scan failed {p.name}'
print('PASS: source dates/timezones, Minerva/Cosmos source coverage, factual caveats, 33-utterance two-speaker script <=90 chars, exact synthesis-input binding, MP3 metadata/hash/full decode/backup, re-enabled HTML/home players, local links, archive retention, dist exact mirrors, manifest/input hashes, public-output scan')
