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
    """Carrega histórico salvo do arquivo JSON"""
    if not os.path.exists("history.json"):
        return []
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_history(data):
    """Salva a lista de histórico no arquivo JSON"""
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# =============================================================
# 🖥️ JANELA PRINCIPAL
# =============================================================

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Cutter Pro + OBS History")
        self.geometry("550x950")

        # =============================
        # Estado da aplicação
        # =============================
        self.input_path = None
        self.cuts = []              # 🔥 fila atual (sessão)
        self.obs = None
        self.is_recording = False
        self.history = load_history()

        # Layout responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.setup_ui()
        self.refresh_history_display()

    # =============================================================
    # 🎨 INTERFACE GRÁFICA (UI)
    # =============================================================

    def setup_ui(self):
        ctk.CTkLabel(self, text="Corte de Vídeo Inteligente", font=("Arial", 20, "bold")).grid(row=0, pady=15)

        # 📂 Arquivo
        self.frame_file = ctk.CTkFrame(self)
        self.frame_file.grid(row=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_file, text="📂 Arquivo", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        self.btn_select = ctk.CTkButton(self.frame_file, text="Selecionar Vídeo", command=self.select_file)
        self.btn_select.pack(pady=5)

        self.label_file = ctk.CTkLabel(
            self.frame_file,
            text="Nenhum arquivo selecionado",
            text_color="#1f2937"
        )
        self.label_file.pack(pady=5)

        # ⏱️ Tempo
        self.frame_time = ctk.CTkFrame(self)
        self.frame_time.grid(row=2, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_time, text="⏱️ Tempo do Corte", font=("Arial", 12, "bold")).pack()

        self.frame_inputs = ctk.CTkFrame(self.frame_time, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        self.entry_start = ctk.CTkEntry(self.frame_inputs, placeholder_text="HH:MM:SS", width=150)
        self.entry_start.pack(side="left", padx=5)

        self.entry_end = ctk.CTkEntry(self.frame_inputs, placeholder_text="HH:MM:SS", width=150)
        self.entry_end.pack(side="left", padx=5)

        # 📋 Fila de cortes
        self.frame_cuts = ctk.CTkFrame(self)
        self.frame_cuts.grid(row=5, padx=10, pady=5, sticky="nsew")

        ctk.CTkLabel(self.frame_cuts, text="📋 Fila de Processamento", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        self.text_cuts = ctk.CTkTextbox(self.frame_cuts, height=120)
        self.text_cuts.pack(fill="both", expand=True, padx=10, pady=5)

        self.text_cuts.insert("end", "Nenhum corte adicionado ainda...\n")

        # 🎬 Ações
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.grid(row=6, pady=5)

        ctk.CTkButton(self.frame_actions, text="➕ Adicionar", command=self.add_cut).pack(side="left", padx=5)
        ctk.CTkButton(self.frame_actions, text="🗑️ Limpar Fila", command=self.clear_cuts, fg_color="#dc2626").pack(side="left", padx=5)

        # 📜 Histórico
        self.frame_history = ctk.CTkFrame(self)
        self.frame_history.grid(row=7, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_history, text="📜 Histórico Recente", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

        self.scroll_history = ctk.CTkScrollableFrame(self.frame_history, height=150)
        self.scroll_history.pack(fill="x", padx=10, pady=5)

        # 🚀 Executar
        self.btn_run = ctk.CTkButton(
            self,
            text="🚀 EXECUTAR TODOS OS CORTES",
            fg_color="#16a34a",
            font=("Arial", 14, "bold"),
            height=40,
            command=self.start_process_thread
        )
        self.btn_run.grid(row=8, pady=10, padx=20, sticky="ew")

        # 🎥 OBS
        self.frame_obs = ctk.CTkFrame(self)
        self.frame_obs.grid(row=9, padx=10, pady=5, sticky="ew")

        self.btn_obs_start = ctk.CTkButton(
            self.frame_obs,
            text="🔴 Iniciar OBS",
            command=self.start_obs_recording,
            fg_color="#d97706",
            hover_color="#92400e"
        )
        self.btn_obs_start.pack(side="left", expand=True, padx=5, pady=10)

        self.btn_obs_stop = ctk.CTkButton(
            self.frame_obs,
            text="⏹️ Parar OBS",
            command=self.stop_obs_recording,
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            state="disabled"
        )
        self.btn_obs_stop.pack(side="left", expand=True, padx=5, pady=10)

        # 📊 Status
        self.label_status = ctk.CTkLabel(self, text="Pronto para iniciar")
        self.label_status.grid(row=10, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.grid(row=11, sticky="ew", padx=20, pady=(0, 20))
        self.progress_bar.set(0.02)

    # =============================================================
    # ⚙️ LÓGICA
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
        start, end = self.entry_start.get().strip(), self.entry_end.get().strip()

        if start and end:
            if len(self.cuts) == 0:
                self.text_cuts.delete("1.0", "end")

            self.cuts.append((start, end))
            self.text_cuts.insert("end", f"Corte {len(self.cuts)}: {start} → {end}\n")

            # histórico
            self.history.append({
                "file": self.input_path,
                "start": start,
                "end": end,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
            save_history(self.history)
            self.refresh_history_display()

            self.entry_start.delete(0, "end")
            self.entry_end.delete(0, "end")

    def clear_cuts(self):
        self.cuts.clear()
        self.text_cuts.delete("1.0", "end")
        self.text_cuts.insert("end", "Nenhum corte adicionado ainda...\n")

    def refresh_history_display(self):
        for widget in self.scroll_history.winfo_children():
            widget.destroy()

        for item in reversed(self.history[-10:]):
            txt = f"{item['date']} | {item['start']} - {item['end']}"
            ctk.CTkLabel(self.scroll_history, text=txt, anchor="w").pack(fill="x")

    # =============================================================
    # 🎞️ PROCESSAMENTO
    # =============================================================

    def start_process_thread(self):
        if not self.input_path or not self.cuts:
            return messagebox.showwarning("Aviso", "Nada para processar.")

        self.btn_run.configure(state="disabled")
        threading.Thread(target=self.execute_cuts_task, daemon=True).start()

    def execute_cuts_task(self):
        try:
            from services.video_cutter import cortar_video

            output_dir = "videos/cuts"
            os.makedirs(output_dir, exist_ok=True)

            base = os.path.splitext(os.path.basename(self.input_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for i, (start, end) in enumerate(self.cuts, 1):
                self.update_status(f"Processando corte {i}/{len(self.cuts)}", i/len(self.cuts))

                out = os.path.join(output_dir, f"{base}_corte_{i}_{timestamp}.mp4")
                cortar_video(self.input_path, start, end, out)

            def finalizar():
                self.update_status("Processamento concluído!", 1)

                if messagebox.askyesno("Sucesso", "Abrir pasta dos cortes?"):
                    os.startfile(os.path.abspath(output_dir))

                self.clear_cuts()

            self.after(0, finalizar)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal"))

    # =============================================================
    # 🎥 OBS
    # =============================================================

    def start_obs_recording(self):
        from services.obs_controller import OBSController

        def task():
            try:
                self.after(0, lambda: self.progress_bar.configure(mode="indeterminate"))
                self.after(0, self.progress_bar.start)

                self.obs = OBSController(password="Sg@273220")
                self.obs.connect()
                self.obs.start_recording()

                self.after(0, lambda: self.btn_obs_start.configure(state="disabled"))
                self.after(0, lambda: self.btn_obs_stop.configure(state="normal"))

                self.update_status("🔴 Gravando com OBS...")

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro OBS", str(e)))

        threading.Thread(target=task, daemon=True).start()

    def stop_obs_recording(self):
        def task():
            try:
                self.obs.stop_recording()
                self.obs.disconnect()

                self.after(0, lambda: self.btn_obs_start.configure(state="normal"))
                self.after(0, lambda: self.btn_obs_stop.configure(state="disabled"))

                self.after(0, self.progress_bar.stop)
                self.after(0, lambda: self.progress_bar.configure(mode="determinate"))

                self.update_status("Finalizando gravação...", 0.5)

                time.sleep(1.5)

                latest = get_latest_video(os.path.join(os.path.expanduser("~"), "Videos"))

                if latest:
                    self.input_path = latest
                    self.after(0, lambda: self.label_file.configure(
                        text=os.path.basename(latest),
                        text_color="#16a34a"
                    ))
                    self.update_status("Vídeo importado com sucesso", 1)
                else:
                    self.update_status("Arquivo não encontrado", 0)

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erro OBS", str(e)))

        threading.Thread(target=task, daemon=True).start()


# =============================================================
# 🚀 INICIALIZAÇÃO
# =============================================================

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()