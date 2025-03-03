import cv2
import numpy as np
import threading
from queue import Queue


class VideoProcessor:
    def __init__(self, max_width=120, font_ratio=0.5):
        self.max_width = max_width
        self.font_ratio = font_ratio
        self.frame_queue = Queue(maxsize=30)
        self.running = False

    def process_video(self, video_path):
        self.running = True
        vid = cv2.VideoCapture(video_path)

        while self.running and vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            resized = self._resize_frame(gray)
            self.frame_queue.put(resized / 255)

        vid.release()
        self.running = False

    def _resize_frame(self, frame):
        target_width = min(frame.shape[1], self.max_width)
        new_height = int(
            frame.shape[0] * (target_width / frame.shape[1]) * self.font_ratio
        )
        return cv2.resize(
            frame, (target_width, new_height), interpolation=cv2.INTER_AREA
        )

    def stop_processing(self):
        self.running = False
        while not self.frame_queue.empty():
            self.frame_queue.get()
