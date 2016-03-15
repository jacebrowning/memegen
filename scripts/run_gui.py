#!env/bin/python

import os
import sys
import logging

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(ROOT)

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
        self._event = None

        # Configure root window
        self.root = tk.Tk()
        self.root.title("{} (v{})".format(__project__, __version__))
        self.root.minsize(500, 500)

        # Initialize the GUI
        self.label = None
        frame = self.init(self.root)
        frame.pack(fill=tk.BOTH, expand=1)

        # Start the event loop
        self.update()
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

    def update(self):
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
            image = self.app.image_service.create(*match)
            self.image = ImageTk.PhotoImage(Image.open(image.path))
            self.label.configure(image=self.image)

        self.restart()

    def restart(self, *_):
        if self._event:
            self.root.after_cancel(self._event)
        self._event = self.root.after(1000, self.update)


if __name__ == '__main__':
    Application(create_app(ProdConfig))
