function mediaPath(path) {
  if (typeof path !== 'string' || !path.trim() || /[:\\?#%]/.test(path) ||
      path.split('/').some((s) => !s || s === '.' || s === '..')) {
    throw new Error('Expected a relative media path under public/: ' + path);
  }
}
export function validate(config) {
  const {width, height, fps, shots, music, title} = config;
  for (const value of [width, height, fps]) {
    if (!Number.isSafeInteger(value) || value < 1) throw new Error('Invalid resolution or fps');
  }
  if (width % 2 || height % 2) throw new Error('H.264 dimensions must be even');
  if (!Array.isArray(shots) || !shots.length) throw new Error('At least one shot is required');
  let frames = 0;
  for (const shot of shots) {
    mediaPath(shot.file);
    if (!Number.isSafeInteger(shot.frames) || shot.frames < 1) throw new Error('Invalid frame count: ' + shot.file);
    frames += shot.frames;
  }
  if (!Number.isSafeInteger(frames)) throw new Error('Total frame count exceeds safe integer range');
  if (music != null) mediaPath(music);
  if (title != null && typeof title !== 'string') throw new Error('Title must be text or null');
  if (config.titlePosition !== undefined && !['top-left', 'top-right', 'bottom-left', 'bottom-right'].includes(config.titlePosition)) {
    throw new Error('titlePosition must be top-left, top-right, bottom-left or bottom-right');
  }
  return frames;
}
