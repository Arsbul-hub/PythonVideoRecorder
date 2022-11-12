import time
from threading import Thread
import cv2
import numpy as np

from PyQt5.QtGui import QPixmap, QImage

import ctypes
from PIL import ImageGrab, Image
import wave
import pyaudio

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

user32 = ctypes.windll.user32


class AudioWriter:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 5
        self.WAVE_OUTPUT_FILENAME = "output.wav"
        self.microphone_id = 0
        self.writing = False
        self.frames = []
        self.pyaudio_obj = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_obj.open(format=self.FORMAT,
                                                  channels=self.CHANNELS,
                                                  rate=self.RATE,
                                                  input=True,
                                                  input_device_index=self.microphone_id,
                                                  frames_per_buffer=self.CHUNK)

    def frame_sender(self):
        if self.writing:
            # t0 = time.perf_counter()
            data = self.audio_stream.read(self.CHUNK)
            self.frames.append(data)

            # t1 = time.perf_counter()

    def start_writing(self):
        self.frames.clear()
        self.writing = True

    def stop_writing(self):
        self.writing = False
        self.save_audio()

    def save_audio(self):
        with wave.open("temp_audio.mp3", 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.pyaudio_obj.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))


class Recording:
    def __init__(self):
        self.write = False
        win_size = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
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
        self.filename = ""

    def frame_sender(self):

        self.get_screenshot()

        if self.write and self.video_writer:
            self.video_writer.write(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))

    def get_fps(self):
        return self.fps, self.fps_list

    def get_screenshot(self):
        try:

            image = ImageGrab.grab()
            self.current_frame = np.array(image)

        except:
            print("Error")

    def write_video(self, fps_clip, filename):

        self.video_writer = cv2.VideoWriter(f"{filename}.mp4", self.video_codec, fps_clip, self.resolution)

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


class VideoManager:
    def __init__(self):
        self.audio = AudioWriter()
        self.recorder = Recording()
        self.filename = ""
        self.tasks = []
        self.fps = 0
        self.fps_list = []
        self.fps_clipper = 60
        self.do_loop = True
        Thread(target=self.main_loop).start()
        # Thread(target=self.video_loop).start()
        # Thread(target=self.audio_loop).start()

    def get_fps(self):
        return self.recorder.fps

    def set_audio_input(self, index):
        self.audio.microphone_id = index

    def add_task(self, task):
        self.tasks.append(task)

    def audio_loop(self):

        while self.do_loop:
            self.audio.frame_sender()

    def main_loop(self):
        try:  # Рекурсия нужна для увеличения fps
            # while self.do_loop:
            t0 = time.perf_counter()

            self.recorder.frame_sender()
            t1 = time.perf_counter()

            if self.tasks:
                for task in self.tasks:
                    task()
            self.fps = 1 // float(t1 - t0)

            self.fps_list.append(self.fps)
        except:
            pass
        if self.do_loop:
            Thread(target=self.main_loop).start()

    def write(self, filename):
        self.fps_clipper = int(sum(self.fps_list) / len(self.fps_list))
        self.recorder.write_video(self.fps_clipper, filename)
        # self.audio.start_writing()

    def stop(self):

        # self.audio.stop_writing()

        self.recorder.stop_video()
        # on_start()
        # Thread(target=lambda: self.save_output(filename, on_stop)).start()

    def get_frame(self):
        return self.recorder.current_frame

    # def save_output(self, filename, on_stop):
    #     videoclip = VideoFileClip("temp_video.mp4")
    #     audioclip = AudioFileClip("temp_audio.mp3")
    #
    #     new_audioclip = CompositeAudioClip([audioclip])
    #     videoclip.audio = new_audioclip
    #
    #     videoclip.write_videofile(filename + ".mp4")
    #     on_stop()

    def frame_to_pixmap(self, bgr_frame):
        try:
            height, width, channel = bgr_frame.shape
            bytesPerLine = 3 * width
            pixmap = QPixmap(QImage(bgr_frame.data, width, height, bytesPerLine, QImage.Format_RGB888))
            return pixmap
        except:
            return QPixmap()

    def stop_all_loops(self):
        self.do_loop = False
