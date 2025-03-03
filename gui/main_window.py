import customtkinter as ctk
import tkinter.messagebox as messagebox
from PIL import Image, ImageFont
from pathlib import Path
import cv2
import threading

from core.image_processor import ImageProcessor
from core.video_processor import VideoProcessor
from utils.file_handler import save_ascii_to_image
from utils.ascii_art import ASCIIArtConverter

# Исправленные настройки темы
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ASCII Art Converter")
        self.geometry("1280x720")
        self.minsize(800, 500)
        self._setup_variables()
        self._create_widgets()
        self._bind_events()

    def _setup_variables(self):
        try:
            self.font = ImageFont.truetype("../assets/fonts/DejaVuSansMono.ttf", 10)
        except:
            self.font = ImageFont.load_default()

        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.ascii_converter = ASCIIArtConverter()
        self.current_ascii = ""
        self.video_thread = None

    def _create_widgets(self):
        self._create_main_frames()
        self._create_image_section()
        self._create_video_section()
        self._create_controls()

    def _create_main_frames(self):
        # Настройка сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Основной контейнер
        self.main_container = ctk.CTkTabview(self)
        self.main_container.grid(row=0, column=0, sticky="nsew")

        # Создаем вкладки
        self.image_tab = self.main_container.add("Изображение")
        self.video_tab = self.main_container.add("Видео")

        # toolbar = ctk.CTkFrame(self, height=40)
        # toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # self.load_btn = ctk.CTkButton(
        #    toolbar, text="Загрузить изображение", command=self.load_image
        # )
        # self.load_btn.pack(side="left", padx=1, pady=1)

    def _create_image_section(self):
        self.image_frame = ctk.CTkFrame(self.image_tab)
        self.image_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.original_image = ctk.CTkLabel(self.image_frame, text="")
        self.original_image.pack(side="left", expand=True, fill="both")

        self.ascii_text = ctk.CTkTextbox(
            self.image_frame,
            wrap="none",
            font=("Courier", 8),
            fg_color="black",
            text_color="white",
        )
        self.ascii_text.pack(side="right", expand=True, fill="both")

        self.btn_load_image = ctk.CTkButton(
            self.image_frame, text="Загрузить изображение", command=self.load_image
        )
        self.btn_load_image.pack(pady=5)

    def _create_video_section(self):
        # Контейнер видео
        self.video_container = ctk.CTkFrame(self.video_tab)
        self.video_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Превью видео
        self.video_preview = ctk.CTkTextbox(
            self.video_container,
            wrap="none",
            font=("Courier", 6),
            fg_color="black",
            text_color="white",
            height=400,
        )
        self.video_preview.pack(expand=True, fill="both")

        # Элементы управления видео
        self.video_controls = ctk.CTkFrame(self.video_container)
        self.video_controls.pack(pady=10)

        self.btn_load_video = ctk.CTkButton(
            self.video_controls, text="Загрузить видео", command=self.load_video
        )
        self.btn_load_video.pack(side="left", padx=5)

        self.btn_play = ctk.CTkButton(
            self.video_controls, text="Старт", command=self.toggle_video_playback
        )
        self.btn_play.pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(
            self.video_controls, text="Стоп", command=self.stop_video, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)

    def _create_controls(self):
        # Панель управления
        self.control_panel = ctk.CTkFrame(self)
        self.control_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.btn_save = ctk.CTkButton(
            self.control_panel, text="Сохранить ASCII", command=self.save_ascii
        )
        self.btn_save.pack(side="right", padx=5)

    def _bind_events(self):
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_image(self):
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.process_image(file_path)

    def process_image(self, path):
        processed = self.image_processor.process(path)
        if processed is not None:
            self.current_ascii = self.ascii_converter.convert_frame(processed)
            self.show_preview(path)
            self.ascii_text.delete("1.0", "end")
            self.ascii_text.insert("1.0", self.current_ascii)

    def show_preview(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.thumbnail((400, 400))

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.original_image.configure(image=ctk_img)
        self.original_image.image = ctk_img

    def load_video(self):
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi")]
        )
        if file_path:
            self.video_processor.video_path = file_path
            self.btn_play.configure(state="normal")

    def toggle_video_playback(self):
        if not self.video_processor.running:
            self.start_video_processing()
            self.btn_play.configure(text="Пауза")
            self.btn_stop.configure(state="normal")
        else:
            self.video_processor.running = False
            self.btn_play.configure(text="Старт")

    def start_video_processing(self):
        self.video_processor.running = True
        self.video_thread = threading.Thread(target=self._process_video_frames)
        self.video_thread.start()

    def _process_video_frames(self):
        while self.video_processor.running:
            frame = self.video_processor.get_next_frame()
            if frame is not None:
                ascii_frame = self.ascii_converter.convert_frame(frame)
                self.video_preview.delete("1.0", "end")
                self.video_preview.insert("1.0", ascii_frame)

    def stop_video(self):
        self.video_processor.stop_processing()
        self.btn_play.configure(text="Старт", state="normal")
        self.btn_stop.configure(state="disabled")

    def save_ascii(self):
        if self.current_ascii:
            file_path = ctk.filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            if file_path:
                with open(file_path, "w") as f:
                    f.write(self.current_ascii)
                messagebox.showinfo("Сохранено", "Файл успешно сохранен!")

    def on_close(self):
        if self.video_processor.running:
            self.video_processor.stop_processing()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
