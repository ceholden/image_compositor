# -*- coding: utf-8 -*
import pkgutil


# Helper function
def recursive_find_subclass(subclass, found=None):
    """ Search subclass for descendents """
    if not found:
        found = []

    sub_subclasses = subclass.__subclasses__()

    for sub_subclass in sub_subclasses:
        if sub_subclass not in found:
            found.append(sub_subclass)
        recursive_find_subclass(sub_subclass, found)

    return found

# Load all modules in this directory
from composite_algorithm import Compositor

for loader, modname, ispkg in pkgutil.iter_modules(__path__):
    loaded_mod = __import__(__name__ + '.' + modname, fromlist=[modname])

# Get subclasses
algorithms = Compositor.__subclasses__()
for algo in algorithms:
    algorithms = recursive_find_subclass(algo, found=algorithms)

__all__ = ['algorithms']
