import os
import subprocess
import logging


def run_ffmpeg_command(args):
    ffmpeg_path = get_ffmpeg_path()

    # =============================
    # Validação do FFmpeg
    # =============================
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(
            f"FFmpeg não encontrado em: {ffmpeg_path}"
        )

    # =============================
    # Montagem do comando
    # =============================
    full_command = [ffmpeg_path] + args

    logging.info(f"Executando comando FFmpeg: {' '.join(full_command)}")

    # =============================
    # Execução
    # =============================
    process = subprocess.run(
        full_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    # =============================
    # Tratamento de erro
    # =============================
    if process.returncode != 0:
        logging.error("Erro ao executar FFmpeg")
        logging.error(process.stderr)

        raise RuntimeError(
            f"FFmpeg falhou:\n{process.stderr}"
        )

    # =============================
    # Log de sucesso
    # =============================
    logging.info("FFmpeg executado com sucesso")

    return process.stdout