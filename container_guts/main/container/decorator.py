__author__ = "Vanessa Sochat"
__copyright__ = "Copyright The ORAS Authors."
__license__ = "Apache-2.0"

from functools import partial, update_wrapper


class ensure_container:
    """
    Ensure the first argument is a container, and the name
    is fully formatted into a ContainerName object (for further parsing)
    """

    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)

    def __call__(self, cls, *args, **kwargs):
        if "image" in kwargs:
            kwargs["image"] = cls.get_container(kwargs["image"])
        elif args:
            container = cls.get_container(args[0])
            args = (container, *args[1:])
        return self.func(cls, *args, **kwargs)
