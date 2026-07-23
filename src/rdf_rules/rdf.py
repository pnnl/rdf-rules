from beartype.vale import Is
from typing import Annotated

from uritools import isuri
URI = Annotated[str, Is[isuri]]
