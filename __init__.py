from typing import Optional

from pyrogram.client import Client
from loads import Description, MainDescription, FuncDescription

__description__ = Description(
    MainDescription("Плагин для гриндилки ресурсов у ботов."),
    FuncDescription('irisfarma'),
    FuncDescription('skpromo'),
    FuncDescription('bfgpromo')
)

import plugins.GrindBots.main