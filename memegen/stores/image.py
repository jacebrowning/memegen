import os
import logging

import sqlalchemy as sa

from ..extensions import db

log = logging.getLogger(__name__)


class MemeModel(db.Model):
    __tablename__ = 'memes'
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    key = sa.Column(sa.String, nullable=False)

    def __repr__(self):
        return "<Meme(id='%s', key='%s')>" % (self.id, self.key)

    def save(self):
        db.session.add(self)
        db.session.commit()


class WordModel(db.Model):
    __tablename__ = 'words'
    id = sa.Column(sa.String, primary_key=True, nullable=False)
    meme_id = sa.Column(sa.Integer, sa.ForeignKey('memes.id'), nullable=False)
    occurances = sa.Column(sa.Integer)

    def __repr__(self):
        return "<Word(id='%s', meme_id='%s', occurances='%s')>" \
            % (self.id, self.meme_id, self.occurances)


class ImageModel:
    def __init__(self, image):
        self._word_models = {}
        self._words = []
        self.key = image.template.key

        # append all the individual words into an array
        for line in image.text.lines:
            self._words += line.lower().split(' ')

        meme = db.session.query(MemeModel).filter_by(key=image.template.key).first()
        if not meme:
            meme = MemeModel(key=image.template.key)
            db.session.add(meme)
            db.session.commit()

        # look-up the word from the database, count the
        # occurances in this particular set of text
        for word in self._words:
            # is there no entry? should we query for one
            # or create a new one?
            if not self._word_models.get(word):
                model = (
                    db.session.query(WordModel)
                    .filter(WordModel.id == word)
                    .first()
                )

                # doesn't exist, create a new model
                if not model:
                    model = WordModel(id=word, meme_id=meme.id, occurances=0)

                model.occurances += 1
                self._word_models[word] = model

            else:
                self._word_models[word].occurances += 1

        # save all the updated occurance counts
        for key in self._word_models:
            if self._word_models[key]:
                db.session.add(self._word_models[key])
        db.session.commit()


class ImageStore:

    LATEST = "latest.jpg"

    def __init__(self, root, config):
        self.root = root
        self.debug = config.get('DEBUG', False)

    @property
    def latest(self):
        return os.path.join(self.root, self.LATEST)

    def exists(self, image):
        image.root = self.root
        # TODO: add a way to determine if the styled image was already generated
        return os.path.isfile(image.path) and not image.style

    def create(self, image):
        if self.exists(image) and not self.debug:
            return

        ImageModel(image)

        image.root = self.root
        image.generate()

        try:
            os.remove(self.latest)
        except IOError:
            pass
        os.symlink(image.path, self.latest)
