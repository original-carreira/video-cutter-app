import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# =============================
# Caminho base (dev + exe)
# =============================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# =============================
# FFmpeg local
# =============================
def get_ffmpeg_path():
    base_path = get_base_path()
    ffmpeg_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    return os.path.normpath(os.path.join(base_path, "ffmpeg", ffmpeg_exe))


# =============================
# Execução do FFmpeg
# =============================
def run_ffmpeg_command(args, timeout=600):

    ffmpeg_path = get_ffmpeg_path()

    if not os.path.exists(ffmpeg_path):
        error_msg = f"FFmpeg não encontrado em: {ffmpeg_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

    if args and args[0].lower() == "ffmpeg":
        args = args[1:]

    full_command = [ffmpeg_path] + args

    logging.info(f"Iniciando FFmpeg: {full_command}")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.run(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            creationflags=creationflags
        )

        if process.returncode == 0:
            logging.info("FFmpeg executado com sucesso.")
            return process.stdout or process.stderr

        error_details = (process.stderr or "")[-1000:]
        logging.error(f"FFmpeg falhou ({process.returncode}):\n{error_details}")

        raise RuntimeError(
            "Erro ao processar o vídeo.\n"
            "Tente ativar o modo compatível."
        )

    except subprocess.TimeoutExpired:
        logging.error(f"Timeout atingido ({timeout}s).")
        raise RuntimeError("Processamento demorou muito e foi cancelado.")

    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise