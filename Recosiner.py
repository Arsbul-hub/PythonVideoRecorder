import time
from threading import Thread
import cv2
import numpy as np
from PyQt5.QtGui import QPixmap, QImage

import ctypes
from PIL import ImageGrab, Image
import pickle

from PyQt5.QtWidgets import QFileDialog

user32 = ctypes.windll.user32


class Recording:
    def __init__(self, data_manager):
        self.write = False
        win_size = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.user_data_manager = data_manager
        self.resolution = win_size
        self.mss_properties = {"top": 0, "left": 0, "width": 400, "height": 400}
        self.video_codec = cv2.VideoWriter_fourcc(*"XVID")
        self.fps_list = []
        self.fps = 0
        self.image = None
        self.video_writer = None
        self.current_frame = None
        self.fps_clipper = 30
        self.tasks = []

        Thread(target=self.frame_sender).start()

    def add_task(self, task):
        self.tasks.append(task)

    def frame_sender(self):
        while True:
            t0 = time.perf_counter()

            self.get_screenshot()

            if self.write and self.video_writer:
                self.video_writer.write(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))

            if self.tasks:
                for i in self.tasks:
                    Thread(target=i).start()
            t1 = time.perf_counter()

            self.fps = 1 / float(t1 - t0)
            self.fps_list.append(self.fps)

    def get_screenshot(self):
        try:

            image = ImageGrab.grab()

            self.current_frame = np.array(image)

        except:
            print("Error")

    def write_video(self, filename):
        print(sum(self.fps_list) / len(self.fps_list))
        self.fps_clipper = sum(self.fps_list) / len(self.fps_list)
        self.video_writer = cv2.VideoWriter(filename + ".mp4", self.video_codec,
                                            sum(self.fps_list) / len(self.fps_list), self.resolution)

        self.write = True

    def stop_video(self):
        self.write = False
        self.video_writer.release()
        self.fps_clipper = 30

    def test(self, frame):
        im = Image.new("RGB", frame.size)
        pixels = zip(frame.raw[2::4], frame.raw[1::4], frame.raw[::4])

        im.putdata(list(pixels))
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGB")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        return QPixmap.fromImage(qim)

    def frame_to_pixmap(self, bgr_frame):
        height, width, channel = bgr_frame.shape
        bytesPerLine = 3 * width
        pixmap = QPixmap(QImage(bgr_frame.data, width, height, bytesPerLine, QImage.Format_RGB888))
        return pixmap
