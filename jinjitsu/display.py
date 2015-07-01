__author__ = 'thomas'

from jinja2 import nodes
from jinja2.ext import Extension
import inspect


class Property(object):
    def __init__(self, type=None, template=None, css_classes="", label=None):
        self.type = type
        self.template = template
        self.css_classes = css_classes
        self.label = label


class ViewModelMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        cls._properties = {}
        for name, prop in new_attrs.items():
            if isinstance(prop, Property):
                prop.name = name
                cls._properties[name] = prop

        return cls


class ViewModel(object):
    __metaclass__ = ViewModelMeta
    includes = []
    excludes = []

    def __init__(self, obj_type=None):
        self.type = obj_type
        self.all_models = None
        print self.specified_properties

    @property
    def specified_properties(self):
        return set(self.includes + [name for name in self._properties])

    def get_property(self, property_name):
        if property_name in self._properties:
            return self._properties[property_name]
        else:
            prop = Property(property_name)
            prop.name = property_name
            return prop


class PropertiesList(object):
    def __init__(self, view_model, obj):
        self.view_model = view_model
        self.obj = obj

    def __iter__(self):
        if self.view_model.includes:
            return iter(self.view_model.specified_properties)
        return iter(self.get_all_public_not_excluded_members())

    def get_all_public_not_excluded_members(self):
        """
        TODO this should handle dictionaries too.
        lists and strings have no members that we care about so return an empty list for them.
        :param obj:
        :return:
        """
        if isinstance(self.obj, dict):
            return [key for key in self.obj if key not in self.view_model.excludes]
        try:
            iter(self.obj)
            return []
        except TypeError:
            return [member[0] for member in inspect.getmembers(self.obj)
                    if not member[0].startswith('_')
                    and member[0] not in self.view_model.excludes]


class PropertyDetails(object):
    def __init__(self, name, property_definition, property_type, property_value):
        self.name = name
        self.property_definition = property_definition
        self.property_type = property_type
        self.property_value = property_value

        self.properties = PropertiesList(property_type, property_value)


class DisplayModels(object):
    def __init__(self):
        self.models = {}  # {string: ViewModel}

    def add_model(self, type, model):
        self.models[type] = model
        model.all_models = self

    def get_model_for_type(self, obj_type):
        """
        TODO: Should this also be able to take in an actual type?
        :param obj_type:
        :return:
        """
        if obj_type in self.models:
            return self.models[obj_type]()
        return ViewModel()

    def get_property_details(self, view_model, property_name, property_value):
        prop = view_model.get_property(property_name)

        property_type = self.get_model_for_type(prop.type)

        #
        if not property_type.type:
            property_type.type = self.get_model_for_type(property_value.__class__.__name__)

        return PropertyDetails(property_name, prop, property_type, property_value)


class DisplayExtension(Extension):
    tags = set(['display'])
    default_template_path = 'display'

    def __init__(self, environment):
        environment.extend(
            display_template_path=self.default_template_path,
            display_template_extension='html',
            display_models=DisplayModels()
        )
        self.format_string = "{path}/{template_name}.{extension}"
        super(DisplayExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        obj = self.parse_object(parser)
        as_model = self.parse_as(parser)
        includes, excludes = self.parse_includes(parser)

        property_name = self.get_property_name(obj)
        current_property = self.get_current_property()
        property_details = self.get_property_details(obj, as_model, property_name, includes, excludes)
        properties = self.get_properties(obj, property_details)

        assignments = [
            self.assign_obj(obj, property_details, lineno),
            self.assign_property_details(obj, property_details, lineno),
            self.assign_properties(obj, properties, lineno),
        ]

        template = self.include_template(obj, property_details)

        return self.create_node(assignments, template)

    def parse_object(self, parser):
        return parser.parse_expression()

    def parse_as(self, parser):
        if parser.stream.next_if('name:as'):
            return parser.parse_expression()
        return nodes.Const(None)

    def parse_includes(self, parser):
        if parser.stream.next_if('name:include'):
            includes = parser.parse_expression()
            excludes = nodes.Const(None)
        elif parser.stream.next_if('name:exclude'):
            includes = nodes.Const(None)
            excludes = parser.parse_expression()
        return includes, excludes

    def get_property_name(self, obj):
        property_stack = self.get_property_stack(obj)
        if property_stack:
            return nodes.List(property_stack)
        return nodes.Const(None)

    def get_current_property(self):
        return nodes.Name('property', 'load')

    def get_property_details(self, obj, current_property,  property_name):
        return self.call_method('call_get_property_details', args=[obj, current_property, property_name])

    def call_get_property_details(self, obj, current_property, property_stack, as_model, includes=None, excludes=None):
        print(obj)
        print(property_stack)
        includes = make_sure_is_list(includes)
        excludes = make_sure_is_list(excludes)

        if not current_property:
            view_model = self.environment.display_models.get_model_for_type(obj.__class__.__name__)
        else:
            view_model = current_property.view_model

        for property_name in property_stack:
            current_obj = self.environment.getattr(current_obj, property_name)
            property_details = self.environment.display_models.get_property_details(view_model, property_name, current_obj)
            view_model = property_details.view_model

        if as_model:
            property_details.view_model = self.environment.display_models.get_model_for_type(as_model)



        return property_details



        new_property = self.environment.display_models.get_property_details(view_model, property_name, obj)
        return PropertyDetails(property_name, include=includes, exclude=excludes)


    def assign_obj(self, obj, property_details, lineno):
        return nodes.Assign(nodes.Name('obj', 'store', lineno=lineno),
                            self.call_method('call_assign_obj', args=[obj, property_details]), lineno=lineno)

    def call_assign_obj(self, obj, property_details):
        return property_details.format_value(obj)

    def assign_property_details(self, property_details, lineno):
        return nodes.Assign(nodes.Name('property', 'store', lineno=lineno), property_details, lineno=lineno)

    def assign_properties(self, lineno):
        return nodes.Assign(nodes.Name('properties', 'store'),
                            nodes.Getattr(nodes.Name('property', 'store'), 'properties'),
                            lineno=lineno)

    def include_template(self, obj, property_details):
        return nodes.Include(self.call_method('call_get_template_list', args=[obj, property_details]), True, False)

    def call_get_template_list(self, obj, property_details):
        templates = []
        if property_details and property_details.template:
            templates.append(self.get_template_path(property_details.template))
        return templates + [self.get_template_path(cls.__name__) for cls in inspect.getmro(obj.__class__)]

    def get_template_path(self, name):
        return self.format_string.format(path=self.environment.display_template_path,
                                         template_name=name,
                                         extension=self.environment.display_template_extension)

    def create_node(self, assignments, template):
        return nodes.Scope(assignments + [template])


def make_sure_is_list(list_to_check):
    if not list_to_check:
        return list_to_check
    if isinstance(list_to_check, basestring):
        return [list_to_check]
    try:
        iter(list_to_check)
        return list_to_check
    except TypeError:
        return [list_to_check]