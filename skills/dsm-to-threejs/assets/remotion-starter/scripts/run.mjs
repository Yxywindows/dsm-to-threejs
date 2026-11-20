import {existsSync, readFileSync, readdirSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {validate} from '../src/config.mjs';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
process.chdir(root);
const config = JSON.parse(readFileSync('film.json', 'utf8'));
const total = validate(config);
const installed = join(root, 'node_modules', '@remotion');
const executable = process.platform === 'win32' ? 'ffprobe.exe' : 'ffprobe';
const bundled = readdirSync(installed).filter(n => n.startsWith('compositor-')).map(n => join(installed, n, executable));
const localProbe = bundled.find(existsSync);
const probe = process.env.FFPROBE || localProbe || 'ffprobe';
const probeCwd = probe === localProbe ? dirname(probe) : root;
function check(file, kind, frames) {
  const path = resolve('public', file);
  if (!existsSync(path)) throw new Error('Missing public/' + file);
  const result = spawnSync(probe, ['-v','error','-show_streams','-of','json',path], {encoding:'utf8',cwd:probeCwd});
  if (result.error || result.status !== 0) throw new Error('ffprobe: ' + (result.error || result.stderr));
  const stream = JSON.parse(result.stdout).streams.find(s => s.codec_type === kind);
  if (!stream) throw new Error(file + ' needs a ' + kind + ' stream');
  const [n,d] = String(stream.time_base).split('/').map(Number);
  const seconds = Number(stream.duration) || Number(stream.duration_ts) * n / d;
  if (!Number.isFinite(seconds) || seconds + .0001 < frames/config.fps)
    throw new Error(file + ': expected at least ' + frames/config.fps + ' seconds, measured ' + seconds);
}
for (const shot of config.shots) check(shot.file, 'video', shot.frames);
if (config.music) check(config.music, 'audio', total);
console.log(config.shots.length + ' shots, ' + total + ' frames at ' + config.fps + ' fps');
const [command,...extra] = process.argv.slice(2);
if (command !== 'check') {
  if (!['studio','render','still'].includes(command)) throw new Error('Unknown command: ' + command);
  const args = [command, 'src/index.jsx'];
  if (command !== 'studio') {
    args.push('Film', extra[0] && !extra[0].startsWith('--') ? extra.shift() : command === 'still' ? 'out/still.png' : 'out/film.mp4');
    if (command === 'render') {
      args.push('--codec=h264');
      if (!config.music) args.push('--muted');
    }
    if (process.env.REMOTION_BROWSER) args.push('--browser-executable=' + process.env.REMOTION_BROWSER);
  }
  const child = spawnSync(process.execPath,[join(installed,'cli','remotion-cli.js'), ...args,...extra],{stdio:'inherit'});
  if (child.error) throw child.error;
  process.exitCode = child.status ?? 1;
}
