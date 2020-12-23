#!/usr/bin/env python3
# coding=utf-8

# MIT License
#
# Copyright 2017 Niels Lohmann <http://nlohmann.me>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import sys
from typing import List, Optional, Any, Set


def resolve_ref(ref):
    return ref.split('/')[-1]


class Property:
    def __init__(self, name, type, required, example=None, description=None, default=None, enum=None, format=None,
                 items=None, maximum=None, exclusive_maximum=False, minimum=None, exclusive_minimum=False,
                 multiple_of=None, max_length=None, min_length=0, pattern=None, max_items=None, min_items=0,
                 unique_items=False, ref_type=None):
        # type
        self.type = type  # type: str
        self.format = format  # type: Optional[str]
        self.ref_type = ref_type  # type: Optional[str]

        # constraints
        self.required = required  # type: bool
        self.enum = enum  # type: Optional[List[Any]]

        # documentation
        self.name = name  # type: str
        self.example = example  # type: Optional[Any]
        self.description = description  # type: Optional[str]
        self.default = default  # type: Optional[Any]

        # numbers
        self.maximum = maximum  # type: Optional[float,int]
        self.exclusive_maximum = exclusive_maximum  # type: bool
        self.minimum = minimum  # type: Optional[float,int]
        self.exclusive_minimum = exclusive_minimum  # type: bool
        self.multiple_of = multiple_of  # type: Optional[float,int]

        # strings
        self.max_length = max_length  # type: Optional[int]
        self.min_length = min_length  # type: int
        self.pattern = pattern  # type: Optional[str]

        # arrays
        self.max_items = max_items  # type: Optional[int]
        self.min_items = min_items  # type: int
        self.unique_items = unique_items  # type: bool
        self.items = items  # type: Optional[str]

    @staticmethod
    def from_dict(property_name, d, required):
        # whether the type was resolved
        ref_type = None

        # We use the Parameter class for parameters inside the swagger specification, but also for parameters. There,
        # type information is given in a "schema" property.
        if 'type' in d or '$ref' in d:
            type_dict = d
        elif 'schema' in d:
            type_dict = d['schema']
        elif 'allOf' in d and len(d['allOf']) > 0:
            type_dict = d['allOf'][0]
        else:
            type_dict = {}

        # type is given or must be resolved from $ref
        if 'type' in type_dict:
            type_str = type_dict['type']
        elif '$ref' in type_dict:
            type_str = resolve_ref(type_dict['$ref'])
            ref_type = type_str
        else:
            type_str = '<i>not specified</i>'

        # join multiple types to string
        if isinstance(type_str, list):
            type_str = '/'.join(type_str)

        # items type is given or must be resolved from $ref
        if 'items' in type_dict:
            if 'type' in type_dict['items']:
                items = type_dict['items']['type']
            else:
                items = resolve_ref(type_dict['items']['$ref'])
                ref_type = items
        else:
            items = None

        return Property(
            name=property_name,
            type=type_str,
            required=required,
            example=d.get('example'),
            description=d.get('description'),
            default=d.get('default'),
            enum=d.get('enum'),
            format=d.get('format'),
            items=items,
            maximum=d.get('maximum'),
            exclusive_maximum=d.get('exclusiveMaximum', False),
            minimum=d.get('minimum'),
            exclusive_minimum=d.get('exclusiveMinimum', False),
            multiple_of=d.get('multipleOf'),
            max_length=d.get('maxLength'),
            min_length=d.get('minLength', 0),
            pattern=d.get('pattern'),
            max_items=d.get('maxItems', 0),
            min_items=d.get('minItems'),
            unique_items=d.get('uniqueItems', False),
            ref_type=ref_type
        )

    @property
    def uml(self):
        # type or array
        if self.type == 'array':
            # determine lower and upper bound
            lower = ''
            upper = ''
            if self.min_items:
                lower = self.min_items if not self.exclusive_minimum else self.min_items + 1
            if self.max_items:
                upper = self.max_items if not self.exclusive_minimum else self.max_items - 1

            # combine lower and upper bound to bounds string
            bounds = ''
            if lower or upper:
                bounds = '{lower}:{upper}'.format(lower=lower, upper=upper)

            type_str = '{items}[{bounds}]'.format(items=self.items, bounds=bounds)
        else:
            type_str = self.type

        # format (e.g., date-time)
        if self.format:
            type_str += ' ({format})'.format(format=self.format)

        # name string (bold if property is required)
        if self.required:
            name_str = '<b>{name}</b>'.format(name=self.name)
        else:
            name_str = self.name

        # simple type definition ({field} is a keyword for PlantUML)
        result = '{{field}} {type_str} {name_str}'.format(type_str=type_str, name_str=name_str)

        # enum
        if self.enum is not None:
            result += ' {{{enum_str}}}'.format(enum_str=', '.join([json.dumps(x) for x in self.enum]))

        # min/max
        if self.minimum or self.maximum:
            minimum = self.minimum if self.minimum is not None else ''
            maximum = self.maximum if self.maximum is not None else ''
            result += ' {{{minimum}..{maximum}}}'.format(minimum=minimum, maximum=maximum)

        # default value
        if self.default is not None:
            result += ' = {default}'.format(default=json.dumps(self.default))

        return result


class Definition:
    def __init__(self, name, type, properties, relationships):
        self.name = name  # type: str
        self.type = type  # type: str
        self.properties = properties  # type: List[Property]
        self.relationships = relationships  # type: Set[str]

    @staticmethod
    def from_dict(name, d):
        properties = []  # type: List[Property]
        for property_name, property in d.get('properties', {}).items():
            properties.append(Property.from_dict(
                property_name=property_name,
                d=property,
                required=property_name in d.get('required', [])
            ))

        if not 'type' in d:
            print('required key "type" not found in dictionary ' + json.dumps(d), file=sys.stderr)

        return Definition(name=name,
                          type=d['type'],
                          properties=properties,
                          relationships={property.ref_type for property in properties if property.ref_type})

    @property
    def uml(self):
        result = 'class {name} {{\n'.format(name=self.name)

        # required properties first
        for property in sorted(self.properties, key=lambda x: x.required, reverse=True):
            result += '    {property_str}\n'.format(property_str=property.uml)

        result += '}\n\n'

        # add relationships
        for relationship in sorted(self.relationships):
            result += '{name} ..> {relationship}\n'.format(name=self.name, relationship=relationship)

        return result


class Parameter:
    def __init__(self, name, location, description, required, property):
        self.name = name  # type: str
        self.location = location  # type: str
        self.description = description  # type: Optional[str]
        self.required = required  # type: bool
        self.property = property  # type: Property

    @staticmethod
    def from_dict(whole, d):
        ref = d.get('$ref')
        if ref != None:
            d = whole['parameters'][resolve_ref(ref)]
        return Parameter(
            name=d['name'],
            location=d['in'],
            description=d.get('description'),
            required=d.get('required', False),
            property=Property.from_dict(d['name'], d, d.get('required', False))
        )


class Response:
    def __init__(self, status, description, property):
        self.status = status  # type: str
        self.description = description  # type: Optional[str]
        self.property = property  # type: Property

    @staticmethod
    def from_dict(whole, status, d):
        return Response(
            status=status,
            description=d.get('description'),
            property=Property.from_dict('', d, False)
        )

    @property
    def uml(self):
        return '{status}: {type}'.format(
            status=self.status,
            type=self.property.uml
        )


class Operation:
    def __init__(self, path, type, summary, description, responses, tags, parameters):
        self.path = path  # type: str
        self.type = type  # type: str
        self.summary = summary  # type: Optional[str]
        self.description = description  # type: Optional[str]
        self.responses = responses  # type: List[Response]
        self.tags = tags  # type: List[str]
        self.parameters = parameters  # type: List[Parameter]

    def __lt__(self, other):
        return self.type < other.type

    @staticmethod
    def from_dict(whole, path, type, d, path_parameters):
        return Operation(
            path=path,
            type=type,
            summary=d.get('summary'),
            description=d.get('description'),
            tags=d.get('tags'),
            responses=[Response.from_dict(whole, status, response) for status, response in d['responses'].items()],
            parameters=path_parameters + [Parameter.from_dict(whole, param) for param in d.get('parameters', [])]
        )

    @property
    def uml(self):
        # collect used parameter locations
        possible_types = ['header', 'path', 'query', 'body', 'formData']
        parameter_types = {x.location for x in self.parameters}

        parameter_strings = []
        for parameter_type in [x for x in possible_types if x in parameter_types]:
            # add heading
            parameter_strings.append('.. {parameter_type} ..'.format(parameter_type=parameter_type))
            # add parameters
            for parameter in [x for x in self.parameters if x.location == parameter_type]:
                parameter_strings.append('{parameter_uml}'.format(parameter_uml=parameter.property.uml))

        # collect references from responses and parameters
        references = [x.property.ref_type for x in self.responses if x.property.ref_type] + \
                     [x.property.ref_type for x in self.parameters if x.property.ref_type]

        return """class "{name}" {{\n{parameter_str}\n.. responses ..\n{response_str}\n}}\n\n{associations}\n""".format(
            name=self.name,
            response_str='\n'.join([x.uml for x in self.responses]),
            parameter_str='\n'.join(parameter_strings),
            associations='\n'.join({'"{name}" ..> {type}'.format(name=self.name, type=type) for type in references})
        )

    @property
    def name(self):
        return '{type} {path}'.format(
            type=self.type.upper(),
            path=self.path
        )


class Path:
    def __init__(self, path, operations):
        self.path = path  # type: str
        self.operations = operations  # type: List[Operation]

    @staticmethod
    def from_dict(whole, path_name, d):
        parameters = [Parameter.from_dict(whole, param) for param in d.get('parameters', [])]
        return Path(
            path=path_name,
            operations=[Operation.from_dict(whole, path_name, t, op, parameters) for t, op in d.items() if t not in ['parameters', 'summary', 'description']]
        )

    @property
    def uml(self):
        return 'interface "{path}" {{\n}}\n\n{operation_str}\n{association_str}\n\n'.format(
            path=self.path,
            operation_str='\n'.join([op.uml for op in self.operations]),
            association_str='\n'.join(['"{path}" ..> "{operation_name}"'.format(
                path=self.path, operation_name=op.name) for op in sorted(self.operations)])
        )


class Swagger:
    def __init__(self, definitions, paths):
        self.definitions = definitions  # type: List[Definition]
        self.paths = paths  # type: List[Path]

    @staticmethod
    def from_dict(d):
        definitions = [Definition.from_dict(name, definition) for name, definition in d.get('definitions',{}).items()]
        paths = [Path.from_dict(d, path_name, path) for path_name, path in d['paths'].items()]
        return Swagger(definitions=definitions, paths=paths)

    @staticmethod
    def from_file(filename):
        loader = json.load
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            import yaml
            loader = yaml.load
        with open(filename, 'r') as fd:
            return Swagger.from_dict(loader(fd))

    @property
    def uml(self):
        uml_str = '@startuml\nhide empty members\nset namespaceSeparator none\n\n{paths}\n{definitions}\n@enduml\n'
        return uml_str.format(
            paths='\n\n'.join([d.uml for d in self.paths]),
            definitions='\n\n'.join([d.uml for d in self.definitions])
        )


if __name__ == '__main__':
    input_file_name = sys.argv[1]
    sw = Swagger.from_file(input_file_name)
    print(sw.uml, end='', flush=True)
