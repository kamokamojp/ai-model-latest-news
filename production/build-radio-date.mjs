#!/usr/bin/env node
// Build the dated issue with the official local VOICEVOX Nemo API; no paid service or key.
import { readFile, writeFile, mkdir, mkdtemp, rm, copyFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import os from 'node:os';

const [inputPath = 'editions/2026-10-27-script.json', outputPath = 'audio/2026-10-27.mp3'] = process.argv.slice(2);
const engine = (process.env.VOICEVOX_URL ?? 'http://127.0.0.1:50121').replace(/\/$/, '');
const backupPath = outputPath.replace(/\.mp3$/i, '-backup.mp3');
const speakerIds = { akari: 10005, naoto: 10001 };
const script = JSON.parse(await readFile(inputPath, 'utf8'));
if (script.issue_id !== '2026-10-27' || script.issue_date !== '2026-10-27' || script.timezone !== 'Asia/Tokyo') throw new Error('wrong issue/date/timezone');
if (script.style !== 'normal' || script.speed !== 'standard' || script.max_characters_per_utterance !== 90) throw new Error('wrong voice style/speed/limit');
if (!Array.isArray(script.utterances) || script.utterances.length === 0 || script.utterance_count !== script.utterances.length) throw new Error('invalid utterances');
for (let i = 0; i < script.utterances.length; i++) {
  const line = script.utterances[i];
  if (speakerIds[line.speaker] !== line.speaker_id || typeof line.text !== 'string' || !line.text.trim()) throw new Error(`invalid speaker/text at ${i + 1}`);
  if ([...line.text].length > 90 || line.characters !== [...line.text].length) throw new Error(`utterance exceeds 90 characters or count mismatch at ${i + 1}`);
}
const versionResponse = await fetch(`${engine}/version`);
if (!versionResponse.ok || await versionResponse.json() !== '0.24.0') throw new Error('official Nemo engine v0.24.0 is required');
const speakerResponse = await fetch(`${engine}/speakers`);
if (!speakerResponse.ok) throw new Error('could not list voice styles');
const speakers = await speakerResponse.json();
for (const id of Object.values(speakerIds)) {
  const style = speakers.flatMap(s => s.styles ?? []).find(s => s.id === id);
  if (!style || style.name !== 'ノーマル') throw new Error(`required normal voice style ${id} not found`);
}
const tempDir = await mkdtemp(path.join(os.tmpdir(), 'ai-model-radio-2026-10-27-'));
await mkdir(path.dirname(outputPath), { recursive: true });
const wavs = [];
try {
  for (let i = 0; i < script.utterances.length; i++) {
    const line = script.utterances[i];
    const speaker = speakerIds[line.speaker];
    const queryResponse = await fetch(`${engine}/audio_query?text=${encodeURIComponent(line.text)}&speaker=${speaker}`, { method: 'POST' });
    if (!queryResponse.ok) throw new Error(`audio_query failed (${queryResponse.status}) for utterance ${i + 1}`);
    const query = await queryResponse.json();
    query.speedScale = 1.0;
    const synthesisResponse = await fetch(`${engine}/synthesis?speaker=${speaker}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(query) });
    if (!synthesisResponse.ok) throw new Error(`synthesis failed (${synthesisResponse.status}) for utterance ${i + 1}`);
    const wav = path.join(tempDir, `${String(i).padStart(3, '0')}.wav`);
    await writeFile(wav, Buffer.from(await synthesisResponse.arrayBuffer()));
    wavs.push(wav);
    process.stdout.write(`Synthesized ${i + 1}/${script.utterances.length}\n`);
  }
  const list = path.join(tempDir, 'concat.txt');
  await writeFile(list, wavs.map(p => `file '${p.replaceAll("'", "'\\''")}'`).join('\n'));
  await new Promise((resolve, reject) => {
    const proc = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-codec:a', 'libmp3lame', '-b:a', '96k', outputPath]);
    proc.on('error', reject);
    proc.on('exit', code => code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`)));
  });
  await copyFile(outputPath, backupPath);
  process.stdout.write(`Wrote ${outputPath} and byte-identical backup ${backupPath} at 96 kbps MP3\n`);
} finally {
  await rm(tempDir, { recursive: true, force: true });
}
