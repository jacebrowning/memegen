class ImageStore:

    def read(self, path):
        # TODO: read images from 'data'
        print(path)
        return None

    def create(self, image):
        image.from_template(image.template, image.text)
        image.path = "../temp.jpg"
