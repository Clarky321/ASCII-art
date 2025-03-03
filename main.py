"""
import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tkinter.messagebox as messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ASCIIArtConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер в ASCII Art")

        # Настройка размеров окна
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)

        # Инициализация переменных
        self.setup_variables()

        # Создание интерфейса
        self.create_widgets()

    def setup_variables(self):
        self.gradient = list(" .,:;irsXA253hMHGS#9B&@")
        self.max_width = 200
        self.font_ratio = 0.55
        self.ascii_art = ""
        self.font_size = 8

        try:
            self.font = ImageFont.truetype("cour.ttf", self.font_size)
        except:
            try:
                self.font = ImageFont.truetype("DejaVuSansMono.ttf", self.font_size)
            except:
                self.font = ImageFont.load_default()

    def create_widgets(self):
        # Основная сетка
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Панель инструментов
        toolbar = ctk.CTkFrame(self.root, height=40)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.load_btn = ctk.CTkButton(
            toolbar, text="Загрузить изображение", command=self.load_image
        )
        self.load_btn.pack(side="left", padx=5, pady=2)

        self.save_btn = ctk.CTkButton(
            toolbar, text="Сохранить ASCII Art", command=self.save_ascii_image
        )
        self.save_btn.pack(side="left", padx=5, pady=2)

        # Область предпросмотра изображения
        self.original_frame = ctk.CTkFrame(self.root)
        self.original_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.original_label = ctk.CTkLabel(self.original_frame, text="")
        self.original_label.pack(expand=True, fill="both")

        # Область ASCII арта
        self.ascii_frame = ctk.CTkFrame(self.root)
        self.ascii_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Текстовое поле с прокруткой
        self.ascii_text = ctk.CTkTextbox(
            self.ascii_frame,
            wrap="none",
            font=("Courier", self.font_size),
            fg_color="black",
            text_color="white",
        )

        self.scroll_y = ctk.CTkScrollbar(
            self.ascii_frame, orientation="vertical", command=self.ascii_text.yview
        )
        self.scroll_x = ctk.CTkScrollbar(
            self.ascii_frame, orientation="horizontal", command=self.ascii_text.xview
        )

        self.ascii_text.configure(yscrollcommand=self.scroll_y.set)
        self.ascii_text.configure(xscrollcommand=self.scroll_x.set)

        self.ascii_text.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.ascii_frame.grid_rowconfigure(0, weight=1)
        self.ascii_frame.grid_columnconfigure(0, weight=1)

    def load_image(self):
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, path):
        img = cv2.imread(path)
        if img is None:
            return

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        target_width = min(gray.shape[1], self.max_width)
        new_height = int(
            gray.shape[0] * (target_width / gray.shape[1]) * self.font_ratio
        )

        resized = cv2.resize(
            gray, (target_width, new_height), interpolation=cv2.INTER_AREA
        )
        normalized = resized / 255
        self.ascii_art = self.convert_to_ascii(normalized)

        self.show_original_image(img)
        self.show_ascii_art()

    def convert_to_ascii(self, normalized_img):
        return "\n".join(
            "".join(
                self.gradient[
                    min(int(p * (len(self.gradient) - 1)), len(self.gradient) - 1)
                ]
                for p in row
            )
            for row in normalized_img
        )

    def show_original_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img)
        img_pil.thumbnail((400, 400), Image.Resampling.LANCZOS)

        ctk_image = ctk.CTkImage(
            light_image=img_pil, dark_image=img_pil, size=img_pil.size
        )

        self.original_label.configure(image=ctk_image)
        self.original_label.image = ctk_image

    def show_ascii_art(self):
        self.ascii_text.delete("1.0", "end")
        self.ascii_text.insert("1.0", self.ascii_art)
        self.ascii_text.see("1.0")

    def save_ascii_image(self):
        if not self.ascii_art:
            return

        file_path = ctk.filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            return

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            lines = self.ascii_art.split("\n")
            max_line_length = max(len(line) for line in lines)

            # Исправление для новых версий Pillow
            bbox = self.font.getbbox("W")
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]

            img_width = max(max_line_length * char_width, 1)
            img_height = max(len(lines) * char_height, 1)

            image = Image.new("RGB", (img_width, img_height), color="black")
            draw = ImageDraw.Draw(image)

            y = 0
            for line in lines:
                draw.text((0, y), line, font=self.font, fill="white")
                y += char_height

            image.save(file_path)
            # Исправление для сообщения
            messagebox.showinfo("Сохранение", f"Файл успешно сохранен:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = ASCIIArtConverter(root)
    root.mainloop()
"""

from gui.main_window import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
