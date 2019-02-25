import json
import os
import shutil
import sys
import tempfile
import traceback
import uuid
from argparse import ArgumentParser, RawDescriptionHelpFormatter


sys.path.insert(0, '../')

from vr900connector.api import ApiConnector, ApiError, urls


def print_responses(user, password, result_dir):
    # connector = ApiConnector(user, password, file_path=tempfile.gettempdir() + "/" + str(uuid.uuid4()))
    connector = ApiConnector(user, password)

    shutil.rmtree(result_dir, ignore_errors=True)
    os.mkdir(result_dir)

    with open(result_dir + '/facilities', 'w+') as file:
        __secure_call(connector, urls.facilities_list(), file)

    with open(result_dir + '/rooms', 'w+') as file:
        __secure_call(connector, urls.rooms(), file)

    with open(result_dir + '/system_status', 'w+') as file:
        __secure_call(connector, urls.system_status(), file)

    with open(result_dir + '/live_report', 'w+') as file:
        __secure_call(connector, urls.live_report(), file)

    with open(result_dir + '/system_control', 'w+') as file:
        __secure_call(connector, urls.system(), file)

    with open(result_dir + '/hvac_state', 'w+') as file:
        __secure_call(connector, urls.hvac(), file)

    with open(result_dir + '/current_pv_metering', 'w+') as file:
        __secure_call(connector, urls.photovoltaics(), file)

    with open(result_dir + '/emf', 'w+') as file:
        __secure_call(connector, urls.emf_report(), file)

    with open(result_dir + '/repeaters', 'w+') as file:
        __secure_call(connector, urls.repeaters(), file)

    connector.logout()


def __secure_call(connector, url, file):
    try:
        file.write(json.dumps(connector.get(url), indent=4))
    except ApiError as e:
        if e.response is not None:
            file.write(e.response.text)
        else:
            file.write(e.message + '\n')
            traceback.print_exc(file=file)
    except Exception as e:
        traceback.print_exc(file=file)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument('--username', '-u', help='Username used to connect', dest='username',
                        required=True)
    parser.add_argument('--password', '-p', help='Password used to connect', dest='password',
                        required=True)
    parser.add_argument('--dir', '-d', help='Where to store files', dest='dir',
                        required=True)

    args = parser.parse_args()
    print_responses(args.username, args.password, args.dir)
