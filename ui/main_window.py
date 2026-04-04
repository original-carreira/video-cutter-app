import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.video_cutter import cortar_video
from services.video_normalizer import normalizar_video
from utils.time_utils import parse_tempo
import os


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Video Cutter")
        self.geometry("500x400")

        self.input_path = None

        self.btn_select = ctk.CTkButton(self, text="Selecionar Vídeo", command=self.select_file)
        self.btn_select.pack(pady=10)

        self.entry_start = ctk.CTkEntry(self, placeholder_text="Início (HH:MM:SS)")
        self.entry_start.pack(pady=5)

        self.entry_end = ctk.CTkEntry(self, placeholder_text="Fim (HH:MM:SS)")
        self.entry_end.pack(pady=5)

        self.switch_reencode = ctk.CTkSwitch(self, text="Modo compatível (reencode)")
        self.switch_reencode.pack(pady=10)

        self.btn_cut = ctk.CTkButton(self, text="Cortar Vídeo", command=self.cut_video)
        self.btn_cut.pack(pady=20)

    def select_file(self):
        self.input_path = filedialog.askopenfilename()
        messagebox.showinfo("Arquivo", f"Selecionado:\n{self.input_path}")

    def cut_video(self):
        video_processado = normalizar_video(self.input_path)

        if not self.input_path:
            messagebox.showerror("Erro", "Selecione um vídeo")
            return

        start = self.entry_start.get()
        end = self.entry_end.get()

        try:
            inicio_seg = parse_tempo(start)
            fim_seg = parse_tempo(end)

            if fim_seg <= inicio_seg:
                messagebox.showerror("Erro", "O tempo final deve ser maior que o inicial")
                return

        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        output_path = self.generate_output_path()

        try:
            cortar_video(
                video_processado,
                start,
                end,
                output_path,
                reencode=self.switch_reencode.get()
            )
            messagebox.showinfo("Sucesso", f"Vídeo salvo em:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Erro ao processar vídeo", str(e))

    def generate_output_path(self):
        base, ext = os.path.splitext(self.input_path)
        return f"{base}_corte{ext}"