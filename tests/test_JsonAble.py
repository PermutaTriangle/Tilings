import pytest

from grids import JsonAble


#
# Simple tests
#


@pytest.fixture
def simple_json_able_object():
    """A really simple JsonAble object where all attributes act nice in JSON."""
    obj = JsonAble(foo="foo string", leet=1337, bar=["beer", "shots"])
    return obj


def test_simple_to_json(simple_json_able_object):
    """Test if we get a correct JSON string from a simple JSON object."""
    json_string = simple_json_able_object.to_json(indent="  ", sort_keys=True)
    assert json_string == """{
  "bar": [
    "beer",
    "shots"
  ],
  "foo": "foo string",
  "leet": 1337
}"""


def test_simple_back_from_json(simple_json_able_object):
    """Test if we get the same attributes back."""
    json_string = simple_json_able_object.to_json()
    obj_back_from_json = JsonAble.from_json(json_string)
    assert obj_back_from_json.bar == simple_json_able_object.bar
    assert obj_back_from_json.foo == simple_json_able_object.foo
    assert obj_back_from_json.leet == simple_json_able_object.leet


#
# Complex tests
#


class ComplexJsonAble(JsonAble):
    def __init__(self):
        super(ComplexJsonAble, self).__init__()
        self.hard_attribute = None
        self.json_able_attribute = None

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        # Get the set back as a set
        hard_attribute = set(attr_dict["hard_attribute"])
        # Decode the attribute as JsonAble
        json_able = JsonAble._from_attr_dict(attr_dict["json_able_attribute"])
        # Manually make the object
        obj = cls()
        obj.hard_attribute = hard_attribute
        obj.json_able_attribute = json_able
        return obj

    def _get_attr_dict(self):
        # Encode the set as a list and get a proper attr dict for the JsonAble
        return {"hard_attribute": list(self.hard_attribute),
                "json_able_attribute": self.json_able_attribute._get_attr_dict()}

    def __eq__(self, other):
        if isinstance(other, ComplexJsonAble):
            return self.hard_attribute == other.hard_attribute \
               and self.json_able_attribute.number == other.json_able_attribute.number \
               and self.json_able_attribute.string == other.json_able_attribute.string
        else:
            raise TypeError


@pytest.fixture
def complex_json_able_object():
    """Complex JSON able object with a rather hard-coded attributes."""
    obj = ComplexJsonAble()
    obj.json_able_attribute = JsonAble(number=123, string="my_string")
    obj.hard_attribute = set(["Initial value"])
    return obj


def test_complex_to_json(complex_json_able_object):
    """Test if we get a correct JSON string from a complex JSON object."""
    json_string = complex_json_able_object.to_json(indent="  ", sort_keys=True)
    assert json_string == """{
  "hard_attribute": [
    "Initial value"
  ],
  "json_able_attribute": {
    "number": 123,
    "string": "my_string"
  }
}"""


def test_complex_back_from_json(complex_json_able_object):
    """Test if we get the same attributes back for a complex object."""
    json_string = complex_json_able_object.to_json()
    obj_back_from_json = ComplexJsonAble.from_json(json_string)
    assert isinstance(obj_back_from_json.hard_attribute, set)
    assert obj_back_from_json == complex_json_able_object
