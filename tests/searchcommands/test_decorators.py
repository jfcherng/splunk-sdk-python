#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2011-2024 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from unittest import main, TestCase
import sys

from io import TextIOWrapper
import pytest

from splunklib.searchcommands import Configuration, Option, environment, validators
from splunklib.searchcommands.decorators import ConfigurationSetting
from splunklib.searchcommands.internals import json_encode_string
from splunklib.searchcommands.search_command import SearchCommand

from tests.searchcommands import rebase_environment


@Configuration()
class TestSearchCommand(SearchCommand):
    boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        validate=validators.Boolean())

    required_boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        require=True, validate=validators.Boolean())

    aliased_required_boolean = Option(
        doc='''
        **Syntax:** **boolean=***<value>*
        **Description:** A boolean value''',
        name='foo', require=True, validate=validators.Boolean())

    code = Option(
        doc='''
        **Syntax:** **code=***<value>*
        **Description:** A Python expression, if mode == "eval", or statement, if mode == "exec"''',
        validate=validators.Code())

    required_code = Option(
        doc='''
        **Syntax:** **code=***<value>*
        **Description:** A Python expression, if mode == "eval", or statement, if mode == "exec"''',
        require=True, validate=validators.Code())

    duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        validate=validators.Duration())

    required_duration = Option(
        doc='''
        **Syntax:** **duration=***<value>*
        **Description:** A length of time''',
        require=True, validate=validators.Duration())

    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        validate=validators.Fieldname())

    required_fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<value>*
        **Description:** Name of a field''',
        require=True, validate=validators.Fieldname())

    file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        validate=validators.File())

    required_file = Option(
        doc='''
        **Syntax:** **file=***<value>*
        **Description:** Name of a file''',
        require=True, validate=validators.File())

    integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        validate=validators.Integer())

    required_integer = Option(
        doc='''
        **Syntax:** **integer=***<value>*
        **Description:** An integer value''',
        require=True, validate=validators.Integer())

    float = Option(
        doc='''
        **Syntax:** **float=***<value>*
        **Description:** An float value''',
        validate=validators.Float())

    required_float = Option(
        doc='''
        **Syntax:** **float=***<value>*
        **Description:** An float value''',
        require=True, validate=validators.Float())

    map = Option(
        doc='''
        **Syntax:** **map=***<value>*
        **Description:** A mapping from one value to another''',
        validate=validators.Map(foo=1, bar=2, test=3))

    required_map = Option(
        doc='''
        **Syntax:** **map=***<value>*
        **Description:** A mapping from one value to another''',
        require=True, validate=validators.Map(foo=1, bar=2, test=3))

    match = Option(
        doc='''
        **Syntax:** **match=***<value>*
        **Description:** A value that matches a regular expression pattern''',
        validate=validators.Match('social security number', r'\d{3}-\d{2}-\d{4}'))

    required_match = Option(
        doc='''
        **Syntax:** **required_match=***<value>*
        **Description:** A value that matches a regular expression pattern''',
        require=True, validate=validators.Match('social security number', r'\d{3}-\d{2}-\d{4}'))

    optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        validate=validators.OptionName())

    required_optionname = Option(
        doc='''
        **Syntax:** **optionname=***<value>*
        **Description:** The name of an option (used internally)''',
        require=True, validate=validators.OptionName())

    regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        validate=validators.RegularExpression())

    required_regularexpression = Option(
        doc='''
        **Syntax:** **regularexpression=***<value>*
        **Description:** Regular expression pattern to match''',
        require=True, validate=validators.RegularExpression())

    set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** A member of a set''',
        validate=validators.Set('foo', 'bar', 'test'))

    required_set = Option(
        doc='''
        **Syntax:** **set=***<value>*
        **Description:** A member of a set''',
        require=True, validate=validators.Set('foo', 'bar', 'test'))

    class ConfigurationSettings(SearchCommand.ConfigurationSettings):
        @classmethod
        def fix_up(cls, command_class):
            pass


@pytest.mark.smoke
class TestDecorators(TestCase):

    def setUp(self):
        TestCase.setUp(self)

    def test_configuration(self):

        def new_configuration_settings_class(setting_name=None, setting_value=None):

            @Configuration(**{} if setting_name is None else {setting_name: setting_value})
            class ConfiguredSearchCommand(SearchCommand):
                class ConfigurationSettings(SearchCommand.ConfigurationSettings):
                    clear_required_fields = ConfigurationSetting()
                    distributed = ConfigurationSetting()
                    generates_timeorder = ConfigurationSetting()
                    generating = ConfigurationSetting()
                    maxinputs = ConfigurationSetting()
                    overrides_timeorder = ConfigurationSetting()
                    required_fields = ConfigurationSetting()
                    requires_preop = ConfigurationSetting()
                    retainsevents = ConfigurationSetting()
                    run_in_preview = ConfigurationSetting()
                    streaming = ConfigurationSetting()
                    streaming_preop = ConfigurationSetting()
                    type = ConfigurationSetting()

                    @classmethod
                    def fix_up(cls, command_class):
                        return

            return ConfiguredSearchCommand.ConfigurationSettings

        for name, values, error_values in (
                ('clear_required_fields',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('distributed',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('generates_timeorder',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('generating',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('maxinputs',
                 (0, 50000, sys.maxsize),
                 (None, -1, sys.maxsize + 1, 'anything other than an int')),
                ('overrides_timeorder',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('required_fields',
                 (['field_1', 'field_2'], set(['field_1', 'field_2']), ('field_1', 'field_2')),
                 (None, 0xdead, {'foo': 1, 'bar': 2})),
                ('requires_preop',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('retainsevents',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('run_in_preview',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('streaming',
                 (True, False),
                 (None, 'anything other than a bool')),
                ('streaming_preop',
                 ('some unicode string', b'some byte string'),
                 (None, 0xdead)),
                ('type',
                 # TODO: Do we need to validate byte versions of these strings?
                 ('events', 'reporting', 'streaming'),
                 ('eventing', 0xdead))):

            for value in values:
                settings_class = new_configuration_settings_class(name, value)

                # Setting property exists
                self.assertIsInstance(getattr(settings_class, name), property)

                # Backing field exists on the settings class and it holds the correct value
                backing_field_name = '_' + name
                self.assertEqual(getattr(settings_class, backing_field_name), value)

                settings_instance = settings_class(command=None)

                # An instance gets its value from the settings class until a value is set on the instance

                self.assertNotIn(backing_field_name, settings_instance.__dict__)
                self.assertEqual(getattr(settings_instance, name), value)
                self.assertEqual(getattr(settings_instance, backing_field_name), value)

                setattr(settings_instance, name, value)

                self.assertIn(backing_field_name, settings_instance.__dict__)
                self.assertEqual(getattr(settings_instance, name), value)
                self.assertEqual(settings_instance.__dict__[backing_field_name], value)

            for value in error_values:
                try:
                    new_configuration_settings_class(name, value)
                except Exception as error:
                    self.assertIsInstance(error, ValueError,
                                          f'Expected ValueError, not {type(error).__name__}({error}) for {name}={repr(value)}')
                else:
                    self.fail(f'Expected ValueError, not success for {name}={repr(value)}')

                settings_class = new_configuration_settings_class()
                settings_instance = settings_class(command=None)
                self.assertRaises(ValueError, setattr, settings_instance, name, value)

    def test_new_configuration_setting(self):

        class Test:
            generating = ConfigurationSetting()

            @ConfigurationSetting(name='required_fields')
            def some_name__other_than_required_fields(self):
                pass

            @some_name__other_than_required_fields.setter
            def some_name__other_than_required_fields(self, value):
                pass

            @ConfigurationSetting
            def streaming_preop(self):
                pass

            @streaming_preop.setter
            def streaming_preop(self, value):
                pass

        ConfigurationSetting.fix_up(Test, {})

        test = Test()
        self.assertFalse(hasattr(Test, '_generating'))
        self.assertFalse(hasattr(test, '_generating'))
        self.assertIsNone(test.generating)

        Test._generating = True
        self.assertIs(test.generating, True)

        test.generating = False
        self.assertIs(test.generating, False)
        self.assertIs(Test._generating, True)
        self.assertIs(test._generating, False)

        self.assertRaises(ValueError, Test.generating.fset, test, 'any type other than bool')

    def test_option(self):

        rebase_environment('app_with_logging_configuration')

        presets = [
            'logging_configuration=' + json_encode_string(environment.logging_configuration),
            'logging_level="WARNING"',
            'record="f"',
            'show_configuration="f"']

        command = TestSearchCommand()
        options = command.options

        options.reset()
        missing = options.get_missing()
        self.assertListEqual(missing, [option.name for option in options.values() if option.is_required])
        self.assertListEqual(presets, [str(option) for option in options.values() if option.value is not None])
        self.assertListEqual(presets, [str(option) for option in options.values() if str(option) != option.name + '=None'])

        test_option_values = {
            validators.Boolean: ('0', 'non-boolean value'),
            validators.Code: ('foo == "bar"', 'bad code'),
            validators.Duration: ('24:59:59', 'non-duration value'),
            validators.Fieldname: ('some.field_name', 'non-fieldname value'),
            validators.File: (__file__, 'non-existent file'),
            validators.Integer: ('100', 'non-integer value'),
            validators.Float: ('99.9', 'non-float value'),
            validators.List: ('a,b,c', '"non-list value'),
            validators.Map: ('foo', 'non-existent map entry'),
            validators.Match: ('123-45-6789', 'not a social security number'),
            validators.OptionName: ('some_option_name', 'non-option name value'),
            validators.RegularExpression: ('\\s+', '(poorly formed regular expression'),
            validators.Set: ('bar', 'non-existent set entry')}

        for option in options.values():
            validator = option.validator

            if validator is None:
                self.assertIn(option.name, ['logging_configuration', 'logging_level'])
                continue

            legal_value, illegal_value = test_option_values[type(validator)]
            option.value = legal_value

            self.assertEqual(
                validator.format(option.value), validator.format(validator.__call__(legal_value)),
                f"{option.name}={legal_value}")

            try:
                option.value = illegal_value
            except ValueError:
                pass
            except BaseException as error:
                self.assertFalse(
                    f'Expected ValueError for {option.name}={illegal_value}, not this {type(error).__name__}: {error}')
            else:
                self.assertFalse(f'Expected ValueError for {option.name}={illegal_value}, not a pass.')

        expected = {
            'foo': False,
            'boolean': False,
            'code': 'foo == \"bar\"',
            'duration': 89999,
            'fieldname': 'some.field_name',
            'file': str(repr(__file__)),
            'integer': 100,
            'float': 99.9,
            'logging_configuration': environment.logging_configuration,
            'logging_level': 'WARNING',
            'map': 'foo',
            'match': '123-45-6789',
            'optionname': 'some_option_name',
            'record': False,
            'regularexpression': '\\s+',
            'required_boolean': False,
            'required_code': 'foo == \"bar\"',
            'required_duration': 89999,
            'required_fieldname': 'some.field_name',
            'required_file': str(repr(__file__)),
            'required_integer': 100,
            'required_float': 99.9,
            'required_map': 'foo',
            'required_match': '123-45-6789',
            'required_optionname': 'some_option_name',
            'required_regularexpression': '\\s+',
            'required_set': 'bar',
            'set': 'bar',
            'show_configuration': False,
        }

        self.maxDiff = None

        tuplewrap = lambda x: x if isinstance(x, tuple) else (x,)
        invert = lambda x: {v: k for k, v in x.items()}

        for x in command.options.values():
            # isinstance doesn't work for some reason
            if type(x.value).__name__ == 'Code':
                self.assertEqual(expected[x.name], x.value.source)
            elif type(x.validator).__name__ == 'Map':
                self.assertEqual(expected[x.name], invert(x.validator.membership)[x.value])
            elif type(x.validator).__name__ == 'RegularExpression':
                self.assertEqual(expected[x.name], x.value.pattern)
            elif isinstance(x.value, TextIOWrapper):
                self.assertEqual(expected[x.name], f"'{x.value.name}'")
            elif not isinstance(x.value, (bool,) + (float,) + (str,) + (bytes,) + tuplewrap(int)):
                self.assertEqual(expected[x.name], repr(x.value))
            else:
                self.assertEqual(expected[x.name], x.value)

        expected = (
            'foo="f" boolean="f" code="foo == \\"bar\\"" duration="24:59:59" fieldname="some.field_name" '
            'file=' + json_encode_string(__file__) + ' float="99.9" integer="100" map="foo" match="123-45-6789" '
            'optionname="some_option_name" record="f" regularexpression="\\\\s+" required_boolean="f" '
            'required_code="foo == \\"bar\\"" required_duration="24:59:59" required_fieldname="some.field_name" '
            'required_file=' + json_encode_string(__file__) + ' required_float="99.9" required_integer="100" required_map="foo" '
            'required_match="123-45-6789" required_optionname="some_option_name" required_regularexpression="\\\\s+" '
            'required_set="bar" set="bar" show_configuration="f"')

        observed = str(command.options)

        self.assertEqual(observed, expected)


if __name__ == "__main__":
    main()
