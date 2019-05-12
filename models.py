from datafiles import datafile


@datafile("templates/{self.key}/config.yml", manual=True)
class Template:

    key: str
