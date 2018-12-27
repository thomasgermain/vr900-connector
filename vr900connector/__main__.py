import json
import inspect

from vr900connector.api import ApiConnector, ApiError, Defaults, Urls

import argparse

_IGNORE_LIST = ['new_token', 'authenticate', 'logout']


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
        default=Defaults.FILES_PATH,
        dest='file_path')
    parser.add_argument('method', help='HTTP method')

    commands_parser = parser.add_subparsers(
        help='commands',
        dest='command')

    functions_list = inspect.getmembers(Urls, predicate=inspect.ismethod)

    for function in functions_list:
        if not function[0] in _IGNORE_LIST:
            function_parser = commands_parser.add_parser(
                function[0],
                help=function[1].__doc__.strip())

            for item in inspect.signature(function[1]).parameters.items():
                function_parser.add_argument(item[0], help=item[0])

    args = parser.parse_args()

    connector = ApiConnector(args.username, args.password, Defaults.SMART_PHONE_ID, args.file_path)

    try:
        url = _get_url(args)
        result = connector.query(url, args.method)
        print(json.dumps(result, indent=4))
    except ApiError as e:
        print('Error from {}: {}'.format(e.response.url, e.response.text))


def _get_url(args):
    function = getattr(Urls, args.command)
    arg_names = _get_args_name(function)

    arg_values = []
    parsed = vars(args)
    for name in arg_names:
        arg_values.append(parsed[name])

    f_kwargs = dict(zip(arg_names, arg_values))
    return function(**f_kwargs)


def _get_args_name(function):
    names = []
    for item in inspect.signature(function).parameters.items():
        names.append(item[0])
    return names


if __name__ == "__main__":
    main()
