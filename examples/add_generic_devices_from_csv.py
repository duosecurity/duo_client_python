#!/usr/bin/python
import duo_client
import argparse
import csv


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--infile',
        required=True,
        help='The path to the input CSV file.'
    )
    parser.add_argument(
        '--device_id_column',
        default='device_id',
        help='The name of the column in the csv file that has the device ID',
    )
    parser.add_argument(
        '--mkey',
        required=len(MKEY_CREDENTIALS.keys())>1,
        help='The Duo Device API managment key: ',
        choices=MKEY_CREDENTIALS.keys()
    )
    parser.add_argument(
        '--ikey',
        required=len(MKEY_CREDENTIALS.keys())>1,
        help='The Duo Device API integration key: ',
        choices=MKEY_CREDENTIALS.keys()
    )
    parser.add_argument(
        '--skey',
        required=len(MKEY_CREDENTIALS.keys())>1,
        help='The Duo Device API secret key: ',
        choices=MKEY_CREDENTIALS.keys()
    )
    parser.add_argument(
        '--host',
        required=len(MKEY_CREDENTIALS.keys())>1,
        help='The Duo Device API hostname ("api-....duosecurity.com"): ',
        choices=MKEY_CREDENTIALS.keys()
    )
    return parser


def upload_identifiers(device_api, csvfile, device_id_column):
    device_ids = []
    with open(args.infile) as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True)
        for row in reader:
            if row[device_id_column]:
                device_ids.append({'device_id': row[device_id_column]})
    if not len(device_ids):
        raise ValueError(
            f'No device IDs read from input column: {device_id_column}')
    self.device_api.activate_cache_with_devices(device_ids)


def main():
    parser = arg_parser()
    args = parser.parse_args()
    device_api = duo_client.client.Client(
        ikey=args.ikey,
        skey=args.skey,
        host=args.host,
        mkey=args.mkey
    )
    upload_identifiers(device_api, args.infile, args.device_id_column)
