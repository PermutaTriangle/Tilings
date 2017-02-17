import json


__all__ = ["JsonAble"]


class JsonAble(object):
    @classmethod
    def from_json(cls, json_string):
        """Get a JSON-able object back from JSON string."""
        attr_dict = json.loads(json_string)
        return cls._from_attr_dict(attr_dict)

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        """Get a JSON-able object back from attribute dictionary."""
        return cls(**cls._prepare_attr_dict(attr_dict))

    @classmethod
    def _prepare_attr_dict(cls, attr_dict):
        return attr_dict

    def to_json(self, **kwargs):
        """Get a JSON string representing the JSON-able object."""
        return json.dumps(self._to_json(), **kwargs)

    def _to_json(self):
        """to_json method helper that collects attributes to be dumped."""
        #attr_dict = {}
        #for attr_name, value in self.__dict__.items():
        #    if isinstance(value, JsonAble):
        #        attr_dict[attr_name] = value.to_json(**kwargs)
        #    else:
        #        attr_dict[attr_name] = value
        #return attr_dict
        return {attr_name: value._to_json() \
                if isinstance(value, JsonAble) \
                else value
                for attr_name, value in self.__dict__.items()}
