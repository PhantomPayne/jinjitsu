__author__ = 'thomas'

from jinja2 import nodes
from jinja2.ext import Extension
import inspect
import os


class PropertyDetails(object):
    def __init__(self, name, template=None, css_classes="", label=None, include=None, exclude=None):
        self.name = name
        self.template = template
        self.css_classes = css_classes
        self.label = label or name
        self.include = include
        self.exclude = exclude

    def format_value(self, obj):
        return obj

    def get_extra_css_classes(self, obj):
        return ''

    def populate(self, obj):
        self.css_classes += self.get_extra_css_classes(obj)


class DisplayModel(PropertyDetails):
    """
    TODO: need to use a metaclass to convert the different types of DisplayProperties to self.fields?
    """
    pass


class DisplayExtension(Extension):
    tags = set(['display'])
    default_template_path = 'display'

    def __init__(self, environment):
        environment.extend(
            display_template_path=self.default_template_path,
            display_template_extension='html',
            display_models={}  # These will be stored in the format {Type: ViewModelType}
        )
        self.format_string = "{path}/{template_name}.{extension}"
        super(DisplayExtension, self).__init__(environment)

    def parse(self, parser):
        stream = parser.stream
        lineno = stream.next().lineno
        print(lineno)

        name = parser.parse_expression()
        objvar = nodes.Name('obj', 'load', lineno=lineno)


        print name
        assignments = []
        has_property_details_kwargs = {}
        property_stack = self.get_property_stack(name)
        if property_stack:
            print('property_stack', property_stack)
            property_var = nodes.Name('property', 'store', lineno=lineno)
            property_node = nodes.Const(property_stack[-1])
            property_details_node = self.call_method('get_property_details', args=[objvar, property_node])
            assignments.append(nodes.Assign(property_var, property_details_node, lineno=lineno))
            has_property_details_kwargs['property'] = property_var

        get_template_args = [objvar]
        properties_args = [name]
        if stream.next_if('name:as'):
            as_type = parser.parse_expression()
            get_template_args.append(as_type)
        if stream.next_if('name:with'):
            with_node = parser.parse_expression()
            print("with_node", with_node)
            properties_args.append(with_node)

        properties_var = nodes.Name('properties', 'store', lineno=lineno)
        properties_node = self.call_method('get_properties', args=properties_args, kwargs=has_property_details_kwargs)
        assignments.append(nodes.Assign(properties_var, properties_node, lineno=lineno))

        call_node = self.call_method('get_template_list', args=get_template_args, kwargs=has_property_details_kwargs)
        scope = nodes.Scope(lineno=lineno)
        assign_obj = nodes.Assign(objvar, name, lineno=lineno)
        assignments.append(assign_obj)

        scope.body = assignments + [nodes.Include(call_node, True, False, lineno=lineno)]
        print(scope)
        return scope

    def get_template_list(self, object_to_display, as_type=None, property=None):
        """
        This gets a list of possible templates based on all the base classes.  This way you can override any subclass
        and it will get it's specific template, otherwise it will use it's parents template.  Having a template for
        object will make sure that this will always find something to fall back to.

        You can pass in a specific template in case you want to render it a certain way.  This is useful for switching
        between displaying one list as a table and another as a ul without giving them weird subclasses of list to pick
        up the templates.

        :param object_to_display: The object that's going to be displayed
        :param as_type: This is passed in if the user specifies a template to use.
        :param of_type: This allows a user to specify a template down one level
        :return: a list of templates to try to load.
        """
        # If the user gives us a specific template to use, then lets use it.
        if as_type:
            # TODO: Link this up to the viewModel list.  This way we can grab out display properties.
            return self.get_template_path(as_type)

        if property and property.template:
            return self.get_template_path(property.template)

        return [self.get_template_path(cls.__name__) for cls in inspect.getmro(object_to_display.__class__)]

    def get_template_path(self, name):
        return self.format_string.format(path=self.environment.display_template_path,
                                         template_name=name,
                                         extension=self.environment.display_template_extension)

    def get_all_public_members(self, name):
        try:
            iter(name)
            return None
        except TypeError:
            return [member[0] for member in inspect.getmembers(name) if not member[0].startswith('_')]

    def get_view_model(self, name):
        return {'name': 'thomas', 'formatValue': lambda x: "tom"}

    def get_property_stack(self, node):
        if isinstance(node, nodes.Const):
            return [node.value]
        if isinstance(node, nodes.Name):
            return [node.name]
        if isinstance(node, nodes.Getattr):
            return self.get_property_stack(node.node) + [node.attr]
        if isinstance(node, nodes.Getitem):
            return self.get_property_stack(node.node) + [self.get_property_stack(node.arg)]
        return []

    def get_property_details(self, obj, property_name):
        """
        Property details

        :param obj:
        :param property_name:
        :return:
        """

        print(obj)
        print(property_name)

        if obj in self.environment.display_models:
            model = self.environment.display_models[obj]
            # TODO: put this in a loop so that you can do {% display obj.address.street %} and get the right data
            property_details = self.environment.getattr(model, property_name)
            if not isinstance(property_details, self.environment.undefined):
                return property_details
        return PropertyDetails(property_name)

    def get_properties(self, name, property_list=None):
        all_properties = self.get_all_public_members(name)
        if not all_properties and not property_list:
            return []
        if all_properties and not property_list:
            return all_properties

        property_list = self.make_sure_list_is_list(property_list)

        if not all_properties:
            return property_list

        return set(all_properties).intersection(property_list)

    def make_sure_list_is_list(self, list_to_check):
        if isinstance(list_to_check, basestring):
            return [list_to_check]
        try:
            iter(list_to_check)
            return list_to_check
        except TypeError:
            return [list_to_check]


class EditExtension(DisplayExtension):
    tags = set(['edit'])
    default_template_path = 'edit'