from PIL import Image, ImageDraw
import tkinter.messagebox as messagebox
from pathlib import Path


def save_ascii_to_image(ascii_art, font, file_path):
    try:
        lines = ascii_art.split("\n")
        max_line_length = max(len(line) for line in lines)

        bbox = font.getbbox("W")
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]

        img_width = max(max_line_length * char_width, 1)
        img_height = max(len(lines) * char_height, 1)

        image = Image.new("RGB", (img_width, img_height), color="black")
        draw = ImageDraw.Draw(image)

        y = 0
        for line in lines:
            draw.text((0, y), line, font=font, fill="white")
            y += char_height

        image.save(file_path)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")
        return False
