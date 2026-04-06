import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading
import os
import time
import json

# =============================================================
# 🛠️ FUNÇÕES UTILITÁRIAS
# =============================================================

def get_latest_video(folder):
    """Retorna o vídeo mais recente da pasta"""
    try:
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        return max(files, key=os.path.getctime) if files else None
    except Exception:
        return None


def load_history():
    """Carrega histórico salvo"""
    if not os.path.exists("history.json"):
        return []
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_history(data):
    """Salva histórico"""
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =============================================================
# 🖥️ JANELA PRINCIPAL
# =============================================================

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Cutter Pro + OBS")
        self.geometry("520x900")

        self.input_path = None
        self.cuts = []
        self.obs = None
        self.is_recording = False

        self.history = load_history()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.setup_ui()

    # =============================================================
    # 🎨 UI
    # =============================================================

    def setup_ui(self):

        ctk.CTkLabel(self, text="Corte de Vídeo Inteligente", font=("Arial", 20, "bold")).grid(row=0, pady=15)

        # 📂 Arquivo
        self.frame_file = ctk.CTkFrame(self)
        self.frame_file.grid(row=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_file, text="📂 Arquivo", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        
        self.btn_select = ctk.CTkButton(self.frame_file, text="Selecionar Vídeo", command=self.select_file)
        self.btn_select.pack(pady=5)
        
        # 🔥 Label para mostrar nome do arquivo selecionado 
        self.label_file = ctk.CTkLabel(self.frame_file, text="Nenhum arquivo selecionado", text_color="#1f2937")
        self.label_file.pack(pady=5)

        # ⏱️ Tempo
        self.frame_time = ctk.CTkFrame(self)
        self.frame_time.grid(row=2, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_time, text="⏱️ Tempo do Corte", font=("Arial", 12, "bold")).pack()

        self.frame_inputs = ctk.CTkFrame(self.frame_time, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        self.entry_start = ctk.CTkEntry(self.frame_inputs, placeholder_text="Início - HH:MM:SS", width=150)
        self.entry_start.pack(side="left", padx=5)

        self.entry_end = ctk.CTkEntry(self.frame_inputs, placeholder_text="Fim - HH:MM:SS", width=150)
        self.entry_end.pack(side="left", padx=5)

        # ⚙️ Opções
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.grid(row=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_options, text="⚙️ Opções", font=("Arial", 12, "bold")).pack()

        self.switch_reencode = ctk.CTkSwitch(self.frame_options, text="Modo Compatível")
        self.switch_reencode.pack()

        self.switch_normalize = ctk.CTkSwitch(self.frame_options, text="Normalizar")
        self.switch_normalize.pack()

        # 📋 Cortes
        self.frame_cuts = ctk.CTkFrame(self)
        self.frame_cuts.grid(row=5, padx=10, pady=5, sticky="nsew")

        ctk.CTkLabel(self.frame_cuts, text="📋 Lista de Cortes", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        self.text_cuts = ctk.CTkTextbox(self.frame_cuts)
        self.text_cuts.pack(fill="both", expand=True, padx=10, pady=5)
        self.text_cuts.insert("end", "Nenhum corte adicionado\n")

        # 🎬 Ações
        self.frame_actions = ctk.CTkFrame(self)
        self.frame_actions.grid(row=6, pady=5)

        ctk.CTkButton(self.frame_actions, text="➕ Adicionar", command=self.add_cut).pack(side="left", padx=5)
        ctk.CTkButton(self.frame_actions, text="🗑️ Limpar", command=self.clear_cuts).pack(side="left", padx=5)

        # 🚀 Executar
        self.btn_run = ctk.CTkButton(self, text="🚀 EXECUTAR CORTES", fg_color="#16a34a",
                                    font=("Arial", 14, "bold"), height=40,
                                    command=self.start_process_thread)
        self.btn_run.grid(row=7, pady=10, padx=10, sticky="ew")

        # 🎥 OBS
        self.frame_obs = ctk.CTkFrame(self)
        self.frame_obs.grid(row=8, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_obs, text="🎥 OBS", font=("Arial", 12, "bold")).pack()

        self.frame_obs_buttons = ctk.CTkFrame(self.frame_obs, fg_color="transparent")
        self.frame_obs_buttons.pack()

        self.btn_obs_start = ctk.CTkButton(self.frame_obs_buttons, text="🔴 Iniciar",
                                          command=self.start_obs_recording, 
                                          fg_color="#d97706", hover_color="#156E49", state="normal")
        self.btn_obs_start.pack(side="left", padx=5)

        self.btn_obs_stop = ctk.CTkButton(self.frame_obs_buttons, text="⏹️ Parar",
                                         command=self.stop_obs_recording,
                                         fg_color="#991b1b", hover_color="#92400E", state="disabled")
        self.btn_obs_stop.pack(side="left", padx=5)

        # 📊 Status
        self.label_status = ctk.CTkLabel(self, text="Pronto")
        self.label_status.grid(row=9, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.grid(row=10, sticky="ew", padx=10)
        self.progress_bar.set(0)

    # =============================================================
    # ⚙️ FUNÇÕES
    # =============================================================

    def update_status(self, text, progress=None):
        self.after(0, lambda: self.label_status.configure(text=text))
        if progress is not None:
            self.after(0, lambda: self.progress_bar.set(progress))

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.input_path = path
            self.label_file.configure(text=os.path.basename(path), text_color="white")

    def add_cut(self):
        start = self.entry_start.get()
        end = self.entry_end.get()

        if start and end:
            # remove mensagem inicial se for o primeiro corte
            if len(self.cuts) == 0:
                self.text_cuts.delete("1.0", "end")
                
            self.cuts.append((start, end))
            self.text_cuts.insert("end", f"Corte {len(self.cuts)}: {start} → {end}\n")
            
            self.entry_start.delete(0, "end")
            self.entry_end.delete(0, "end")
            
            # 🔥 salva no histórico
            self.history.append({
                "file": self.input_path,
                "start": start,
                "end": end,
                "date": datetime.now().isoformat()
            })
            save_history(self.history)

    def clear_cuts(self):
        self.cuts.clear()
        self.text_cuts.delete("1.0", "end")
        self.text_cuts.insert("end", "Nenhum corte adicionado ainda ...\n")

    # =============================================================
    # 🎞️ PROCESSAMENTO
    # =============================================================

    def start_process_thread(self):
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        from services.video_cutter import cortar_video

        try:
            self.update_status("Processando...", 0)
            for i, (start, end) in enumerate(self.cuts):
                cortar_video(self.input_path, start, end,
                             f"videos/cuts/corte_{i}.mp4")
                self.update_status(f"Corte {i+1}", (i+1)/len(self.cuts))

            self.update_status("Concluído", 1)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # =============================================================
    # 🎥 OBS
    # =============================================================

    def start_obs_recording(self):
        from services.obs_controller import OBSController

        def task():
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()

            self.obs = OBSController(password="Sg@273220")
            self.obs.connect()
            self.obs.start_recording()

            self.is_recording = True

            self.after(0, lambda: self.btn_obs_start.configure(state="disabled"))
            self.after(0, lambda: self.btn_obs_stop.configure(state="normal"))

            self.update_status("Gravando...")

        threading.Thread(target=task, daemon=True).start()

    def stop_obs_recording(self):
        def task():
            self.obs.stop_recording()
            self.obs.disconnect()

            self.is_recording = False

            self.after(0, lambda: self.btn_obs_start.configure(state="normal"))
            self.after(0, lambda: self.btn_obs_stop.configure(state="disabled"))

            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate")

            time.sleep(1.5)

            folder = os.path.join(os.path.expanduser("~"), "Videos")
            latest = get_latest_video(folder)

            if latest:
                self.input_path = latest
                self.after(0, lambda: self.label_file.configure(
                    text=os.path.basename(latest),
                    text_color="#2ecc71"
                ))
                self.update_status("Importado com sucesso", 1)

        threading.Thread(target=task, daemon=True).start()


# =============================================================
# 🚀 INICIALIZAÇÃO
# =============================================================

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()