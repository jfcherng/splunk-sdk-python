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

"""Command line utilities shared by command line tools & unit tests."""

from os import path
from optparse import OptionParser
import sys
from dotenv import dotenv_values

__all__ = [ "error", "Parser", "cmdline" ]

# Print the given message to stderr, and optionally exit
def error(message, exitcode = None):
    print(f"Error: {message}", file=sys.stderr)
    if exitcode is not None: sys.exit(exitcode)


class record(dict):
    def __getattr__(self, name):
        try: 
            return self[name] 
        except KeyError: 
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class Parser(OptionParser):
    def __init__(self, rules = None, **kwargs):
        OptionParser.__init__(self, **kwargs)
        self.dests = set({})
        self.result = record({ 'args': [], 'kwargs': record() })
        if rules is not None: self.init(rules)

    def init(self, rules):
        """Initialize the parser with the given command rules."""
        # Initialize the option parser
        for dest in rules.keys():
            rule = rules[dest]

            # Assign defaults ourselves here, instead of in the option parser
            # itself in order to allow for multiple calls to parse (dont want
            # subsequent calls to override previous values with default vals).
            if 'default' in rule:
                self.result['kwargs'][dest] = rule['default']

            flags = rule['flags']
            kwargs = { 'action': rule.get('action', "store") }
            # NOTE: Don't provision the parser with defaults here, per above.
            for key in ['callback', 'help', 'metavar', 'type']:
                if key in rule: kwargs[key] = rule[key]
            self.add_option(*flags, dest=dest, **kwargs)

            # Remember the dest vars that we see, so that we can merge results
            self.dests.add(dest)

    # Load command options from '.env' file
    def load(self, filepath):
        argv = []
        try:
            filedata = dotenv_values(filepath)
        except:
            error("Unable to open '%s'" % filepath, 2)

        # update result kwargs value with .env file data
        for key, value in filedata.items():
            value = value.strip()
            if len(value) == 0 or value is None: continue  # Skip blank value
            elif key in self.dests:
                self.result['kwargs'][key] = value
            else:
                raise NameError("No such option --" + key)

        return self

    def loadif(self, filepath):
        """Load the given filepath if it exists, otherwise ignore."""
        if path.isfile(filepath): self.load(filepath)
        return self

    def loadenv(self, filename):
        dir_path = path.dirname(path.realpath(__file__))
        filepath = path.join(dir_path, '..', filename)
        self.loadif(filepath)
        return self

    def parse(self, argv):
        """Parse the given argument vector."""
        kwargs, args = self.parse_args(argv)
        self.result['args'] += args
        # Annoying that parse_args doesn't just return a dict
        for dest in self.dests:
            value = getattr(kwargs, dest)
            if value is not None:
                self.result['kwargs'][dest] = value
        return self

    def format_epilog(self, formatter):
        return self.epilog or ""


def cmdline(argv, rules=None, config=None, **kwargs):
    """Simplified cmdopts interface that does not default any parsing rules
       and that does not allow compounding calls to the parser."""
    parser = Parser(rules, **kwargs)
    if config is not None: parser.loadenv(config)
    return parser.parse(argv).result

