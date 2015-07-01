__author__ = 'Tom'


from jinjitsu import display




def test_PropertyList_dictionary():
    dictionary = {"name": "thomas", "age": "27", "height": "6ft 3in"}
    prop_list = display.PropertiesList(display.ViewModel(), dictionary)
    assert set(prop_list) == set(['name', 'age', 'height'])


class TestViewModel(display.ViewModel):
    includes = ['name', 'age']


def test_PropertyList_dictionary_includes():
    dictionary = {"name": "thomas", "age": "27", "height": "6ft 3in"}
    prop_list = display.PropertiesList(TestViewModel(), dictionary)
    assert set(prop_list) == set(['name', 'age'])


class TestViewModelExcludes(display.ViewModel):
    excludes = ['name', 'age']


def test_PropertyList_dictionary_excludes():
    dictionary = {"name": "thomas", "age": "27", "height": "6ft 3in"}
    prop_list = display.PropertiesList(TestViewModelExcludes(), dictionary)
    assert set(prop_list) == set(['height'])


def test_PropertyList_list():
    list = ['name', 1, 7]
    prop_list = display.PropertiesList(display.ViewModel(), list)
    assert set(prop_list) == set([])


def test_PropertyList_list_includes():
    list = ['name', 1, 7]
    prop_list = display.PropertiesList(TestViewModel(), list)
    assert set(prop_list) == set(['name', 'age'])


def test_PropertyList_list_excludes():
    list = ['name', 1, 7]
    prop_list = display.PropertiesList(TestViewModelExcludes(), list)
    assert set(prop_list) == set([])


class TestObj(object):
    pass


def test_PropertyList_obj():
    obj = TestObj()
    obj.name = 'thomas'
    obj.age = '27'
    obj.address = '1 place street'
    prop_list = display.PropertiesList(display.ViewModel(), obj)
    assert set(prop_list) == set(['name', 'age', 'address'])


def test_PropertyList_obj_includes():
    obj = TestObj()
    obj.name = 'thomas'
    obj.age = '27'
    obj.address = '1 place street'
    prop_list = display.PropertiesList(TestViewModel(), obj)
    assert set(prop_list) == set(['name', 'age'])


def test_PropertyList_obj_excludes():
    obj = TestObj()
    obj.name = 'thomas'
    obj.age = '27'
    obj.address = '1 place street'
    prop_list = display.PropertiesList(TestViewModelExcludes(), obj)
    assert set(prop_list) == set(['address'])