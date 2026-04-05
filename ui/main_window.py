import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.video_cutter import cortar_video
from services.video_normalizer import normalizar_video
from utils.time_utils import parse_tempo
from services.obs_controller import OBSController
import threading
import os
import platform
import subprocess
import logging
import time


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # =============================
        # Configurações da Janela
        # =============================
        self.title("Video Cutter Pro")
        self.geometry("650x600")
        self.minsize(600, 600)
        self.resizable(False, False)

        self.center_window()

        # =============================
        # Variáveis de Estado
        # =============================
        self.input_path = None
        self.output_last_path = None
        self.cuts = []  # Lista para armazenar múltiplos cortes

        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        """Inicializa os componentes da interface"""

        self.label_title = ctk.CTkLabel(self, text="Corte de Vídeo Inteligente", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=(20, 10))

        self.btn_select = ctk.CTkButton(self, text="Selecionar Vídeo", fg_color="#3b8ed0", hover_color="#1f538d", command=self.select_file)
        self.btn_select.pack(pady=10)

        self.label_filename = ctk.CTkLabel(self, text="Nenhum arquivo selecionado", font=("Arial", 12, "bold"), text_color="#1f1f1f", wraplength=400)
        self.label_filename.pack(pady=(0, 10))

        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(pady=5)

        self.entry_start = ctk.CTkEntry(self.time_frame, placeholder_text="Início (HH:MM:SS)", width=150)
        self.entry_start.pack(side="left", padx=5)

        self.entry_end = ctk.CTkEntry(self.time_frame, placeholder_text="Fim (HH:MM:SS)", width=150)
        self.entry_end.pack(side="left", padx=5)

        self.switch_reencode = ctk.CTkSwitch(self, text="Modo compatível (reencode pesado)")
        self.switch_reencode.pack(pady=5)

        self.switch_normalize = ctk.CTkSwitch(self, text="Normalizar áudio/vídeo")
        self.switch_normalize.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.stop()

        self.listbox_cuts = ctk.CTkTextbox(self, height=100)
        self.listbox_cuts.pack(pady=5, padx=20, fill="x")

        self.btn_add_cut = ctk.CTkButton(self, text="Adicionar Corte", command=self.add_cut)
        self.btn_add_cut.pack(pady=5)

        self.btn_clear = ctk.CTkButton(self, text="Limpar Lista", command=self.clear_cuts)
        self.btn_clear.pack(pady=5)

        self.btn_cut = ctk.CTkButton(self, text="Executar Cortes", height=40, font=("Arial", 14, "bold"), fg_color="#2fa572", hover_color="#106a43", command=self.cut_video)
        self.btn_cut.pack(pady=20)

        self.label_status = ctk.CTkLabel(self, text="", text_color="#3b8ed0")
        self.label_status.pack(pady=5)

        self.btn_record = ctk.CTkButton(
            self,text="Gravar Trecho (OBS)",
            fg_color="#d97706",
            hover_color="#b45309",
            command=self.record_with_obs
            )
        self.btn_record.pack(pady=5)
        
    def record_with_obs(self):
        obs = OBSController(password="Sg@273220")
        
        try:
            obs.connect()
            
            self.label_status.configure(text="Gravando... Clique novamente para parar.", text_color="#d97706")
            
            obs.start_recording()
            
            time.sleep(10)  # Grava por 10 segundos (ajuste conforme necessário)
            obs.stop_recording()
            obs.disconnect()
            
            self.label_status.configure(text="Gravação concluída!", text_color="#2fa572")
        except Exception as e:
            messagebox.showerror("Erro OBS", f"Falha na gravação com OBS:\n{str(e)}")
            
        
    
    
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Vídeos", "*.mp4 *.mkv *.avi *.mov")])
        if path:
            self.input_path = path
            self.label_filename.configure(text=f"Arquivo selecionado:\n{os.path.basename(path)}", text_color="#2b2b2b")
            self.label_status.configure(text="Arquivo pronto para corte.")

    def add_cut(self):
        start, end = self.entry_start.get(), self.entry_end.get()
        try:
            if parse_tempo(end) <= parse_tempo(start):
                messagebox.showerror("Erro", "Tempo final deve ser maior")
                return
            if (start, end) in self.cuts:
                return
            self.cuts.append((start, end))
            self.listbox_cuts.insert("end", f"{start} → {end}\n")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def clear_cuts(self):
        self.cuts.clear()
        self.listbox_cuts.delete("1.0", "end")

    def generate_output_path_multi(self, index):
        folder = "videos/cuts"
        os.makedirs(folder, exist_ok=True)
        name, ext = os.path.splitext(os.path.basename(self.input_path))
        return os.path.join(folder, f"{name}_corte_{index}{ext}")

    def toggle_ui_state(self, state):
        """Habilita/Desabilita componentes durante o processo"""
        buttons = [self.btn_cut, self.btn_select, self.btn_add_cut, self.btn_clear, 
                   self.switch_reencode, self.switch_normalize]
        for btn in buttons:
            btn.configure(state=state)

    def cut_video(self):
        if not self.input_path or not self.cuts:
            messagebox.showerror("Erro", "Selecione um vídeo e adicione cortes!")
            return

        self.toggle_ui_state("disabled")
        self.progress_bar.start()
        
        reencode, normalize = self.switch_reencode.get(), self.switch_normalize.get()

        def process():
            try:
                video = normalizar_video(self.input_path) if normalize else self.input_path
                for i, (start, end) in enumerate(self.cuts, start=1):
                    self.after(0,
                               lambda idx=i, total=len(self.cuts):
                                   self.label_status.configure(
                                       text=f"Cortando {idx}/{total}..."
                                       )
                                   )
                    output = self.generate_output_path_multi(i)
                    cortar_video(video, start, end, output, reencode=reencode)
                
                self.after(0, lambda: self.finalizar_sucesso())
            except Exception as e:
                self.after(0, lambda: self.finalizar_erro(str(e)))

        threading.Thread(target=process, daemon=True).start()

    def finalizar_sucesso(self):
        logging.info("UI finalizada com sucesso")        
        try:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            self.toggle_ui_state("normal")
        except Exception as e:
            print("Erro na finalização:", e)

        self.label_status.configure(text="Processamento concluído", text_color="#2fa572")
        if messagebox.askyesno("Sucesso!", "Deseja abrir a pasta?"):
            self.open_file_explorer()
        self.clear_cuts()

    def finalizar_erro(self, mensagem):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.toggle_ui_state("normal")
        self.label_status.configure(text="Erro no processamento", text_color="#cc0000")
        messagebox.showerror("Erro crítico", f"O FFmpeg falhou:\n{mensagem}")

    def open_file_explorer(self):
        path = os.path.abspath("videos/cuts")
        if not os.path.exists(path): os.makedirs(path)
        
        if platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.Popen(["open" if platform.system() == "Darwin" else "xdg-open", path])
