import logging
import os
import sys
from ui.main_window import MainWindow  # 🔥 IMPORTANTE


# =============================
# Caminho base (funciona no .exe)
# =============================
def get_base_path():
    # Verificar se estamos rodando em um ambiente empacotado (PyInstaller)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# =============================
# Caminho para dados do app (logs)
# =============================
def get_appdata_path():
    """Retorna pasta correta para dados do app"""
    app_name = "VideoCutter"

    if os.name == "nt":  # Windows
        base_dir = os.getenv("APPDATA")
    else:
        base_dir = os.path.expanduser("~")

    app_dir = os.path.join(base_dir, app_name)
    log_dir = os.path.join(app_dir, "logs")

    os.makedirs(log_dir, exist_ok=True)

    return log_dir

# =============================
# Setup de logs
# =============================
def setup_logging():
    # Configurar logging para arquivo
    log_dir = get_appdata_path()
    
    log_file = os.path.join(log_dir, "app.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
# =============================
# Execução principal
# =============================
if __name__ == "__main__":
    setup_logging()
    logging.info("Aplicação iniciada")

    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logging.error(f"Erro fatal na aplicação: {e}", exc_info=True)