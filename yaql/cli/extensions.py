#    Copyright (c) 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import os
import types
import yaql

from json import JSONDecoder
from yaql.context import ContextAware, Context
from yaql.exceptions import YaqlParsingException, YaqlException

PROMPT = "yaql> "


@ContextAware()
def main(context):
    print "Yet Another Query Language - command-line query tool"
    print "Copyright (c) 2013 Mirantis, Inc"
    print
    if not context.get_data():
        print "No data loaded into context "
        print "Type '@load data-file.json' to load data"
        print
    comm = True
    while comm != 'exit':
        try:
            comm = raw_input(PROMPT)
        except EOFError:
            return
        if comm[0] == '@':
            funcName, args = parse_service_command(comm)
            if funcName not in SERVICE_FUNCTIONS:
                print "Unknown command " + funcName
            else:
                SERVICE_FUNCTIONS[funcName](args, context)
            continue
        try:
            expr = yaql.parse(comm)
        except YaqlParsingException as ex:
            if ex.position:
                pointer_string = (" " * (ex.position + len(PROMPT))) + '^'
                print pointer_string
            print ex.message
            continue
        try:
            res = expr.evaluate(context=Context(context))
            if isinstance(res, types.GeneratorType):
                res = list(res)
            print json.dumps(res, indent=4)
        except StandardError as ex:
            print "Execution exception:"
            if hasattr(ex, 'message'):
                print ex.message
            else:
                print "Unknown"


def load_data(data_file, context):
    try:
        json_str = open(os.path.expanduser(data_file)).read()
    except IOError as e:
        print "Unable to read data file '{0}': {1}".format(data_file,
                                                           e.strerror)
        return
    try:
        decoder = JSONDecoder()
        data = decoder.decode(json_str)
    except Exception as e:
        print "Unable to parse data: " + e.message
        return
    context.set_data(data)
    print "Data from file '{0}' loaded into context".format(data_file)


def register_in_context(context):
    context.register_function(main, '__main')


def parse_service_command(comm):
    space_index = comm.find(' ')
    if space_index == -1:
        return comm, None
    func_name = comm[:space_index]
    args = comm[len(func_name) + 1:]
    return func_name, args


SERVICE_FUNCTIONS = {
    # '@help':print_help,
    '@load': load_data,
    # '@import':import_module,
    # '@register':register_function
}
