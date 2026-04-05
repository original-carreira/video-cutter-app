import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.video_cutter import cortar_video
from services.video_normalizer import normalizar_video
from utils.time_utils import parse_tempo
import threading
import os
import datetime
import platform
import subprocess


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # =============================
        # Configurações da Janela
        # =============================
        self.title("Video Cutter Pro")
        self.geometry("550x500")
        
        # =============================
        # Variáveis de Estado
        # =============================
        self.input_path = None
        self.output_last_path = None
        self.cuts = []  # Lista para armazenar múltiplos cortes

        self.setup_ui()

    # =============================
    # Construção da Interface
    # =============================
    def setup_ui(self):
        """Inicializa os componentes da interface"""
        
        # Título
        self.label_title = ctk.CTkLabel(
            self,
            text="Corte de Vídeo Inteligente",
            font=("Arial", 20, "bold")
        )
        self.label_title.pack(pady=(20, 10))

        # Botão selecionar vídeo
        self.btn_select = ctk.CTkButton(
            self,
            text="Selecionar Vídeo",
            fg_color="#3b8ed0",
            hover_color="#1f538d",
            command=self.select_file
        )
        self.btn_select.pack(pady=10)

        # Nome do arquivo
        self.label_filename = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado",
            font=("Arial", 12, "bold"),
            text_color="#1f1f1f",
            wraplength=400,
            justify="center"
        )
        self.label_filename.pack(pady=(0, 10))

        # Inputs de tempo
        self.time_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.time_frame.pack(pady=5)

        self.entry_start = ctk.CTkEntry(
            self.time_frame,
            placeholder_text="Início (HH:MM:SS)",
            width=150
        )
        self.entry_start.pack(side="left", padx=5)

        self.entry_end = ctk.CTkEntry(
            self.time_frame,
            placeholder_text="Fim (HH:MM:SS)",
            width=150
        )
        self.entry_end.pack(side="left", padx=5)

        # Opções
        self.switch_reencode = ctk.CTkSwitch(self, text="Modo compatível (reencode pesado)")
        self.switch_reencode.pack(pady=5)

        self.switch_normalize = ctk.CTkSwitch(self, text="Normalizar áudio/vídeo")
        self.switch_normalize.pack(pady=5)

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.stop()

        # Lista de cortes
        self.listbox_cuts = ctk.CTkTextbox(self, height=100)
        self.listbox_cuts.pack(pady=5, padx=20, fill="x")

        # Botão adicionar corte
        self.btn_add_cut = ctk.CTkButton(
            self,
            text="Adicionar Corte",
            command=self.add_cut
        )
        self.btn_add_cut.pack(pady=5)

        # Botão limpar lista
        self.btn_clear = ctk.CTkButton(
            self,
            text="Limpar Lista",
            command=self.clear_cuts
        )
        self.btn_clear.pack(pady=5)

        # Botão iniciar corte
        self.btn_cut = ctk.CTkButton(
            self,
            text="Iniciar Corte",
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#2fa572",
            hover_color="#106a43",
            command=self.cut_video
        )
        self.btn_cut.pack(pady=20)

        # Status
        self.label_status = ctk.CTkLabel(self, text="", text_color="#3b8ed0")
        self.label_status.pack(pady=5)

    # =============================
    # Seleção de arquivo
    # =============================
    def select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.mkv *.avi *.mov")]
        )
        if path:
            self.input_path = path
            nome = os.path.basename(path)

            self.label_filename.configure(
                text=f"Arquivo selecionado:\n{nome}",
                text_color="#2b2b2b"
            )

            self.label_status.configure(text="Arquivo pronto para corte.")

    # =============================
    # Adicionar corte
    # =============================
    def add_cut(self):
        start = self.entry_start.get()
        end = self.entry_end.get()

        try:
            start_sec = parse_tempo(start)
            end_sec = parse_tempo(end)

            if end_sec <= start_sec:
                messagebox.showerror("Erro", "Tempo final deve ser maior")
                return

        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        # Evita duplicados
        if (start, end) in self.cuts:
            messagebox.showwarning("Aviso", "Corte já adicionado")
            return

        self.cuts.append((start, end))
        self.listbox_cuts.insert("end", f"{start} → {end}\n")

    # =============================
    # Limpar cortes
    # =============================
    def clear_cuts(self):
        self.cuts.clear()
        self.listbox_cuts.delete("1.0", "end")

    # =============================
    # Geração de nome de saída
    # =============================
    def generate_output_path_multi(self, index):
        folder = "videos/cuts"
        os.makedirs(folder, exist_ok=True)

        filename = os.path.basename(self.input_path)
        name, ext = os.path.splitext(filename)

        return os.path.join(folder, f"{name}_corte_{index}{ext}")

    # =============================
    # Execução do corte (Thread)
    # =============================
    def cut_video(self):

        if self.btn_cut.cget("state") == "disabled":
            return

        if not self.input_path:
            messagebox.showerror("Erro", "Selecione um vídeo!")
            return

        if not self.cuts:
            messagebox.showerror("Erro", "Adicione pelo menos um corte!")
            return

        self.toggle_ui_state("disabled")
        self.progress_bar.start()

        reencode = self.switch_reencode.get()
        normalize = self.switch_normalize.get()

        def process():
            try:
                video = normalizar_video(self.input_path) if normalize else self.input_path

                for i, (start, end) in enumerate(self.cuts, start=1):
                    output = self.generate_output_path_multi(i)

                    cortar_video(
                        video,
                        start,
                        end,
                        output,
                        reencode=reencode
                    )

                self.output_last_path = output
                self.after(0, self.finalizar_sucesso)

            except Exception as e:
                self.after(0, lambda: self.finalizar_erro(str(e)))

        threading.Thread(target=process, daemon=True).start()

    # =============================
    # Controle UI
    # =============================
    def toggle_ui_state(self, state):
        self.btn_cut.configure(state=state)
        self.btn_select.configure(state=state)

    # =============================
    # Finalização sucesso
    # =============================
    def finalizar_sucesso(self):
        self.progress_bar.stop()
        self.toggle_ui_state("normal")

        self.label_status.configure(text="Finalizado!", text_color="#2fa572")

        self.clear_cuts()

        if messagebox.askyesno("Sucesso", "Deseja abrir a pasta?"):
            self.open_file_explorer()

    # =============================
    # Finalização erro
    # =============================
    def finalizar_erro(self, erro):
        self.progress_bar.stop()
        self.toggle_ui_state("normal")

        self.label_status.configure(text="Erro no processamento", text_color="red")
        messagebox.showerror("Erro", "Falha ao processar vídeo")
        print("Erro técnico:", erro)

    # =============================
    # Abrir pasta
    # =============================
    def open_file_explorer(self):
        path = os.path.abspath("videos/cuts")

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()