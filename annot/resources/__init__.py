import os
from typing import Dict
from glob import glob

from PySide6.QtGui import QImage

"""Icons from Google material icon pack https://fonts.google.com/icons"""


def _get_icons() -> Dict[str, QImage]:
    rv = {}
    for fn in glob(os.path.dirname(__file__) + os.sep + '*.png'):
        icon = QImage(fn)
        name, _ = os.path.splitext(os.path.basename(fn))
        rv[name] = icon
    return rv


ICONS = _get_icons()
