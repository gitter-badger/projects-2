#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

try:
    import mock
except ImportError:
    from unittest import mock

try:
    import __builtin__
    builtin_module = '__builtin__'
except ImportError:
    builtin_module = 'builtins'

from projects import projectfile


class FileLoading(TestCase):

    def test__load_method_called_with_the_right_path(self):
        dummy_path = '/dummy/path'
        with mock.patch(builtin_module+'.open') as mock_open:
            projectfile._load(dummy_path)
            mock_open.assert_called_with(dummy_path, 'r')

    def test__load_method_returns_the_loaded_file_content_as_a_list_of_string(self):
        mock_open = mock.mock_open(read_data='line 1\nline 2')
        expected = ['line 1', 'line 2']
        with mock.patch(builtin_module+'.open', mock_open):
            result = projectfile._load('...')
            self.assertEqual(expected, result)


class AdditionalHelperFunctions(TestCase):

    def test__get_currently_parseable_command(self):
        data = {
            'commands': {
                'current-command': {
                    'done': False
                },
                'finished-command': {
                    'done': True
                }
            }
        }
        expected = data['commands']['current-command']
        result = projectfile._get_current_command(data)
        self.assertEqual(expected, result)

    def test__no_returnable_command_found__returns_none(self):
        data = {
            'commands': {
                'current-command': {
                    'done': True
                },
                'finished-command': {
                    'done': True
                }
            }
        }
        expected = None
        result = projectfile._get_current_command(data)
        self.assertEqual(expected, result)


class VersionParser(TestCase):

    def test__valid_version_can_be_parsed_1(self):
        line = 'from v1.2.3'
        expected = (1, 2, 3)
        result = projectfile._parse_version(line)
        self.assertEqual(expected, result)

    def test__valid_version_can_be_parsed_2(self):
        line = 'from 1.2.3'
        expected = (1, 2, 3)
        result = projectfile._parse_version(line)
        self.assertEqual(expected, result)

    def test__valid_version_can_be_parsed_3(self):
        line = 'from           v1.2.3    '
        expected = (1, 2, 3)
        result = projectfile._parse_version(line)
        self.assertEqual(expected, result)

    def test__valid_version_can_be_parsed_4(self):
        line = 'from v123456789.23456789.3456789'
        expected = (123456789, 23456789, 3456789)
        result = projectfile._parse_version(line)
        self.assertEqual(expected, result)

    def test__invalid_version__raise_exception_1(self):
        line = ' from v1.2.3'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_version(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_version__raise_exception_2(self):
        line = '       from v1.2.3'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_version(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_version__raise_exception_3(self):
        line = '\t\tfrom v1.2.3'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_version(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_version__raise_exception_4(self):
        line = 'from v1.2'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_version(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_FORMAT_ERROR == cm.exception.args[0])

    def test__invalid_version__raise_exception_5(self):
        line = 'from v1.2_4'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_version(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_FORMAT_ERROR == cm.exception.args[0])

    def test__not_version_related_input__returns_none(self):
        line = 'something'
        expected = None
        result = projectfile._parse_version(line)
        self.assertEqual(expected, result)


class EmptyLineParser(TestCase):

    def test__parse_empty_line_1(self):
        line = ''
        expected = True
        result = projectfile._parse_empty_line(line)
        self.assertEqual(expected, result)

    def test__parse_empty_line_2(self):
        line = ' '
        expected = True
        result = projectfile._parse_empty_line(line)
        self.assertEqual(expected, result)

    def test__parse_empty_line_3(self):
        line = '\t'
        expected = True
        result = projectfile._parse_empty_line(line)
        self.assertEqual(expected, result)

    def test__parse_empty_line_4(self):
        line = 'valami'
        expected = False
        result = projectfile._parse_empty_line(line)
        self.assertEqual(expected, result)

    def test__parse_empty_line_5(self):
        line = '  valami'
        expected = False
        result = projectfile._parse_empty_line(line)
        self.assertEqual(expected, result)


class IndentedLineParser(TestCase):

    def test__parse_indented_line_1(self):
        line = ' valami'
        expected = 'valami'
        result = projectfile._parse_indented_line(line)
        self.assertEqual(expected, result)

    def test__parse_indented_line_2(self):
        line = '           valami'
        expected = 'valami'
        result = projectfile._parse_indented_line(line)
        self.assertEqual(expected, result)

    def test__parse_indented_line_3(self):
        line = ' valami valamik    '
        expected = 'valami valamik'
        result = projectfile._parse_indented_line(line)
        self.assertEqual(expected, result)

    def test__parse_indented_line_4(self):
        line = 'valami'
        expected = None
        result = projectfile._parse_indented_line(line)
        self.assertEqual(expected, result)


class CommentDelimiterParser(TestCase):

    def test__delimiter_can_be_parsed__zero_indentation(self):
        line = '"""'
        expected = True
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__delimiter_can_be_parsed__one_indentation(self):
        line = ' """'
        expected = True
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__delimiter_can_be_parsed__one_indentation_with_tab(self):
        line = '\t"""'
        expected = True
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__delimiter_can_be_parsed__two_indentations(self):
        line = '  """'
        expected = True
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__delimiter_can_be_parsed__two_indentations__tailing_indentations_ignored(self):
        line = '  """                    \t\t\t   '
        expected = True
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__invalid_delimiter_returns_negative_number_1(self):
        line = '""'
        expected = False
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)

    def test__invalid_delimiter_returns_negative_number_2(self):
        line = '" ""'
        expected = False
        result = projectfile._parse_comment_delimiter(line)
        self.assertEqual(expected, result)


class LineParser(TestCase):

    def test__line_can_be_parsed_1(self):
        line = 'valami'
        expected = 'valami'
        result = projectfile._parse_line(line)
        self.assertEqual(expected, result)

    def test__line_can_be_parsed_2(self):
        line = ' valami'
        expected = 'valami'
        result = projectfile._parse_line(line)
        self.assertEqual(expected, result)

    def test__line_can_be_parsed_3(self):
        line = '   valami    '
        expected = 'valami'
        result = projectfile._parse_line(line)
        self.assertEqual(expected, result)

    def test__line_can_be_parsed_4(self):
        line = '\t\tvalami    '
        expected = 'valami'
        result = projectfile._parse_line(line)
        self.assertEqual(expected, result)

    def test__line_can_be_parsed_5(self):
        line = ' valami valami    '
        expected = 'valami valami'
        result = projectfile._parse_line(line)
        self.assertEqual(expected, result)


class VariableParser(TestCase):

    def test__variable_can_be_parsed__basic_case(self):
        line = 'my_variable = valami'
        expected = {'my_variable': 'valami'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__more_whitespaces(self):
        line = 'my_variable   =   valami'
        expected = {'my_variable': 'valami'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__no_whitespace(self):
        line = 'my_variable=valami'
        expected = {'my_variable': 'valami'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__full_range_variable_name(self):
        line = '1234567890.abc-abc = valami'
        expected = {'1234567890.abc-abc': 'valami'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__whitespace_inside_value(self):
        line = 'my_variable = valami vmi'
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__whitespace_inside_value_and_after_value(self):
        line = 'my_variable = valami vmi     '
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__double_quoted_value(self):
        line = 'my_variable = "valami vmi"'
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__double_quoted_value_tailing_whitespace(self):
        line = 'my_variable = "valami vmi"     '
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__double_quoted_value_with_escaped_double_quote(self):
        line = 'my_variable = "valami\\"vmi"'
        expected = {'my_variable': 'valami"vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__double_quoted_value_with_escaped_quote(self):
        line = 'my_variable = "valami\\\'vmi"'
        expected = {'my_variable': 'valami\'vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__quoted_value(self):
        line = 'my_variable = \'valami vmi\''
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__quoted_value_tailing_whitespace(self):
        line = 'my_variable = \'valami vmi\'     '
        expected = {'my_variable': 'valami vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__quoted_value_with_escaped_double_quote(self):
        line = 'my_variable = \'valami\\"vmi\''
        expected = {'my_variable': 'valami"vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__variable_can_be_parsed__quoted_value_with_escaped_quote(self):
        line = 'my_variable = \'valami\\\'vmi\''
        expected = {'my_variable': 'valami\'vmi'}
        result = projectfile._parse_variable(line)
        self.assertEqual(expected, result)

    def test__invalid_variable__indentation_should_raise_exception__basic_case(self):
        line = ' my_variable = valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_variable__indentation_should_raise_exception__more_whitespaces(self):
        line = '         my_variable = valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_variable__indentation_should_raise_exception__tabs(self):
        line = '\t\tmy_variable = valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_full_range_variable__indentation_should_raise_exception(self):
        line = ' 1234567890.abc-abc = valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_variable__should_raise_exception__unmatched_quote_1(self):
        line = 'my_variable = \'valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_QUOTE_AFTER_ERROR == cm.exception.args[0])

    def test__invalid_variable__should_raise_exception__unmatched_quote_2(self):
        line = 'my_variable = valami\''
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_QUOTE_BEFORE_ERROR == cm.exception.args[0])

    def test__invalid_variable__should_raise_exception__unmatched_double_quote_1(self):
        line = 'my_variable = "valami'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_QUOTE_AFTER_ERROR == cm.exception.args[0])

    def test__invalid_variable__should_raise_exception__unmatched_double_quote_2(self):
        line = 'my_variable = valami"'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_variable(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_QUOTE_BEFORE_ERROR == cm.exception.args[0])


class CommandDivisorParser(TestCase):

    def test__command_divisor_can_be_parsed_1(self):
        line = '==='
        expected = True
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_2(self):
        line = ' ==='
        expected = True
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_3(self):
        line = ' ===      '
        expected = True
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_4(self):
        line = '\t==='
        expected = True
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_5(self):
        line = '=='
        expected = False
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_6(self):
        line = '='
        expected = False
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)

    def test__command_divisor_can_be_parsed_7(self):
        line = '= =='
        expected = False
        result = projectfile._parse_command_divisor(line)
        self.assertEqual(expected, result)


class CommandHeaderParser(TestCase):

    def test__valid_command_header__basic_case(self):
        line = 'command:'
        expected = {
            'command': {
                'done': False
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__command_name_full_range(self):
        line = 'command_COMMAND_1234567890.abc-abc:'
        expected = {
            'command_COMMAND_1234567890.abc-abc': {
                'done': False
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__extra_space_after_colon(self):
        line = 'command:   '
        expected = {
            'command': {
                'done': False
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__extra_space_before_colon(self):
        line = 'command  :'
        expected = {
            'command': {
                'done': False
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__two_alternative_commands(self):
        line = 'command|com:'
        expected = {
            'command': {
                'done': False
            },
            'com': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__three_alternative_commands(self):
        line = 'command|com|c:'
        expected = {
            'command': {
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__alternatives_with_space(self):
        line = 'command |  com    | c    :'
        expected = {
            'command': {
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__dependencies(self):
        line = 'command|com|c: [dep]'
        expected = {
            'command': {
                'dependencies': ['dep'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__multiple_dependencies(self):
        line = 'command|com|c: [dep, dep2, dep3]'
        expected = {
            'command': {
                'dependencies': ['dep', 'dep2', 'dep3'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__full_range_dependencies(self):
        line = 'command|com|c: [command_COMMAND_1234567890.abc-abc]'
        expected = {
            'command': {
                'dependencies': ['command_COMMAND_1234567890.abc-abc'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__dependencies_with_no_whitespaces(self):
        line = 'command|com|c:[dep]'
        expected = {
            'command': {
                'dependencies': ['dep'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__dependencies_with_more_outside_whitespaces(self):
        line = 'command|com|c:    [dep]          '
        expected = {
            'command': {
                'dependencies': ['dep'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__dependencies_with_more_inside_whitespaces(self):
        line = 'command|com|c: [ dep    ]'
        expected = {
            'command': {
                'dependencies': ['dep'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__valid_command_header__multiple_dependencies_with_more_inside_whitespaces(self):
        line = 'command|com|c: [ dep  ,               dep1  ]'
        expected = {
            'command': {
                'dependencies': ['dep', 'dep1'],
                'done': False
            },
            'com': {
                'alias': 'command'
            },
            'c': {
                'alias': 'command'
            }
        }
        result = projectfile._parse_command_header(line)
        self.assertEqual(expected, result)

    def test__invalid_command_header__raises_exception__indentation_1(self):
        line = ' command:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__indentation_2(self):
        line = '     command:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__indentation_3(self):
        line = '\tcommand:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__indentation_4(self):
        line = ' command'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_SYNTAX_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__no_colon_1(self):
        line = 'command'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_MISSING_COLON_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__no_colon_2(self):
        line = 'command|'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_MISSING_COLON_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__no_colon_3(self):
        line = 'command   [deb]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_MISSING_COLON_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_colon_syntax_1(self):
        line = 'command:c'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_COLON_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_colon_syntax_2(self):
        line = ':command'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_COLON_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_alternative_list_1(self):
        line = 'command|:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_ALTERNATIVE == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_alternative_list_2(self):
        line = '|command:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_ALTERNATIVE == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_alternative_list_3(self):
        line = '|command|:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_ALTERNATIVE == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_alternative_list_4(self):
        line = 'command||:'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_ALTERNATIVE == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_1(self):
        line = 'command: []'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_EMPTY_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_2(self):
        line = 'command: ['
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_3(self):
        line = 'command: ]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_4(self):
        line = 'command: [,]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_5(self):
        line = 'command: [ ,]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_6(self):
        line = 'command: [ ,  ]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_7(self):
        line = 'command: [dep1, , dep2]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])

    def test__invalid_command_header__raises_exception__wrong_dependency_list_8(self):
        line = 'command: [dep1,,dep2]'
        with self.assertRaises(Exception) as cm:
            projectfile._parse_command_header(line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INVALID_DEPENDENCY_LIST == cm.exception.args[0])


class StartState(TestCase):

    def test__can_parse_version(self):
        data = {}
        line = 'from v1.2.3'
        expected = {'min-version': (1, 2, 3)}
        expected_state = projectfile._state_before_commands
        next_state = projectfile._state_start(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_tolerate_empty_lines(self):
        data = {}
        line1 = ''
        line2 = 'from v1.2.3'

        expected1 = {}
        expected2 = {'min-version': (1, 2, 3)}
        expected_state1 = projectfile._state_start
        expected_state2 = projectfile._state_before_commands

        next_state1 = projectfile._state_start(data, line1)
        self.assertEqual(expected1, data)
        self.assertEqual(expected_state1, next_state1)

        next_state2 = projectfile._state_start(data, line2)
        self.assertEqual(expected2, data)
        self.assertEqual(expected_state2, next_state2)

    def test__cannot_tolerate_anything_else(self):
        data = {}
        line = 'valami'
        with self.assertRaises(Exception) as cm:
            projectfile._state_start(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_MISSING_ERROR == cm.exception.args[0])

    def test__raise_error_on_invalid_version(self):
        data = {}
        line = 'from v.1'
        with self.assertRaises(Exception) as cm:
            projectfile._state_start(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VERSION_FORMAT_ERROR == cm.exception.args[0])


class BeforeCommandsState(TestCase):

    def test__can_tolerate_empty_lines(self):
        data = {}
        line = ''
        expected = {}
        expected_state = projectfile._state_before_commands
        next_state = projectfile._state_before_commands(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_parse_comments(self):
        data = {}
        line = '"""'
        expected = {'description': ''}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_before_commands(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_parse_variables(self):
        data = {}
        line = 'some_variable = 42'
        expected = {'variables': {'some_variable': '42'}}
        expected_state = projectfile._state_variables
        next_state = projectfile._state_before_commands(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_parse_command_header(self):
        data = {}
        line = 'my_command:'
        expected = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command
        next_state = projectfile._state_before_commands(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__invalid_variable__raises_error(self):
        data = {}
        line = '  invalid_variable=4'
        with self.assertRaises(Exception) as cm:
            projectfile._state_before_commands(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_INDENTATION_ERROR == cm.exception.args[0])

    def test__invalid_command_header__raises_error(self):
        data = {}
        line = '  invalid_command|:'
        with self.assertRaises(Exception) as cm:
            projectfile._state_before_commands(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_INDENTATION_ERROR == cm.exception.args[0])

    def test__indented_line_raises_error(self):
        data = {}
        line = '  indented line'
        with self.assertRaises(Exception) as cm:
            projectfile._state_before_commands(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_SYNTAX_ERROR == cm.exception.args[0])


class MainCommentState(TestCase):

    def test__first_comment_line_added_right(self):
        data = {}
        line = 'This is the first line for the main comment..'
        expected = {'description': line}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__another_line_appended_with_a_space_to_the_existing_ones(self):
        data = {'description': 'Some text.'}
        line = 'This should be appended..'
        expected = {'description': 'Some text. This should be appended..'}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__extra_whitespaces_will_be_ignored(self):
        data = {'description': 'Some text.'}
        line = '         \t\tThis should be appended..    \t   '
        expected = {'description': 'Some text. This should be appended..'}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__empty_line_acts_as_a_separator__appends_two_lines_to_the_end(self):
        data = {'description': 'Some text.'}
        line = ''
        expected = {'description': 'Some text.\n\n'}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__second_empty_line_does_not_add_more_seaprators(self):
        data = {'description': 'Some text.\n\n'}
        line = ''
        expected = {'description': 'Some text.\n\n'}
        expected_state = projectfile._state_main_comment
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__comment_delimiter_ends_the_comment_capturing(self):
        data = {'description': 'Some text.\n\n'}
        line = '"""'
        expected = {'description': 'Some text.\n\n'}
        expected_state = projectfile._state_variables
        next_state = projectfile._state_main_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)


class VariableState(TestCase):

    def test__no_variable_parsed_yet__create_the_variable_key(self):
        data = {}
        line = 'my-variable = 42'
        expected = {'variables': {'my-variable': '42'}}
        expected_state = projectfile._state_variables
        next_state = projectfile._state_variables(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__next_variable_is_added_to_the_dictionary(self):
        data = {'variables': {
            'first-variable': '42'
        }}
        line = 'second-variable = 23'
        expected = {'variables': {
            'first-variable': '42',
            'second-variable': '23'
        }}
        expected_state = projectfile._state_variables
        next_state = projectfile._state_variables(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_tolerate_empty_lines(self):
        data = {'variables': {
            'first-variable': '42'
        }}
        line = ''
        expected = {'variables': {
            'first-variable': '42'
        }}
        expected_state = projectfile._state_variables
        next_state = projectfile._state_variables(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__invalid_variable_syntax__raises_exception(self):
        data = {'variables': {
            'first-variable': '42'
        }}
        line = 'second-variable = \'23'
        with self.assertRaises(Exception) as cm:
            projectfile._state_variables(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._VARIABLE_QUOTE_AFTER_ERROR == cm.exception.args[0])

    def test__non_variable__raises_invalid_command_header_exception(self):
        # command headers are in higher priority than variables
        data = {'variables': {
            'first-variable': '42'
        }}
        line = ' non-variable'
        with self.assertRaises(Exception) as cm:
            projectfile._state_variables(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_SYNTAX_ERROR == cm.exception.args[0])

    def test__comment_delimiter__raises_exception(self):
        data = {'variables': {
            'first-variable': '42'
        }}
        line = '"""'
        with self.assertRaises(Exception) as cm:
            projectfile._state_variables(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMENT_DELIMITER_UNEXPECTED_ERROR == cm.exception.args[0])

    def test__valid_command_header_switches_state(self):
        data = {'variables': {
            'first-variable': '42'
        }}
        line = 'my_command:'
        expected = {
            'variables': {
                'first-variable': '42'
            },
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command
        next_state = projectfile._state_variables(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)


class CommandState(TestCase):

    def test__can_tolerate_empty_line(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = ''
        expected = dict(data)
        expected_state = projectfile._state_command
        next_state = projectfile._state_command(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__can_parse_comment_delimiter(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = '"""'
        expected = dict(data)
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__indented_line__will_be_the_first_pre_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = '  cd ~ '
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': [
                        'cd ~'
                    ]
                }
            }
        }
        expected_state = projectfile._state_pre
        next_state = projectfile._state_command(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__command_separator_switches_right_to_post(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = '  ==='
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': [],
                    'post': []
                }
            }
        }
        expected_state = projectfile._state_post
        next_state = projectfile._state_command(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__nonindented_line__raises_exception(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = 'something'
        with self.assertRaises(Exception) as cm:
            projectfile._state_command(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_UNEXPECTED_UNINDENTED_ERROR == cm.exception.args[0])


class CommandCommentState(TestCase):

    def test__first_comment_line_added_right(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False
                }
            }
        }
        line = 'This is the first line for the main comment..'
        expected = {
            'commands': {
                'my_command': {
                    'description': 'This is the first line for the main comment..',
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__another_line_appended_with_a_space_to_the_existing_ones(self):
        data = {
            'commands': {
                'my_command': {
                    'description': 'Some text..',
                    'done': False
                }
            }
        }
        line = 'This should be appended..'
        expected = {
            'commands': {
                'my_command': {
                    'description': 'Some text.. This should be appended..',
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__extra_whitespaces_will_be_ignored(self):
        data = {
            'commands': {
                'my_command': {
                    'description': 'Some text..',
                    'done': False
                }
            }
        }
        line = '         \t\tThis should be appended..    \t   '
        expected = {
            'commands': {
                'my_command': {
                    'description': 'Some text.. This should be appended..',
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__empty_line_acts_as_a_separator__appends_two_lines_to_the_end(self):
        data = {
            'commands': {
                'my_command': {
                    'description': 'Some text.',
                    'done': False
                }
            }
        }
        line = ''
        expected = {
            'commands': {
                'my_command': {
                    'description': 'Some text.\n\n',
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__second_empty_line_does_not_add_more_seaprators(self):
        data = {
            'commands': {
                'my_command': {
                    'description': 'Some text.\n\n',
                    'done': False
                }
            }
        }
        line = ''
        expected = {
            'commands': {
                'my_command': {
                    'description': 'Some text.\n\n',
                    'done': False
                }
            }
        }
        expected_state = projectfile._state_command_comment
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__comment_delimiter_ends_the_comment_capturing(self):
        data = {
            'commands': {
                'my_command': {
                    'description': 'Some text.\n\n',
                    'done': False
                }
            }
        }
        line = '"""'
        expected = {
            'commands': {
                'my_command': {
                    'description': 'Some text.\n\n',
                    'done': False,
                    'pre': []
                }
            }
        }
        expected_state = projectfile._state_pre
        next_state = projectfile._state_command_comment(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

class PreState(TestCase):

    def test__can_tolerate_empty_lines(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': []
                }
            }
        }
        line = ''
        expected = dict(data)
        expected_state = projectfile._state_pre
        next_state = projectfile._state_pre(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__indented_line_processed_as_a_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': []
                }
            }
        }
        line = '  some indented command'
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['some indented command']
                }
            }
        }
        expected_state = projectfile._state_pre
        next_state = projectfile._state_pre(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__parsed_command_appended_to_the_pre_list(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['previous command']
                }
            }
        }
        line = '  some indented command'
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': [
                        'previous command',
                        'some indented command'
                        ]
                }
            }
        }
        expected_state = projectfile._state_pre
        next_state = projectfile._state_pre(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__command_divisor_switches_state(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['previous command']
                }
            }
        }
        line = '  ==='
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['previous command'],
                    'post': []
                }
            }
        }
        expected_state = projectfile._state_post
        next_state = projectfile._state_pre(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__valid_command_header_finishes_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['previous command']
                }
            }
        }
        line = 'next_command:'
        expected = {
            'commands': {
                'my_command': {
                    'done': True,
                    'pre': ['previous command']
                },
                'next_command': {
                    'done': False,
                }
            }
        }
        expected_state = projectfile._state_command
        next_state = projectfile._state_pre(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__valid_command_header_finishes_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': ['previous command']
                }
            }
        }
        line = 'next_command|'
        with self.assertRaises(Exception) as cm:
            projectfile._state_pre(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_MISSING_COLON_ERROR == cm.exception.args[0])


class PostState(TestCase):

    def test__can_tolerate_empty_lines(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'pre': []
                }
            }
        }
        line = ''
        expected = dict(data)
        expected_state = projectfile._state_post
        next_state = projectfile._state_post(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__indented_line_processed_as_a_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': []
                }
            }
        }
        line = '  some indented command'
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': ['some indented command']
                }
            }
        }
        expected_state = projectfile._state_post
        next_state = projectfile._state_post(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__parsed_command_appended_to_the_post_list(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': ['previous command']
                }
            }
        }
        line = '  some indented command'
        expected = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': [
                        'previous command',
                        'some indented command'
                        ]
                }
            }
        }
        expected_state = projectfile._state_post
        next_state = projectfile._state_post(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__command_divisor__raises_error(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': ['previous command']
                }
            }
        }
        line = '==='
        with self.assertRaises(Exception) as cm:
            projectfile._state_post(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_DELIMITER_UNEXPECTED_ERROR == cm.exception.args[0])

    def test__valid_command_header_finishes_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': ['previous command']
                }
            }
        }
        line = 'next_command:'
        expected = {
            'commands': {
                'my_command': {
                    'done': True,
                    'post': ['previous command']
                },
                'next_command': {
                    'done': False,
                }
            }
        }
        expected_state = projectfile._state_command
        next_state = projectfile._state_post(data, line)
        self.assertEqual(expected, data)
        self.assertEqual(expected_state, next_state)

    def test__valid_command_header_finishes_command(self):
        data = {
            'commands': {
                'my_command': {
                    'done': False,
                    'post': ['previous command']
                }
            }
        }
        line = 'next_command|'
        with self.assertRaises(Exception) as cm:
            projectfile._state_post(data, line)
        self.assertEqual(cm.exception.__class__, SyntaxError)
        self.assertTrue(projectfile._COMMAND_HEADER_MISSING_COLON_ERROR == cm.exception.args[0])

