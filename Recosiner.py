import time
from threading import Thread
import cv2
import numpy as np
import pyautogui
from PyQt5.QtGui import QPixmap, QImage

import ctypes
from PIL import ImageGrab, Image
import wave
import pyaudio
import moviepy.editor as mpe

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
        Thread(target=self.audio_loop).start()

    def audio_loop(self):

        while True:
            if self.writing:
                data = self.audio_stream.read(self.CHUNK)
                self.frames.append(data)

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

        Thread(target=self.frame_sender).start()

    def frame_sender(self):
        while True:

            t0 = time.perf_counter()

            self.get_screenshot()

            # print(1 / float(tr2 - tr1))
            if self.write and self.video_writer:
                self.video_writer.write(cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB))

            t1 = time.perf_counter()

            self.fps = 1 / float(t1 - t0)

            self.fps_list.append(self.fps)

    def get_fps(self):
        return self.fps, self.fps_list

    def get_screenshot(self):
        try:

            image = ImageGrab.grab()

            self.current_frame = np.array(image)

        except:
            print("Error")

    def write_video(self):
        print(  sum(self.fps_list) / len(self.fps_list))
        self.fps_clipper = sum(self.fps_list) / len(self.fps_list)
        self.video_writer = cv2.VideoWriter("temp_video.mp4", self.video_codec,
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


class VideoManager:
    def __init__(self):
        self.audio = AudioWriter()
        self.recorder = Recording()
        self.filename = ""
        self.tasks = []
        Thread(target=self.loop).start()

    def fps(self):
        return self.recorder.fps

    def add_task(self, task):
        self.tasks.append(task)

    def loop(self):
        while True:
            #print(self.tasks)
            if self.tasks:
                for i in self.tasks:

                    Thread(target=i).start()

    def write(self):
        self.recorder.write_video()
        self.audio.start_writing()

    def stop(self, filename):
        self.audio.stop_writing()

        self.recorder.stop_video()
        print(123)
        Thread(target=lambda: self.save_output(filename)).start()
    def get_frame(self):
        return self.recorder.current_frame
    def save_output(self, filename):
        videoclip = mpe.VideoFileClip("temp_video.mp4")
        audioclip = mpe.AudioFileClip("temp_audio.mp3")

        new_audioclip = mpe.CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(filename + ".mp4")

    def frame_to_pixmap(self, bgr_frame):

        height, width, channel = bgr_frame.shape
        bytesPerLine = 3 * width
        pixmap = QPixmap(QImage(bgr_frame.data, width, height, bytesPerLine, QImage.Format_RGB888))
        return pixmap
