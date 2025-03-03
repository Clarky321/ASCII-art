import cv2
import numpy as np


class ImageProcessor:
    def __init__(self, max_width=200, font_ratio=0.55):
        self.max_width = max_width
        self.font_ratio = font_ratio

    def process(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        target_width = min(gray.shape[1], self.max_width)
        new_height = int(
            gray.shape[0] * (target_width / gray.shape[1]) * self.font_ratio
        )

        resized = cv2.resize(
            gray, (target_width, new_height), interpolation=cv2.INTER_AREA
        )
        return resized / 255
