import json
from inspect import getmembers, isfunction, signature

from vr900connector.api import ApiConnector, ApiError, constants, urls

import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Read states of vaillant API')
    parser.add_argument(
        'username',
        help='username')
    parser.add_argument(
        'password',
        help='password')
    parser.add_argument(
        '-fp', '--file-path',
        help='File path to store cookie and serial number in',
        default=constants.DEFAULT_FILES_PATH,
        dest='file_path')
    parser.add_argument('method', help='HTTP method')

    commands_parser = parser.add_subparsers(
        help='commands',
        dest='command')

    functions_list = [member for member in getmembers(urls) if isfunction(member[1])]

    for function in functions_list:
        function_parser = commands_parser.add_parser(
            function[0],
            help=function[0])

        for item in signature(function[1]).parameters.items():
            function_parser.add_argument(item[0], help=item[0])

    args = parser.parse_args()

    connector = ApiConnector(args.username, args.password, constants.DEFAULT_SMART_PHONE_ID, args.file_path)

    try:
        url = _get_url(args)
        result = connector.query(url, args.method)
        print(json.dumps(result, indent=4))
    except ApiError as e:
        print(e.response.text)


def _get_url(args):
    function = getattr(urls, args.command)
    arg_names = _get_args_name(function)

    arg_values = []
    parsed = vars(args)
    for name in arg_names:
        arg_values.append(parsed[name])

    f_kwargs = dict(zip(arg_names, arg_values))
    return function(**f_kwargs)


def _get_args_name(function):
    names = []
    for item in signature(function).parameters.items():
        names.append(item[0])
    return names


if __name__ == "__main__":
    main()
