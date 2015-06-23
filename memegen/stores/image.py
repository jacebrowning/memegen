import os


class ImageStore:

    def __init__(self, root):
        self.root = root

    def exists(self, image):
        image.root = self.root
        return os.path.isfile(image.path)

    def create(self, image):
        image.root = self.root
        image.generate()
