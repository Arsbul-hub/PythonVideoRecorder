import sys

from PyQt5 import QtCore

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from Recosiner import VideoManager

from design import Ui_MainWindow
from UserData import User
from datetime import datetime

import pyaudio


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.user_data_manager = User()
        self.video_manager = VideoManager()
        self.out_folder.setText(f"Папка хранения видео: {self.user_data_manager.get_data('out_directory')}")
        self.video_manager.add_task(self.update_frame)

        self.start_writing.clicked.connect(self.write_video)
        self.stop_writing.clicked.connect(self.stop_video)
        self.choose_out_folder.clicked.connect(self.set_out_folder)

        self.recording_state.hide()

        # self.microphones = []
        self.inputs = {}
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            self.inputs[p.get_device_info_by_index(i)['name']] = i
            self.microphones.addItem(p.get_device_info_by_index(i)['name'])
        if self.user_data_manager.get_data("audio_input"):
            self.microphones.setCurrentIndex(self.user_data_manager.get_data("audio_input"))
        self.microphones.currentIndexChanged.connect(self.on_change_microphone)

    def on_change_microphone(self):
        self.video_manager.set_audio_input(self.microphones.currentIndex())
        self.user_data_manager.update_data("audio_input", self.microphones.currentIndex())

    def write_video(self):
        saving_filename = self.user_data_manager.get_data(
            "out_directory") + f"/Видео{datetime.now().time().strftime('%H-%M-%S')}"
        self.video_manager.write(saving_filename)
        self.recording_state.show()

    def stop_video(self):

        self.video_manager.stop()

        self.recording_state.hide()

    def set_out_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Место хранения видео", "")
        if directory:
            self.out_folder.setText(f"Папка хранения видео: {directory}")
            self.user_data_manager.update_data("out_directory", directory)

    def update_frame(self):
        # print(self.video_manager.recorder.current_frame)

        pixmap = self.video_manager.frame_to_pixmap(self.video_manager.get_frame())
        pixmap = pixmap.scaled(self.video_view.width(), self.video_view.height(), QtCore.Qt.KeepAspectRatio)
        self.video_view.setPixmap(pixmap)

        self.current_fps.setText(f"FPS: {self.video_manager.fps}")

    def closeEvent(self, event):
        self.video_manager.stop_all_loops()
        # self.connection.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
