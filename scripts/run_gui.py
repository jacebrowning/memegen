#!env/bin/python

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

        # Configure speech recognition
        if speech_recognition:
            self._recogizer = speech_recognition.Recognizer()
            self._recogizer.energy_threshold = 1500
            self._recogizer.dynamic_energy_adjustment_ratio = 3
            self._microphone = speech_recognition.Microphone()
            with self._microphone as source:
                log.info("Adjusting for ambient noise...")
                self._recogizer.adjust_for_ambient_noise(source, duration=3)
            log.info("Listening for audio...")
            self._recogizer.listen_in_background(self._microphone, self.listen)

        # Configure root window
        self.root = tk.Tk()
        self.root.title("{} (v{})".format(__project__, __version__))
        self.root.minsize(500, 500)

        # Initialize the GUI
        self.label = None
        frame = self.init(self.root)
        frame.pack(fill=tk.BOTH, expand=1)

        # Start the event loop
        self.restart()
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

    def listen(self, recognizer, audio):
        log.info("Recognizing speech...")
        try:
            value = recognizer.recognize_google(audio)
        except speech_recognition.UnknownValueError:
            log.warning("No speech detected")
        else:
            log.info("Detected speech: %s", value)
            self.update(value)
        log.info("Listening for audio...")

    def update(self, value=None):
        text = Text(value or self.text.get())

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


if __name__ == '__main__':
    Application(create_app(ProdConfig))
