__author__ = 'Tom'


from jinjitsu import display


class TestViewModel(display.ViewModel):
    includes = ['name', 'age']


def test_DisplayModels_add_model():
    display_models = display.DisplayModels()
    display_models.add_model("user", TestViewModel)

    assert display_models.models["user"] == TestViewModel


def test_DisplayModels_get_model_for_type_found():
    display_models = display.DisplayModels()
    display_models.add_model("user", TestViewModel)

    gotten_model = display_models.get_model_for_type("user")
    assert isinstance(gotten_model, TestViewModel)


def test_DisplayModels_get_model_for_type_not_found():
    display_models = display.DisplayModels()
    display_models.add_model("user", TestViewModel)

    gotten_model = display_models.get_model_for_type("not_user")
    assert isinstance(gotten_model, display.ViewModel)


def find_property_details():
    display_models = display.DisplayModels()
    display_models.add_model("user", TestViewModel)

    gotten_model = display_models.get_model_for_type("user")

    return display_models.get_property_details(gotten_model, 'name', {'name': 'thomas'})


def test_DisplayModels_get_property_details_found_name():
    assert find_property_details().name == "name"


def test_DisplayModels_get_property_details_found_view_model_not_found():
    assert isinstance(find_property_details().property_type, display.ViewModel)


def test_DisplayModels_get_property_details_found_view_model_not_found_right_default_type():
    print (find_property_details().property_type.type)


def test_DisplayModels_get_property_details_not_found():
    pass