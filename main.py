import sys
import time
from pprint import pprint

import cv2
import numpy as np
import pyautogui
from PyQt5 import Qt, QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from Recosiner import Recording

from design import Ui_MainWindow
from UserData import User
from datetime import datetime


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.user_data_manager = User()
        self.recorder = Recording(self.user_data_manager)
        self.out_folder.setText(f"Папка хранения видео: {self.user_data_manager.get_data('out_directory')}")
        self.recorder.add_task(self.update_frame)

        self.start_writing.clicked.connect(self.write_video)
        self.stop_writing.clicked.connect(self.stop_video)
        self.choose_out_folder.clicked.connect(self.set_out_folder)

        self.recording_icon.setMovie(QMovie("recoding_icon.gif"))
        dd = QtCore.QSize()
        dd = dd.scaled(self.recording_icon.width(), self.recording_icon.height(), QtCore.Qt.KeepAspectRatio)
        self.recording_icon.movie().setScaledSize(dd)
        self.recording_icon.hide()
        self.recording_icon.movie().start()

    def write_video(self):
        saving_filename = self.user_data_manager.get_data(
            "out_directory") + f"/Видео{datetime.now().time().strftime('%H-%M-%S')}"
        self.recorder.write_video(saving_filename)
        self.recording_icon.show()

    def stop_video(self):
        self.recorder.stop_video()

        self.recording_icon.hide()

    def set_out_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Место хранения видео", "")
        if directory:
            self.out_folder.setText(f"Папка хранения видео: {directory}")
            self.user_data_manager.update_data("out_directory", directory)

    def update_frame(self):
        pixmap = self.recorder.frame_to_pixmap(self.recorder.current_frame)
        pixmap = pixmap.scaled(self.video_view.width(), self.video_view.height(), QtCore.Qt.KeepAspectRatio)
        self.video_view.setPixmap(pixmap)

        self.current_fps.setText(str(self.recorder.fps))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
