from contextlib import suppress
from typing import List

import log
from datafiles import datafile


@datafile("../templates-legacy/{self.key}/config.yml")
class LegacyTemplate:
    key: str
    name: str
    link: str
    default: List[str]
    aliases: List[str]


def run():
    for count, template in enumerate(LegacyTemplate.objects.all(), start=1):
        print(f"{count}: {template.key}")


if __name__ == "__main__":
    log.silence("datafiles")
    run()
