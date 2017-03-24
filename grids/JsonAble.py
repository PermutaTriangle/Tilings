import json


__all__ = ["JsonAble"]


class JsonAble(object):
    def __init__(self, attr_dict={}, **kwargs):
        """Initialize the dictionary of the object."""
        self.__dict__.update(attr_dict)
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls, json_string):
        """Get a JSON-able object back from JSON string.

        This base implementation uses helper methods to read the attr dict from
        the JSON string and then creating an object to return from the attr
        dict. This implementation should not be overridden; rather, one should
        override the helper methods.
        """
        attr_dict = cls._attr_dict_from_json(json_string)
        obj = cls._from_attr_dict(attr_dict)
        return obj

    @staticmethod
    def _attr_dict_from_json(json_string):
        """Read the attr dict from a JSON string.

        This base implementation just loads the JSON string.
        One should probably not override this method.
        """
        return json.loads(json_string)

    # OVERRIDE THIS ONE
    @classmethod
    def _from_attr_dict(cls, attr_dict):
        """Get a JSON-able object back from attribute dictionary.

        This base implementation takes the attr dict and uses it as the sole
        argument to the class' constructor.
        This is something to override because you need to process the attr dict.
        """
        return cls(attr_dict)

    def to_json(self, *args, **kwargs):
        """Get a JSON string representing the JSON-able object.

        One should probably not override this method."""
        return json.dumps(self._get_attr_dict(), *args, **kwargs)

    # OVERRIDE THIS ONE
    def _get_attr_dict(self):
        """to_json method helper that collects attributes to be dumped.

        This base implementation takes all the items of the __dict__
        of the object and: calls _get_attr_dict on the value if it is a
        JsonAble, otherwise it uses the unmodified value.
        This method should be overridden.
        """
        return {attr_name: value._get_attr_dict() \
                if isinstance(value, JsonAble) \
                else value
                for attr_name, value in self.__dict__.items()}
