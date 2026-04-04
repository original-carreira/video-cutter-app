import subprocess
import logging

def run_ffmpeg_command(command):
    try:
        logging.info(f"Executando comando: {' '.join(command)}")
        subprocess.run(command, check=True)
        logging.info("Comando executado com sucesso")
    except subprocess.CalledProcessError as e:
        logging.error("Erro ao executar FFmpeg", exc_info=True)
        raise e