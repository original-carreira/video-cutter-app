import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.obs_controller import OBSController
from datetime import datetime
import threading
import os
import time

# Certifique-se de que os serviços abaixo existam no seu projeto
# from services.video_cutter import cortar_video
# from services.video_normalizer import normalizar_video
# from utils.time_utils import parse_tempo
# from services.obs_controller import OBSController


# =============================
# 🔥 FUNÇÃO UTILITÁRIA (OBS)
# =============================
def get_latest_video(folder):
    try:
        files = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        
        if not files:
            return None
        
        return max(files, key=os.path.getctime)
    except Exception as e:
        return None

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Video Cutter Pro + OBS")
        self.geometry("520x750")
        
        self.input_path = None
        self.cuts = []

        # Grid Base (Responsivo)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        
        self.obs = None  # Controlador OBS
        self.is_recording = False

        self.setup_ui()

    def setup_ui(self):
        # Título
        ctk.CTkLabel(self, text="Corte de Vídeo Inteligente", font=("Arial", 18, "bold")).grid(row=0, pady=10)

        # Seleção de Arquivo
        self.btn_select = ctk.CTkButton(self, text="📁 Selecionar Vídeo", command=self.select_file)
        self.btn_select.grid(row=1, pady=5)
        
        self.label_file = ctk.CTkLabel(self, text="Nenhum arquivo selecionado", text_color="#1f2937")
        self.label_file.grid(row=2, pady=2)

        # Inputs de Tempo
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.grid(row=3, pady=10)
        
        self.entry_start = ctk.CTkEntry(self.frame_inputs, placeholder_text="Início (HH:MM:SS)", width=140)
        self.entry_start.pack(side="left", padx=5)
        
        self.entry_end = ctk.CTkEntry(self.frame_inputs, placeholder_text="Fim (HH:MM:SS)", width=140)
        self.entry_end.pack(side="left", padx=5)

        # Switches de Opções
        self.frame_switches = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_switches.grid(row=4, pady=5)
        
        self.switch_reencode = ctk.CTkSwitch(self.frame_switches, text="Modo Compatível (Reencode)")
        self.switch_reencode.pack(pady=2)
        
        self.switch_normalize = ctk.CTkSwitch(self.frame_switches, text="Normalizar Áudio/Vídeo")
        self.switch_normalize.pack(pady=2)

        # Lista de Cortes
        self.text_cuts = ctk.CTkTextbox(self)
        self.text_cuts.grid(row=5, sticky="nsew", padx=20, pady=10)

        # Botões de Lista
        self.frame_list_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_list_actions.grid(row=6, pady=5)
        
        ctk.CTkButton(self.frame_list_actions, text="➕ Adicionar Corte", fg_color="#2563eb", command=self.add_cut).pack(side="left", padx=5)
        ctk.CTkButton(self.frame_list_actions, text="🗑️ Limpar Lista", fg_color="#dc2626", command=self.clear_cuts).pack(side="left", padx=5)

        # Botão de Execução Principal
        self.btn_run = ctk.CTkButton(self, text="🚀 EXECUTAR CORTES", fg_color="#16a34a", font=("Arial", 14, "bold"), command=self.start_process_thread)
        self.btn_run.grid(row=7, pady=(10, 5))

        # Novo Botão OBS 
        self.btn_obs_start = ctk.CTkButton(self, text="🎥 Gravar com OBS", fg_color="#d97706",hover_color="#92400e" ,command=self.start_obs_recording)
        self.btn_obs_start.grid(row=8, pady=5)
        
        self.btn_obs_stop = ctk.CTkButton(self, text="⏹️ Parar Gravação OBS", fg_color="#991b1b", hover_color="#7f1d1d", command=self.stop_obs_recording, state="disabled")
        self.btn_obs_stop.grid(row=9, pady=5)

        # Status e Progresso
        self.label_status = ctk.CTkLabel(self, text="Pronto")
        self.label_status.grid(row=10, pady=2)
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate")
        self.progress_bar.grid(row=11, sticky="ew", padx=20, pady=(0, 20))
        self.progress_bar.set(0)

    # --- Funções de Auxílio ---

    def update_status(self, text, progress):
        self.after(0, lambda: self.label_status.configure(text=text))
        self.after(0, lambda: self.progress_bar.set(progress))

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.input_path = path
            self.label_file.configure(text=os.path.basename(path), text_color="white")

    def add_cut(self):
        start, end = self.entry_start.get().strip(), self.entry_end.get().strip()
        if start and end:
            self.cuts.append((start, end))
            self.text_cuts.insert("end", f"{start} → {end}\n")
            self.entry_start.delete(0, 'end')
            self.entry_end.delete(0, 'end')

    def clear_cuts(self):
        self.cuts.clear()
        self.text_cuts.delete("1.0", "end")
        self.progress_bar.set(0)

    # --- Processamento de Vídeo ---

    def start_process_thread(self):
        if not self.input_path or not self.cuts:
            return messagebox.showwarning("Aviso", "Selecione um vídeo e adicione cortes.")
        
        self.btn_run.configure(state="disabled")
        threading.Thread(target=self.execute_cuts_task, daemon=True).start()

    def execute_cuts_task(self):
        try:
            from services.video_cutter import cortar_video
            from services.video_normalizer import normalizar_video
            
            output_dir = "videos/cuts"
            os.makedirs(output_dir, exist_ok=True)

            video_src = normalizar_video(self.input_path) if self.switch_normalize.get() else self.input_path

            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, (start, end) in enumerate(self.cuts, 1):
                self.update_status(f"Processando corte {i}/{len(self.cuts)}", i/len(self.cuts))
                out = os.path.join(output_dir, f"{base_name}_cut_{i}_{timestamp}.mp4")
                cortar_video(video_src, start, end, out, reencode=self.switch_reencode.get())

            self.after(0, self.finalizar_sucesso)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))
        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal"))

    def finalizar_sucesso(self):
        self.update_status("Concluído", 1)
        if messagebox.askyesno("Sucesso", "Cortes prontos! Abrir pasta?"):
            os.startfile(os.path.abspath("videos/cuts"))
        self.clear_cuts()

    # --- Integração com OBS ---
    
    def start_obs_recording(self):
        if self.is_recording:
            return messagebox.showinfo("Info", "Já está gravando com OBS.")
        
        def task():
            try:
                self.obs = OBSController(password="Sg@273220")  # ajuste sua senha
                self.obs.connect()
                self.obs.start_recording()
                self.is_recording = True
                
                self.after(0, lambda: self.btn_obs_start.configure(state="disabled"))
                self.after(0, lambda: self.btn_obs_stop.configure(state="normal"))
                
                self.update_status("Gravando com OBS...", 0)
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: messagebox.showerror("Erro OBS", error_msg))

        threading.Thread(target=task, daemon=True).start()

    def stop_obs_recording(self):
        if not self.is_recording or not self.obs:
            return messagebox.showinfo("Info", "Não está gravando com OBS.")
        
        def task():
            try:
                self.obs.stop_recording()
                self.obs.disconnect()
                
                self.is_recording = False
                self.obs = None
                
                self.after(0, lambda: self.btn_obs_start.configure(state="normal"))
                self.after(0, lambda: self.btn_obs_stop.configure(state="disabled"))
                
                self.update_status("Gravação OBS parada", 1)
                
                # =============================
                # 🔥 AUTO IMPORT DO VÍDEO
                # =============================
                time.sleep(1.5)
                
                latest_video = get_latest_video(os.path.join(os.path.expanduser("~"), "Videos"))
                
                if latest_video:
                    self.input_path = latest_video
                    
                    self.after(0, lambda: self.label_file.configure(
                        text=os.path.basename(latest_video), text_color="#1f2937"
                        ))
                    
                    self.update_status("Vídeo importado do OBS!", 1)
                    
                else:
                    self.update_status("Gravação finalizada, mas não foi possível encontrar o vídeo.", 1)
                    
                
                
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda: messagebox.showerror("Erro OBS", error_msg))
                
        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
