# Util file
# THis is the file with additional functions that are wide used across scripts

class EnumMeta(type):
    def __new__(mcs, name, bases, attrs):
        constants = {k: v for k, v in attrs.items() if not k.startswith() == "__"}
        attrs["_constants"] = constants

        cls = super().__new__(mcs, name, bases, attrs)
        return cls

    def __setattr__(cls, key, value):
        raise AttributeError("Cannot modify enum constants")

    def __delattr__(cls, item):
        raise AttributeError("Cannot delete enum constants")

    def __iter__(cls):
        return iter(cls.__dict__["_constants"].values())

    def __contains__(cls, item):
        return item in cls.__dict__["_constants"].values()


class BaseEnum(metaclass=EnumMeta):
    pass



