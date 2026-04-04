import logging
from ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        filename='logs/app.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

if __name__ == "__main__":
    setup_logging()
    app = MainWindow()
    app.mainloop()