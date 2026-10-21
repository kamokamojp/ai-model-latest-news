#!/usr/bin/env node
// Build an MP3 from scripted VOICEVOX Nemo dialogue using the local official API.
// Input JSON: {"utterances":[{"speaker":"akari","text":"..."}, {"speaker":"naoto","text":"..."}]}
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import os from 'node:os';

const args = process.argv.slice(2);
const inputPath = args[0] ?? 'scripts/radio-script.json';
const outputPath = args[1] ?? 'dist/radio_show.mp3';
const engine = (process.env.VOICEVOX_URL ?? 'http://127.0.0.1:50021').replace(/\/$/, '');
const speakerIds = { akari: 10005, naoto: 10001 };
const script = JSON.parse(await readFile(inputPath, 'utf8'));
if (!Array.isArray(script.utterances) || script.utterances.length === 0) throw new Error('utterances must be a non-empty array');
const tempDir = await mkdtemp(path.join(os.tmpdir(), 'ai-news-radio-'));
await mkdir(path.dirname(outputPath), { recursive: true });
const wavs = [];
try {
  for (let i = 0; i < script.utterances.length; i++) {
    const line = script.utterances[i];
    const speaker = speakerIds[line.speaker];
    if (!speaker || typeof line.text !== 'string' || !line.text.trim()) throw new Error(`Invalid utterance ${i + 1}`);
    const q = await fetch(`${engine}/audio_query?text=${encodeURIComponent(line.text)}&speaker=${speaker}`, { method: 'POST' });
    if (!q.ok) throw new Error(`audio_query failed (${q.status}) for line ${i + 1}`);
    const query = await q.json();
    const audio = await fetch(`${engine}/synthesis?speaker=${speaker}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(query) });
    if (!audio.ok) throw new Error(`synthesis failed (${audio.status}) for line ${i + 1}`);
    const wav = path.join(tempDir, `${String(i).padStart(3, '0')}.wav`);
    await writeFile(wav, Buffer.from(await audio.arrayBuffer()));
    wavs.push(wav);
    process.stdout.write(`Synthesized ${i + 1}/${script.utterances.length}\n`);
  }
  const list = path.join(tempDir, 'concat.txt');
  await writeFile(list, wavs.map(p => `file '${p.replaceAll("'", "'\\''")}'`).join('\n'));
  await new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-codec:a', 'libmp3lame', '-b:a', '96k', outputPath]);
    proc.on('error', reject); proc.on('exit', code => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`)));
  });
  process.stdout.write(`Wrote ${outputPath}\n`);
} finally { await rm(tempDir, { recursive: true, force: true }); }

