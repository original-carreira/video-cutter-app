import os
import sys
import subprocess
import logging


# =============================
# Caminho base da aplicação
# =============================
def get_base_path():
    """
    Retorna o diretório correto:
    - Desenvolvimento → raiz do projeto
    - Executável (.exe) → pasta do executável
    """
    if getattr(sys, 'frozen', False):
        # Quando executado como .exe
        return os.path.dirname(sys.executable)

    # Quando executado em modo desenvolvimento
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# =============================
# Caminho do FFmpeg
# =============================
def get_ffmpeg_path():
    """
    Retorna o caminho do FFmpeg dentro da aplicação.
    Funciona tanto no ambiente de desenvolvimento quanto no executável.
    """
    base_path = get_base_path()

    # Define nome conforme sistema operacional
    ffmpeg_exe = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"

    return os.path.join(base_path, "ffmpeg", ffmpeg_exe)


# =============================
# Execução do FFmpeg
# =============================
def run_ffmpeg_command(args):
    """
    Executa um comando FFmpeg de forma segura e controlada.

    Args:
        args (list): Lista de argumentos do FFmpeg (sem incluir o executável)

    Returns:
        str: Saída padrão do FFmpeg (stdout)

    Raises:
        FileNotFoundError: Se o FFmpeg não for encontrado
        RuntimeError: Se o FFmpeg falhar durante a execução
    """

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

    logging.info(f"Executando FFmpeg: {full_command}")

    try:
        # =============================
        # Execução
        # =============================
        process = subprocess.run(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=300  # 🔥 evita travamento infinito (5 min)
        )

    except subprocess.TimeoutExpired:
        logging.error("Timeout ao executar FFmpeg")
        raise RuntimeError("O processamento demorou muito e foi interrompido.")

    # =============================
    # Tratamento de erro
    # =============================
    if process.returncode != 0:
        logging.error("Erro ao executar FFmpeg")

        # Limita tamanho do log para evitar excesso
        logging.error(process.stderr[:1000])

        raise RuntimeError(
            "Falha ao processar o vídeo.\n"
            "Tente ativar o modo compatível."
        )

    # =============================
    # Log de sucesso
    # =============================
    logging.info("FFmpeg executado com sucesso")

    return process.stdout