from jinjitsu import display


def test_viewmodel_init():
    view_model = display.ViewModel("int")
    assert view_model
    assert view_model.type == "int"


class TestViewModel(display.ViewModel):
    includes = ['name', 'age']


def test_view_model_subclass():
    test = TestViewModel()
    #assert test.type == "TestViewModel"     # does this even make sense?


def test_view_model_subclass_with_includes():
    test = TestViewModel()
    assert test.specified_properties == set(['name', 'age'])


class TestViewModelWithProperties(display.ViewModel):
    name = display.Property(type="string")


def test_view_model_subclass_with_property():
    test = TestViewModelWithProperties()
    assert test.specified_properties == set(['name'])


class TestViewModelWithPropertiesAndIncludes(display.ViewModel):
    includes = ['age']
    name = display.Property(type="string")


def test_view_model_subclass_with_property_and_includes():
    test = TestViewModelWithPropertiesAndIncludes()
    assert set(test.specified_properties) == set(['name', 'age'])


def test_view_model__get_property_unknown():
    test = TestViewModel()
    prop = test.get_property("height")
    assert prop.name == "height"


def test_view_model__get_property__from_include():
    test = TestViewModel()
    prop = test.get_property("age")
    assert prop.name == "age"


def test_view_model__get_property__from_specified():
    test = TestViewModelWithProperties()
    prop = test.get_property("name")
    assert prop.name == "name"


def test_view_model__get_property__from_specified():
    test = TestViewModelWithProperties()
    prop = test.get_property("name")
    assert prop.type == "string"