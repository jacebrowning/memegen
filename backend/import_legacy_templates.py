from contextlib import suppress
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


def run():
    for count, legacy in enumerate(LegacyTemplate.objects.all(), start=1):
        if not legacy.key.startswith("_"):
            log.info(f"Importing template {count}: {legacy.key}")
            template = Template(legacy.key)
            template.name = legacy.name
            template.source = legacy.link
            template.sample = legacy.default
            template.datafile.save()


if __name__ == "__main__":
    log.silence("datafiles")
    run()
