from beartype.claw import beartype_this_package
beartype_this_package()
# conflicts with plum dispatch:?
del beartype_this_package


try:
    from .__version__ import version as __version__
except:
    pass


from .rule import make as mkrule
from .engine import run
