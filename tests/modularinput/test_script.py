import sys

from splunklib.client import Service
from splunklib.modularinput import Script, EventWriter, Scheme, Argument, Event
import io

from splunklib.modularinput.utils import xml_compare
from tests.modularinput.modularinput_testlib import data_open

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

TEST_SCRIPT_PATH = "__IGNORED_SCRIPT_PATH__"


def test_error_on_script_with_null_scheme(capsys):
    """A script that returns a null scheme should generate no output on
    stdout and an error on stderr saying that it the scheme was null."""

    # Override abstract methods
    class NewScript(Script):
        def get_scheme(self):
            return None

        def stream_events(self, inputs, ew):
            # not used
            return

    script = NewScript()

    ew = EventWriter(sys.stdout, sys.stderr)

    in_stream = io.StringIO()

    args = [TEST_SCRIPT_PATH, "--scheme"]
    return_value = script.run_script(args, ew, in_stream)

    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == "FATAL Modular input script returned a null scheme.\n"
    assert 0 != return_value


def test_scheme_properly_generated_by_script(capsys):
    """Check that a scheme generated by a script is what we expect."""

    # Override abstract methods
    class NewScript(Script):
        def get_scheme(self):
            scheme = Scheme("abcd")
            scheme.description = u"\uC3BC and \uC3B6 and <&> f\u00FCr"
            scheme.streaming_mode = scheme.streaming_mode_simple
            scheme.use_external_validation = False
            scheme.use_single_instance = True

            arg1 = Argument("arg1")
            scheme.add_argument(arg1)

            arg2 = Argument("arg2")
            arg2.description = u"\uC3BC and \uC3B6 and <&> f\u00FCr"
            arg2.data_type = Argument.data_type_number
            arg2.required_on_create = True
            arg2.required_on_edit = True
            arg2.validation = "is_pos_int('some_name')"
            scheme.add_argument(arg2)

            return scheme

        def stream_events(self, inputs, ew):
            # not used
            return

    script = NewScript()

    ew = EventWriter(sys.stdout, sys.stderr)

    args = [TEST_SCRIPT_PATH, "--scheme"]
    return_value = script.run_script(args, ew, sys.stderr)

    output = capsys.readouterr()

    assert output.err == ""
    assert return_value == 0

    with data_open("data/scheme_without_defaults.xml") as data:
        found = ET.fromstring(output.out)
        expected = ET.parse(data).getroot()

        assert xml_compare(expected, found)


def test_successful_validation(capsys):
    """Check that successful validation yield no text and a 0 exit value."""

    # Override abstract methods
    class NewScript(Script):
        def get_scheme(self):
            return None

        def validate_input(self, definition):
            # always succeed...
            return

        def stream_events(self, inputs, ew):
            # unused
            return

    script = NewScript()

    ew = EventWriter(sys.stdout, sys.stderr)

    args = [TEST_SCRIPT_PATH, "--validate-arguments"]

    return_value = script.run_script(args, ew, data_open("data/validation.xml"))

    output = capsys.readouterr()

    assert output.err == ""
    assert output.out == ""
    assert return_value == 0


def test_failed_validation(capsys):
    """Check that failed validation writes sensible XML to stdout."""

    # Override abstract methods
    class NewScript(Script):
        def get_scheme(self):
            return None

        def validate_input(self, definition):
            raise ValueError("Big fat validation error!")

        def stream_events(self, inputs, ew):
            # unused
            return

    script = NewScript()

    ew = EventWriter(sys.stdout, sys.stderr)

    args = [TEST_SCRIPT_PATH, "--validate-arguments"]

    return_value = script.run_script(args, ew, data_open("data/validation.xml"))

    output = capsys.readouterr()

    with data_open("data/validation_error.xml") as data:
        expected = ET.parse(data).getroot()
        found = ET.fromstring(output.out)

        assert output.err == ""
        assert xml_compare(expected, found)
        assert return_value != 0


def test_write_events(capsys):
    """Check that passing an input definition and writing a couple events goes smoothly."""

    # Override abstract methods
    class NewScript(Script):
        def get_scheme(self):
            return None

        def stream_events(self, inputs, ew):
            event = Event(
                data="This is a test of the emergency broadcast system.",
                stanza="fubar",
                time="%.3f" % 1372275124.466,
                host="localhost",
                index="main",
                source="hilda",
                sourcetype="misc",
                done=True,
                unbroken=True
            )

            ew.write_event(event)
            ew.write_event(event)

    script = NewScript()
    input_configuration = data_open("data/conf_with_2_inputs.xml")

    ew = EventWriter(sys.stdout, sys.stderr)

    return_value = script.run_script([TEST_SCRIPT_PATH], ew, input_configuration)

    output = capsys.readouterr()
    assert output.err == ""
    assert return_value == 0

    with data_open("data/stream_with_two_events.xml") as data:
        expected = ET.parse(data).getroot()
        found = ET.fromstring(output.out)

        assert xml_compare(expected, found)


def test_service_property(capsys):
    """ Check that Script.service returns a valid Service instance as soon
    as the stream_events method is called, but not before.

    """

    # Override abstract methods
    class NewScript(Script):
        def __init__(self):
            super(NewScript, self).__init__()
            self.authority_uri = None

        def get_scheme(self):
            return None

        def stream_events(self, inputs, ew):
            self.authority_uri = inputs.metadata['server_uri']

    script = NewScript()
    with data_open("data/conf_with_2_inputs.xml") as input_configuration:
        ew = EventWriter(sys.stdout, sys.stderr)

        assert script.service is None

        return_value = script.run_script(
            [TEST_SCRIPT_PATH], ew, input_configuration)

        output = capsys.readouterr()
        assert return_value == 0
        assert output.err == ""
        assert isinstance(script.service, Service)
        assert script.service.authority == script.authority_uri
        # self.test.assertIsInstance(service, Service)
        # self.test.assertEqual(str(service.authority), inputs.metadata['server_uri'])
