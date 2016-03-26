#!env/bin/python

import queue
import threading
import logging

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
try:
    import speech_recognition  # pylint: disable=import-error
except ImportError:
    speech_recognition = None

from memegen import __project__, __version__
from memegen.settings import ProdConfig
from memegen.app import create_app
from memegen.domain import Text

log = logging.getLogger(__name__)


class Application:

    def __init__(self, app):
        self.app = app
        self.label = None
        self.text = None
        self._image = None
        self._update_event = None
        self._clear_event = None

        # Configure root window
        self.root = tk.Tk()
        self.root.title("{} (v{})".format(__project__, __version__))
        self.root.minsize(500, 500)

        # Configure speech recognition
        self._queue = queue.Queue()
        self._event = threading.Event()
        self._speech_recognizer = SpeechRecognizer(self._queue, self._event)
        self._speech_recognizer.start()
        self.process_speech()

        # Initialize the GUI
        self.label = None
        frame = self.init(self.root)
        frame.pack(fill=tk.BOTH, expand=1)

        # Start the event loop
        self.restart()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    def init(self, root):
        padded = {'padding': 5}
        sticky = {'sticky': tk.NSEW}

        # Configure grid
        frame = ttk.Frame(root, **padded)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)
        frame.columnconfigure(0, weight=1)

        def frame_image(root):
            frame = ttk.Frame(root, **padded)

            # Configure grid
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)

            # Place widgets
            self.label = ttk.Label(frame)
            self.label.grid(row=0, column=0)

            return frame

        def frame_text(root):
            frame = ttk.Frame(root, **padded)

            # Configure grid
            frame.rowconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
            frame.columnconfigure(0, weight=1)

            # Place widgets
            self.text = ttk.Entry(frame)
            self.text.bind("<Key>", self.restart)
            self.text.grid(row=0, column=0, **sticky)
            self.text.focus_set()

            return frame

        def separator(root):
            return ttk.Separator(root)

        # Place widgets
        frame_image(frame).grid(row=0, **sticky)
        separator(frame).grid(row=1, padx=10, pady=5, **sticky)
        frame_text(frame).grid(row=2, **sticky)

        return frame

    def process_speech(self):
        try:
            speech = self._queue.get(0)
        except queue.Empty:
            pass
        else:
            self.update(speech)
        finally:
            self.root.after(10, self.process_speech)

    def update(self, value=None):
        if value:
            self.clear()
            self.text.insert(0, value)

        text = Text(self.text.get())
        ratio = 0
        match = None

        for template in self.app.template_service.all():
            _ratio, path = template.match(str(text).lower())
            if _ratio > ratio:
                ratio = _ratio
                log.info("Matched at %s: %s - %s", ratio, template, path)
                match = template, Text(path)

        if match:
            domain = self.app.image_service.create(*match)
            image = Image.open(domain.path)
            old_size = image.size
            max_size = self.root.winfo_width(), self.root.winfo_height()
            ratio = min(max_size[0] / old_size[0], max_size[1] / old_size[1])
            new_size = [int(s * ratio * 0.9) for s in old_size]
            image = image.resize(new_size, Image.ANTIALIAS)
            self._image = ImageTk.PhotoImage(image)
            self.label.configure(image=self._image)

            self.clear()

        self.restart(update=True, clear=False)

    def clear(self, *_):
        self.text.delete(0, tk.END)
        self.restart()

    def restart(self, *_, update=True, clear=True):
        if update:
            if self._update_event:
                self.root.after_cancel(self._update_event)
            self._update_event = self.root.after(1000, self.update)
        if clear:
            if self._clear_event:
                self.root.after_cancel(self._clear_event)
            self._clear_event = self.root.after(5000, self.clear)

    def close(self):
        log.info("Closing the application...")
        self._event.set()
        self._speech_recognizer.join()
        self.root.destroy()


class SpeechRecognizer(threading.Thread):

    def __init__(self, queue, event):  # pylint: disable=redefined-outer-name
        super().__init__()
        self.queue = queue
        self.event = event
        self.microphone = None
        self.recognizer = None

    def run(self):
        if not speech_recognition:
            return
        self.configure()
        while not self.event.is_set():
            audio = self.listen()
            if audio:
                result = self.recognize(audio)
                if result:
                    self.queue.put(result)

    def configure(self):
        self.recognizer = speech_recognition.Recognizer()
        self.recognizer.energy_threshold = 1500
        self.recognizer.dynamic_energy_adjustment_ratio = 3
        self.microphone = speech_recognition.Microphone()
        with self.microphone as source:
            log.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
            log.info("Engery threshold: %s", self.recognizer.energy_threshold)

    def listen(self):
        log.info("Listening for audio...")
        audio = None
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(source, timeout=0.5)
            except speech_recognition.WaitTimeoutError:
                log.debug("No audio detected")
            else:
                log.debug("Audio detected: %s", audio)
        return audio

    def recognize(self, audio):
        log.info("Recognizing speech...")
        speech = None
        try:
            speech = self.recognizer.recognize_google(audio)
        except speech_recognition.UnknownValueError:
            log.warning("No speech detected")
        else:
            log.debug("Detected speech: %s", speech)
        return speech


if __name__ == '__main__':
    api = create_app(ProdConfig)
    with api.app_context():
        Application(api)
