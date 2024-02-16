# -*- coding: utf-8 -*-
import re
from itertools import chain

from pypeg2 import List, contiguous, csl, name, optional, parse


def error_response(error, msg):
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": 200,
            "message": msg,
            "data": {
                "name": str(error),
                "debug": "",
                "message": msg,
                "arguments": list(error.args),
                "exception_type": type(error).__name__
            }
        }
    }


class TortecsSerializer(object):
    def __init__(self, record, query="{*}", many=False):
        self.many = many
        self._record = record
        self._raw_query = query
        super().__init__()

    def get_parsed_restql_query(self):
        parser = TortecsParser(self._raw_query)
        try:
            parsed_restql_query = parser.get_parsed()
            return parsed_restql_query
        except SyntaxError as e:
            msg = "QuerySyntaxError: " + e.msg + " on " + e.text
            raise SyntaxError(msg) from None
        except Exception as e:
            msg = "QueryFormatError: " + str(e)
            raise Exception(msg) from None

    @property
    def data(self):
        parsed_restql_query = self.get_parsed_restql_query()
        if self.many:
            return [
                self.serialize(rec, parsed_restql_query)
                for rec
                in self._record
            ]
        return self.serialize(self._record, parsed_restql_query)

    @classmethod
    def build_flat_field(cls, rec, field_name):
        all_fields = rec.fields_get_keys()
        if field_name not in all_fields:
            msg = "'%s' field is not found" % field_name
            raise LookupError(msg)
        field_type = rec.fields_get(field_name).get(field_name).get('type')
        if field_type in ['one2many', 'many2many']:
            return {
                field_name: [record.id for record in rec[field_name]]
            }
        elif field_type in ['many2one']:
            return {
                field_name: rec[field_name].id
            }
        elif field_type == "binary" and isinstance(rec[field_name], bytes) and rec[field_name]:
            return {
                field_name: rec[field_name].decode("utf-8")
            }
        elif field_type == 'datetime' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%Y-%m-%d-%H-%M")
            }
        elif field_type == 'date' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%Y-%m-%d")
            }
        elif field_type == 'time' and rec[field_name]:
            return {
                field_name: rec[field_name].strftime("%H-%M-%S")
            }
        else:
            return {field_name: rec[field_name]}

    @classmethod
    def build_nested_field(cls, rec, field_name, nested_parsed_query):
        all_fields = rec.fields_get_keys()
        if field_name not in all_fields:
            msg = "'%s' field is not found" % field_name
            raise LookupError(msg)
        field_type = rec.fields_get(field_name).get(field_name).get('type')
        if field_type in ['one2many', 'many2many']:
            return {
                field_name: [
                    cls.serialize(record, nested_parsed_query)
                    for record
                    in rec[field_name]
                ]
            }
        elif field_type in ['many2one']:
            return {
                field_name: cls.serialize(rec[field_name], nested_parsed_query)
            }
        else:
            # Not a neste field
            msg = "'%s' is not a nested field" % field_name
            raise ValueError(msg)

    @classmethod
    def serialize(cls, rec, parsed_query):
        data = {}

        '''
            NOTE: self.parsed_restql_query["include"] not being empty is not a guarantee that the exclude operator(-) 
            has not been used because the same self.parsed_restql_query["include"] is used to store nested fields when 
            the exclude operator(-) is used
        '''
        if parsed_query["exclude"]:
            # Exclude fields from a query
            all_fields = rec.fields_get_keys()
            for field in parsed_query["include"]:
                if field == "*":
                    continue
                for nested_field, nested_parsed_query in field.items():
                    built_nested_field = cls.build_nested_field(
                        rec,
                        nested_field,
                        nested_parsed_query
                    )
                    data.update(built_nested_field)

            flat_fields = set(all_fields).symmetric_difference(set(parsed_query['exclude']))
            for field in flat_fields:
                flat_field = cls.build_flat_field(rec, field)
                data.update(flat_field)

        elif parsed_query["include"]:
            '''
                Here we are sure that self.parsed_restql_query["exclude"] is empty which means the exclude operator(-) 
                is not used, so self.parsed_restql_query["include"] contains only fields to include
            '''

            all_fields = rec.fields_get_keys()
            if "*" in parsed_query['include']:
                # Include all fields
                parsed_query['include'] = filter(lambda item: item != "*", parsed_query['include'])
                fields = chain(parsed_query['include'], all_fields)
                parsed_query['include'] = list(fields)

            for field in parsed_query["include"]:
                if isinstance(field, dict):
                    for nested_field, nested_parsed_query in field.items():
                        built_nested_field = cls.build_nested_field(rec, nested_field, nested_parsed_query)
                        data.update(built_nested_field)
                else:
                    flat_field = cls.build_flat_field(rec, field)
                    data.update(flat_field)
        else:
            # The query is empty i.e query={}
            # return nothing
            return {}
        return data

class IncludedField(List):
    grammar = name()


class ExcludedField(List):
    grammar = contiguous('-', name())


class AllFields(str):
    grammar = '*'


class BaseArgument(List):
    @property
    def value(self):
        return self[0]


class ArgumentWithoutQuotes(BaseArgument):
    grammar = name(), ':', re.compile(r'[^,:"\'\)]+')


class ArgumentWithSingleQuotes(BaseArgument):
    grammar = name(), ':', "'", re.compile(r'[^\']+'), "'"


class ArgumentWithDoubleQuotes(BaseArgument):
    grammar = name(), ':', '"', re.compile(r'[^"]+'), '"'


class Arguments(List):
    grammar = optional(csl(
        [
            ArgumentWithoutQuotes,
            ArgumentWithSingleQuotes,
            ArgumentWithDoubleQuotes
        ],
        separator=','
    ))


class ArgumentsBlock(List):
    grammar = optional('(', Arguments, ')')

    @property
    def arguments(self):
        if self[0] is None:
            return []  # No arguments
        return self[0]


class ParentField(List):
    """
    According to ParentField grammar:
    self[0]  returns IncludedField instance,
    self[1]  returns Block instance
    """

    @property
    def name(self):
        return self[0].name

    @property
    def block(self):
        return self[1]


class BlockBody(List):
    grammar = optional(csl(
        [ParentField, IncludedField, ExcludedField, AllFields],
        separator=','
    ))


class Block(List):
    grammar = ArgumentsBlock, '{', BlockBody, '}'

    @property
    def arguments(self):
        return self[0].arguments

    @property
    def body(self):
        return self[1]


# ParentField grammar,
# We don't include `ExcludedField` here because
# exclude operator(-) on a parent field should
# raise syntax error, e.g {name, -location{city}}
# `IncludedField` is a parent field and `Block`
# contains its sub fields
ParentField.grammar = IncludedField, Block


class TortecsParser(object):
    def __init__(self, query):
        self._query = query

    def get_parsed(self):
        parse_tree = parse(self._query, Block)
        return self._tt_transform_block(parse_tree)

    def _tt_transform_block(self, block):
        fields = {
            "include": [],
            "exclude": [],
            "arguments": {}
        }

        for argument in block.arguments:
            argument = {str(argument.name): argument.value}
            fields['arguments'].update(argument)

        for field in block.body:
            # A field may be a parent or included field or excluded field
            field = self._tt_transform_field(field)

            if isinstance(field, dict):
                # A field is a parent
                fields["include"].append(field)
            elif isinstance(field, IncludedField):
                fields["include"].append(str(field.name))
            elif isinstance(field, ExcludedField):
                fields["exclude"].append(str(field.name))
            elif isinstance(field, AllFields):
                # include all fields
                fields["include"].append("*")

        if fields["exclude"]:
            # fields['include'] should contain only nested fields

            # We should add `*` operator in fields['include']
            add_include_all_operator = True
            for field in fields["include"]:
                if field == "*":
                    # `*` operator is alredy in fields['include']
                    add_include_all_operator = False
                    continue

                if isinstance(field, str):
                    # Including and excluding fields on the same field level
                    msg = (
                        "Can not include and exclude fields on the same "
                        "field level"
                    )
                    raise ValueError(msg)

            if add_include_all_operator:
                # Make sure we include * operator
                fields["include"].append("*")
        return fields

    def _tt_transform_field(self, field):
        # A field may be a parent or included field or excluded field
        if isinstance(field, ParentField):
            return self._tt_transform_parent_field(field)
        elif isinstance(field, (IncludedField, ExcludedField, AllFields)):
            return field

    def _tt_transform_parent_field(self, parent_field):
        parent_field_name = str(parent_field.name)
        parent_field_value = self._tt_transform_block(parent_field.block)
        return {parent_field_name: parent_field_value}
