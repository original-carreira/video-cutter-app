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

        # Configurações da Janela
        self.title("Video Cutter Pro")
        self.geometry("550x500")
        
        # Variáveis de Estado
        self.input_path = None
        self.output_last_path = None

        self.setup_ui()

    def setup_ui(self):
        """Inicializa os componentes da interface"""
        
        # Título Central
        self.label_title = ctk.CTkLabel(self, text="Corte de Vídeo Inteligente", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=(20, 10))

        # Botão selecionar vídeo (Melhorado com feedback de nome)
        self.btn_select = ctk.CTkButton(
            self,
            text="Selecionar Vídeo",
            fg_color="#3b8ed0",
            hover_color="#1f538d",
            command=self.select_file
        )
        self.btn_select.pack(pady=10)

        self.label_filename = ctk.CTkLabel(
            self,
            text="Nenhum arquivo selecionado",
            font=("Arial", 11),
            text_color="gray"
        )
        self.label_filename.pack(pady=(0, 10))

        # Container para os campos de tempo (Lado a lado)
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

        # Opções de Processamento
        self.switch_reencode = ctk.CTkSwitch(self, text="Modo compatível (reencode pesado)")
        self.switch_reencode.pack(pady=5)

        self.switch_normalize = ctk.CTkSwitch(self, text="Normalizar áudio/vídeo (pré-processamento)")
        self.switch_normalize.pack(pady=5)

        # Barra de Progresso (Invisível por padrão)
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.stop()  # set(0) removido (não necessário para modo indeterminate)

        # Botão cortar
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

        # Label status
        self.label_status = ctk.CTkLabel(self, text="", text_color="#3b8ed0")
        self.label_status.pack(pady=5)

    # =============================
    # Selecionar arquivo
    # =============================
    def select_file(self):
        path = filedialog.askopenfilename(
            title="Selecione o vídeo",
            filetypes=[("Arquivos de Vídeo", "*.mp4 *.mkv *.avi *.mov")]
        )
        if path:
            self.input_path = path
            nome_arq = os.path.basename(path)

            self.label_filename.configure(
                text=f"Arquivo: {nome_arq}",
                text_color="white"
            )

            self.btn_select.configure(text="Trocar Vídeo")

            # 🔹 Feedback adicional
            self.label_status.configure(text="Arquivo carregado. Pronto para cortar.", text_color="#3b8ed0")

    # =============================
    # Geração do caminho de saída (Melhorado: Evita sobrescrita)
    # =============================
    def generate_output_path(self):
        folder = "videos/cuts"
        os.makedirs(folder, exist_ok=True)

        filename = os.path.basename(self.input_path)
        name, ext = os.path.splitext(filename)
        
        # Adiciona timestamp para não perder cortes anteriores
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        return os.path.join(folder, f"{name}_corte_{timestamp}{ext}")

    # =============================
    # Função principal (Processamento em Thread)
    # =============================
    def cut_video(self):

        # Evita múltiplos cliques
        if self.btn_cut.cget("state") == "disabled":
            return

        # Validação de entrada
        if not self.input_path:
            messagebox.showerror("Erro", "Por favor, selecione um vídeo primeiro!")
            return

        start = self.entry_start.get()
        end = self.entry_end.get()

        try:
            start_sec = parse_tempo(start)
            end_sec = parse_tempo(end)

            if end_sec <= start_sec:
                messagebox.showerror("Erro", "O tempo final deve ser maior que o inicial!")
                return

        except ValueError as e:
            messagebox.showerror("Erro", f"Formato de tempo inválido: {e}")
            return

        # Bloqueia UI e ativa progresso
        self.toggle_ui_state("disabled")
        self.progress_bar.configure(indeterminate_speed=1.5)
        self.progress_bar.start()

        # 🔹 Mensagem diferenciada se normalização estiver ativa
        if self.switch_normalize.get():
            self.label_status.configure(
                text="Normalizando vídeo... (etapa mais demorada)",
                text_color="#3b8ed0"
            )
        else:
            self.label_status.configure(
                text="Processando corte...",
                text_color="#3b8ed0"
            )

        # Captura estados dos switches
        reencode = self.switch_reencode.get()
        normalize = self.switch_normalize.get()

        def process_thread():
            try:
                # Normalização opcional
                video_para_cortar = (
                    normalizar_video(self.input_path) 
                    if normalize else self.input_path
                )

                self.output_last_path = self.generate_output_path()

                # Executa o serviço de corte
                cortar_video(
                    video_para_cortar,
                    start,
                    end,
                    self.output_last_path,
                    reencode=reencode
                )

                self.after(0, self.finalizar_sucesso)

            except Exception as e:
                self.after(0, lambda: self.finalizar_erro(str(e)))

        threading.Thread(target=process_thread, daemon=True).start()

    # =============================
    # Helpers e Finalização
    # =============================
    def toggle_ui_state(self, state):
        """Habilita ou desabilita botões críticos durante o processo"""
        self.btn_cut.configure(state=state)
        self.btn_select.configure(state=state)
        self.entry_start.configure(state=state)
        self.entry_end.configure(state=state)

    def finalizar_sucesso(self):
        self.progress_bar.stop()
        self.toggle_ui_state("normal")

        self.label_status.configure(
            text="Finalizado com sucesso!",
            text_color="#2fa572"
        )

        if messagebox.askyesno(
            "Sucesso",
            f"Vídeo salvo em:\n{self.output_last_path}\n\nDeseja abrir a pasta agora?"
        ):
            self.open_file_explorer()

    def finalizar_erro(self, erro_msg):
        self.progress_bar.stop()
        self.toggle_ui_state("normal")

        self.label_status.configure(
            text="Erro no processamento",
            text_color="#e74c3c"
        )

        # 🔹 Mensagem amigável ao usuário
        messagebox.showerror(
            "Erro",
            "Falha ao processar o vídeo.\n\n"
            "Dica: tente ativar o modo compatível (reencode ou normalização)."
        )

        # 🔹 Log técnico (console)
        print("Erro detalhado:", erro_msg)

    def open_file_explorer(self):
        """Abre a pasta onde o vídeo foi salvo de forma cross-platform"""
        path = os.path.abspath(os.path.dirname(self.output_last_path))

        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()