import shutil
from pathlib import Path
from typing import List

import log
from datafiles import datafile

from backend.models import Template


@datafile("../templates-legacy/{self.key}/config.yml")
class LegacyTemplate:
    key: str
    name: str
    link: str
    default: List[str]
    aliases: List[str]

    def copy_images(self, destination: Path):
        for source in self.datafile.path.parent.iterdir():
            if source.suffix in {".jpg", ".png"}:
                shutil.copy(source, destination)


def run():
    log.silence("datafiles", allow_warning=True)

    for count, legacy in enumerate(LegacyTemplate.objects.all(), start=1):

        if legacy.key.startswith("_"):
            continue

        log.info(f"Importing template {count}: {legacy.key}")

        template = Template(legacy.key)
        template.name = legacy.name
        template.source = legacy.link
        template.sample = legacy.default or ["YOUR TEXT", "GOES HERE"]

        legacy.copy_images(template.datafile.path.parent)


if __name__ == "__main__":
    run()
