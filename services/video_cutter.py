from infra.ffmpeg_runner import run_ffmpeg_command

def cortar_video(input_path, start_time, end_time, output_path, reencode=False, precise=False):

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y"
    ]

    if not precise:
        command += ["-ss", start_time, "-to", end_time]

    command += ["-i", input_path]

    if precise:
        command += ["-ss", start_time, "-to", end_time]

    command += [
        "-map", "0:v:0",
        "-map", "0:a:0?"  # evita erro se não houver áudio
    ]

    if reencode:
        command += [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac"
        ]
    else:
        command += [
            "-c", "copy",
            "-avoid_negative_ts", "make_zero"
        ]

    command.append(output_path)

    run_ffmpeg_command(command)