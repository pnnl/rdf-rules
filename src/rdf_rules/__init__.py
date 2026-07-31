from beartype.claw import beartype_this_package
beartype_this_package()
# conflicts with plum dispatch:?
del beartype_this_package
from .rule import make
