import os
import logging
from infra.ffmpeg_runner import run_ffmpeg_command

def normalizar_video(input_path):

    filename = os.path.basename(input_path)

    if "_normalized" in filename:
        return input_path

    os.makedirs("videos/normalized", exist_ok=True)

    base_name = os.path.splitext(filename)[0]
    output_path = f"videos/normalized/{base_name}_normalized.mp4"

    # Evita reprocessamento
    if os.path.exists(output_path):
        logging.info("Vídeo já normalizado. Reutilizando arquivo.")
        return output_path

    logging.info(f"Normalizando vídeo: {input_path} → {output_path}")

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", input_path,
        "-map", "0:v:0",
        "-map", "0:a:0?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-af", "loudnorm",
        "-movflags", "+faststart",
        output_path
    ]

    run_ffmpeg_command(command)

    if not os.path.exists(output_path):
        raise RuntimeError("Falha na normalização do vídeo")

    return output_path