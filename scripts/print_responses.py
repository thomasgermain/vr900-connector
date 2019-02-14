import json
import os
import shutil
import sys
import tempfile
import traceback
import uuid
from argparse import ArgumentParser, RawDescriptionHelpFormatter

sys.path.insert(0, '../')

from vr900connector.api import ApiConnector, ApiError, constant


def print_responses(user, password, result_dir):
    connector = ApiConnector(user, password, file_dir=tempfile.gettempdir() + "/" + str(uuid.uuid4()))

    shutil.rmtree(result_dir, ignore_errors=True)
    os.mkdir(result_dir)

    with open(result_dir + '/facilities', 'w+') as file:
        secure_call(connector, constant.FACILITIES_URL, file)

    with open(result_dir + '/rooms', 'w+') as file:
        secure_call(connector, constant.ROOMS_URL, file)

    with open(result_dir + '/system_status', 'w+') as file:
        secure_call(connector, constant.SYSTEM_STATUS_URL, file)

    with open(result_dir + '/live_report', 'w+') as file:
        secure_call(connector, constant.LIVE_REPORT_URL, file)

    with open(result_dir + '/system_control', 'w+') as file:
        secure_call(connector, constant.SYSTEM_CONTROL_URL, file)

    with open(result_dir + '/hvac_state', 'w+') as file:
        secure_call(connector, constant.HVAC_STATE_URL, file)

    with open(result_dir + '/current_pv_metering', 'w+') as file:
        secure_call(connector, constant.CURRENT_PV_METERING_INFO_URL, file)

    with open(result_dir + '/emf', 'w+') as file:
        secure_call(connector, constant.EMF_URL, file)

    with open(result_dir + '/repeaters', 'w+') as file:
        secure_call(connector, constant.REPEATERS_URL, file)

    connector.logout()


def secure_call(connector, url, file):
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
