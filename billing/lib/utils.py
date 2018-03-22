from importlib import import_module


def clsfstr(module, name):
    """
    Make class instance from string
    """
    return getattr(import_module(module), name)
