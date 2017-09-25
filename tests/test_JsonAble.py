import copy
import pytest

from grids_two import JsonAble


#
# Simple tests
#


@pytest.fixture
def simple_json_able_object():
    """A really simple JsonAble object where all attributes act nice in JSON.
    
    This fixture includes the object and its expected JSON string when sorting
    the keys and using two spaces to indent.
    """
    obj = JsonAble(foo="foo string", leet=1337, bar=["beer", "shots"])
    expected_json_string = """{
  "bar": [
    "beer",
    "shots"
  ],
  "foo": "foo string",
  "leet": 1337
}"""
    return obj, expected_json_string


def test_simle_eq(simple_json_able_object):
    obj, _ = simple_json_able_object
    # Default implementation compares by object identity
    assert obj != 3
    assert obj != "String"
    assert obj == obj


def test_simple_to_json(simple_json_able_object):
    """Test if we get a correct JSON string from a simple JSON object."""
    obj, expected_json_string = simple_json_able_object
    json_string = obj.to_json(indent="  ", sort_keys=True)
    assert json_string == expected_json_string
    assert json_string != expected_json_string.replace("string", "attr")


def test_simple_back_from_json(simple_json_able_object):
    """Test if we get the same attributes back."""
    obj, json_string = simple_json_able_object
    obj_back_from_json = JsonAble.from_json(json_string)
    assert obj_back_from_json.bar == obj.bar
    assert obj_back_from_json.foo == obj.foo
    assert obj_back_from_json.leet == obj.leet


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
    """Complex JSON able object with a rather hard-coded attributes.
    
    This fixture includes the object and its expected JSON string when sorting
    the keys and using two spaces to indent.
    """
    obj = ComplexJsonAble()
    obj.json_able_attribute = JsonAble(number=123, string="my_string")
    obj.hard_attribute = set(["Initial value"])
    expected_json_string = """{
  "hard_attribute": [
    "Initial value"
  ],
  "json_able_attribute": {
    "number": 123,
    "string": "my_string"
  }
}"""
    return obj, expected_json_string


def test_complex_eq(complex_json_able_object):
    obj, _ = complex_json_able_object
    with pytest.raises(TypeError):
        assert obj != 3
    with pytest.raises(TypeError):
        assert obj != "String"
    assert obj == obj
    assert not obj != obj
    obj1 = copy.deepcopy(obj)
    obj2 = copy.deepcopy(obj)
    obj3 = copy.deepcopy(obj)
    assert obj == obj1
    assert obj == obj2
    assert obj == obj3
    # Modify obj1 and compare
    obj1.hard_attribute.add("pine cool aide")
    assert obj != obj1
    # Modify obj2 and compare
    obj2.json_able_attribute.number += 1
    assert obj != obj2
    # Modify obj3 and compare
    obj3.json_able_attribute.string += "moo"
    assert obj != obj3


def test_complex_to_json(complex_json_able_object):
    """Test if we get a correct JSON string from a complex JSON object."""
    obj, expected_json_string = complex_json_able_object
    json_string = obj.to_json(indent="  ", sort_keys=True)
    assert json_string == expected_json_string


def test_complex_back_from_json(complex_json_able_object):
    """Test if we get the same attributes back for a complex object."""
    obj, json_string = complex_json_able_object
    obj_back_from_json = ComplexJsonAble.from_json(json_string)
    assert isinstance(obj_back_from_json.hard_attribute, set)
    assert obj_back_from_json == obj
