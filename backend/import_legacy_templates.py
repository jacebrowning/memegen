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
    for lt in LegacyTemplate.objects.all():
        print(lt.key)


if __name__ == "__main__":
    log.silence("datafiles")
    run()
