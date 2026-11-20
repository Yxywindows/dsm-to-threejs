#!/usr/bin/env python3
"""Inspect a decoded film. Only explicit delivery requirements affect the result."""
import argparse
from array import array
from fractions import Fraction
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def fps_value(value):
    try:
        number = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError("use 25 or 30000/1001") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("frame rate must be positive")
    return number


def execute(argv):
    result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f"{Path(argv[0]).name} failed with exit code {result.returncode}")
    return result.stdout


def probe(tool, path, *options):
    return json.loads(execute([tool, "-v", "error", *options, "-of", "json", str(path)]))


def read_audio(tool, path, stream):
    # Decode post-priming audio. Keep PCM memory bounded even for feature-length films.
    cmd = [tool, "-v", "error", "-xerror", "-i", str(path), "-map", f"0:{stream['index']}",
           "-f", "f32le", "-acodec", "pcm_f32le", "-"]
    count = 0
    squares = 0.0
    peak = 0.0
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        while block := process.stdout.read(262144):
            samples = array("f")
            samples.frombytes(block)
            if sys.byteorder != "little":
                samples.byteswap()
            count += len(samples)
            squares += sum(v*v for v in samples)
            peak = max(peak, max(map(abs, samples), default=0))
        if process.wait():
            raise RuntimeError("audio decode failed")
    rms = math.sqrt(squares/count) if count else 0
    return {"decoded_samples_per_channel": count//stream["channels"],
            "decoded_duration_s": count/(int(stream["sample_rate"])*stream["channels"]),
            "peak_dbfs": 20*math.log10(peak) if peak else None,
            "rms_dbfs": 20*math.log10(rms) if rms else None}


def write_sheet(tool, path, destination, video_index, shots):
    # Up to three unique frame samples per supplied shot: start, middle, end.
    start = 0
    labels = []
    for i, length in enumerate(shots, 1):
        for f in sorted({start, start+length//2, start+length-1}):
            labels.append({"shot": i, "frame_0based": f})
        start += length
    count = len(labels)
    columns = min(6, count) if count > 24 else min(3, count)
    rows = math.ceil(count/columns)
    cell = min(240, 4096//max(columns, rows))
    if cell < 24:
        raise ValueError("too many shots for a small single contact sheet; review in groups")
    select = "+".join(f"eq(n\\,{v['frame_0based']})" for v in labels)
    # Pad before tiling so portrait, square and landscape films retain their display aspect.
    height = max(16, 2*round(cell*0.5625/2))
    vf = (f"select={select},scale=w='min({cell},trunc({height}*dar/2)*2)':"
          f"h='min({height},trunc({cell}/dar/2)*2)',setsar=1,"
          f"pad={cell}:{height}:(ow-iw)/2:(oh-ih)/2,"
          f"tile={columns}x{rows}:nb_frames={count}:padding=2:margin=2")
    destination.parent.mkdir(parents=True, exist_ok=True)
    execute([tool, "-v", "error", "-xerror", "-y", "-i", str(path), "-map", f"0:{video_index}",
             "-vf", vf, "-frames:v", "1", "-update", "1", str(destination)])
    return {"file": destination.name, "columns": columns, "order": "row-major", "cells": labels}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--width", type=positive)
    parser.add_argument("--height", type=positive)
    parser.add_argument("--fps", type=fps_value, help="expected constant rate, integer or rational")
    parser.add_argument("--frames", type=positive)
    parser.add_argument("--shots", help="comma-separated shot lengths in frames; counts and samples only")
    parser.add_argument("--sheet", type=Path, help="optional contact sheet (.jpg or .png)")
    parser.add_argument("--json", type=Path, help="also write the stdout JSON report here")
    parser.add_argument("--audio", choices=["optional", "present", "absent", "audible", "silent"], default="optional",
                        help="silent accepts no track or all tracks below the chosen sample-peak threshold")
    parser.add_argument("--silence-dbfs", type=float, default=-60, help="sample-peak reference for audible/silent")
    parser.add_argument("--audio-sync", action="store_true",
                        help="require every audio stream to cover the presented video span, allowing a codec frame of padding or rounding")
    parser.add_argument("--check-audio", action="store_true", help="decode and measure audio even without a level requirement")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    a = parser.parse_args()
    shots = None
    if a.shots is not None:
        try:
            shots = [positive(n.strip()) for n in a.shots.split(",")]
        except (ValueError, argparse.ArgumentTypeError):
            parser.error("--shots requires comma-separated positive integers")
    if not math.isfinite(a.silence_dbfs) or a.silence_dbfs > 0:
        parser.error("--silence-dbfs must be finite and <= 0")
    if a.sheet and a.sheet.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        parser.error("--sheet expects a .jpg or .png path")
    outputs = [p.resolve() for p in (a.sheet, a.json) if p]
    if a.input.resolve() in outputs or len(outputs) != len(set(outputs)):
        parser.error("input, sheet and report must use different paths")
    for tool in (a.ffmpeg, a.ffprobe):
        if not shutil.which(tool):
            parser.error(f"{Path(tool).name} is unavailable")
    meta = probe(a.ffprobe, a.input, "-show_streams", "-show_format")
    videos = [s for s in meta["streams"] if s["codec_type"] == "video" and not s.get("disposition", {}).get("attached_pic")]
    if not videos:
        raise ValueError("no video stream")
    v = videos[0]
    decoded = probe(a.ffprobe, a.input, "-select_streams", str(v["index"]), "-show_frames",
                    "-show_entries", "frame=best_effort_timestamp,duration,pkt_duration")
    frames = decoded.get("frames", [])
    execute([a.ffmpeg, "-v", "error", "-xerror", "-i", str(a.input), "-map", f"0:{v['index']}", "-an", "-f", "null", "-"])
    checks = {"video_decoded": bool(frames)}
    n = len(frames)
    tick = Fraction(v["time_base"])
    pts = [int(f["best_effort_timestamp"]) for f in frames if "best_effort_timestamp" in f]
    complete = len(pts) == n and n > 0
    checks["complete_increasing_timestamps"] = complete and all(y > x for x, y in zip(pts, pts[1:]))
    last_ticks = (frames[-1].get("duration") or frames[-1].get("pkt_duration")) if frames else None
    span = (pts[-1]-pts[0]+int(last_ticks))*tick if complete and last_ticks is not None else None
    timing = {"first_pts_s": float(pts[0]*tick) if pts else None, "time_base": str(tick),
              "decoded_video_span_s": float(span) if span is not None else None}
    if a.fps:
        # Compare timestamps against the ideal timeline, allowing one container tick of rounding.
        tolerance = min(tick, Fraction(1, 4)/a.fps)
        errors = [abs((p-pts[0])*tick-Fraction(i, 1)/a.fps) for i,p in enumerate(pts)]
        checks["requested_cfr_timeline"] = complete and max(errors, default=0) <= tolerance
        if span is not None:
            checks["requested_frame_duration"] = abs(span-Fraction(n,1)/a.fps) <= tolerance
        elif n < 2:
            checks["requested_frame_duration"] = False
        timing.update(expected_fps=str(a.fps), timestamp_tolerance_s=float(tolerance),
                      max_timeline_error_s=float(max(errors)) if errors else None)
    for field in ("width", "height"):
        if getattr(a,field) is not None:
            checks["requested_"+field] = v[field] == getattr(a,field)
    if a.frames is not None:
        checks["requested_frame_count"] = n == a.frames
    if shots:
        checks["shot_lengths_cover_frame_count"] = sum(shots) == n
    audio = []
    sync = []
    for s in meta["streams"]:
        if s["codec_type"] != "audio":
            continue
        row = {k:s.get(k) for k in ("codec_name", "channels", "sample_rate", "start_time", "duration")}
        if a.check_audio or a.audio_sync or a.audio in ("audible", "silent"):
            row.update(read_audio(a.ffmpeg, a.input, s))
        if a.audio_sync:
            start = s.get("start_time")
            # Stream presentation timing honors MP4 edit lists. AAC's decoded PCM
            # may include one final padded access unit even when presentation lengths match.
            audio_duration = float(s.get("duration") or row["decoded_duration_s"])
            codec_samples = 2048 if s.get("profile") in ("HE-AAC","HE-AACv2") else 1024
            tolerance_s = max(float(tick), float(Fraction(s["time_base"])),
                              codec_samples/int(s["sample_rate"]) if s["codec_name"] == "aac" else 0)
            synced = False
            if start is not None and span is not None:
                delta = float(start)-float(pts[0]*tick)
                end_delta = delta+audio_duration-float(span)
                synced = max(abs(delta),abs(end_delta)) <= tolerance_s+1e-6
                row.update(start_delta_s=delta, end_delta_s=end_delta)
            row["coverage_tolerance_s"] = tolerance_s
            sync.append(synced)
        audio.append(row)
    if a.audio_sync:
        checks["audio_covers_presented_video"] = bool(sync) and all(sync)
    if a.audio == "present":
        checks["audio_present"] = bool(audio)
    elif a.audio == "absent":
        checks["audio_absent"] = not audio
    elif a.audio in ("silent", "audible"):
        loud = any(r["peak_dbfs"] is not None and r["peak_dbfs"] > a.silence_dbfs for r in audio)
        checks["audio_"+a.audio] = loud if a.audio == "audible" else not loud
    report = {"input": a.input.name, "passed": all(checks.values()), "checks": checks,
              "video": {k:v.get(k) for k in ("codec_name","pix_fmt","width","height","avg_frame_rate")},
              "decoded_frames": n, "timing": timing, "audio": audio}
    if a.sheet and n and (not shots or sum(shots) == n):
        report["contact_sheet"] = write_sheet(a.ffmpeg,a.input,a.sheet,v["index"],shots or [n])
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(output+"\n", encoding="utf-8")
    print(output)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Film check failed: {error}", file=sys.stderr)
        sys.exit(2)
