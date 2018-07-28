#!/usr/bin/env python3


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180728'
__version__ = '0.01'
__description__ = '''Searches for AWS ImageId based on command line options.'''


import argparse
import datetime
import os
import sys
from pathlib import Path
try:
    import boto3
except ImportError:
    print("[-] This script requires boto3. Try 'pip install boto3', \
or do an Internet search for installation instructions.")


def check_aws_files():
    """Checks for the AWS credentials and config files in the default location."""
    if sys.platform.lower().startswith('win'):
        cred_loc = str(Path.home()) +  '\\.aws\\'
    else:
        cred_loc = str(Path.home()) + '/.aws/'
    if os.path.exists(cred_loc):
        files = os.listdir(cred_loc)
        if 'config' not in files:
            print('[-] Missing config file in {}'.format(cred_loc))
        if 'credentials' not in files:
            print('[-] Missing credential file in {}'.format(cred_loc))
            exit()
    else:
        print('[-] AWS configuration files not found in {}. Exiting.'.format(cred_loc))
        exit()

def get_images(architecture, hypervisor, is_public, owner, name, platform=None):
    """Uses describe_images to return a list of dictionarys of AWS images"""
    ec2 = boto3.client('ec2')
    if platform:
        response = ec2.describe_images(Filters=[
            {'Name': 'platform', 'Values': [platform]},
            {'Name': 'architecture', 'Values': [architecture]},
            {'Name': 'hypervisor', 'Values': [hypervisor]},
            {'Name': 'is-public', 'Values': [is_public]},
            {'Name': 'owner-alias', 'Values': [owner]},
            {'Name': 'name', 'Values': [name]}
        ])
    else:
        response = ec2.describe_images(Filters=[
            {'Name': 'architecture', 'Values': [architecture]},
            {'Name': 'hypervisor', 'Values': [hypervisor]},
            {'Name': 'is-public', 'Values': [is_public]},
            {'Name': 'owner-alias', 'Values': [owner]},
            {'Name': 'name', 'Values': [name]}
        ])
    return response.get('Images')

def main():
    """Retrieves, sorts, and filters AWS images"""

    # Checks to make sure the AWS config and credentials files exist.
    check_aws_files()

    # Gets either just windows images or all images
    if args.windows:
        images = get_images(architecture, hypervisor, is_public, owner_alias, name_filter, 'windows')
    else:
        images = get_images(architecture, hypervisor, is_public, owner_alias, name_filter)

    # sorts the images by creation date, and filters images client side if specified in the options
    if images:
        sorted_images = sorted(images, key=lambda k: k['CreationDate'], reverse=True)
        print('{:15}{:45}{:15}'.format('ImageId', 'ImageLocation', 'CreationDate'))
        for image in sorted_images:
            if image['CreationDate'] < image_age:
                if args.filter:
                    if not args.filter.lower() in image['ImageLocation'].lower():
                        continue
                print('{:15}{:45}{:15}'.format(image['ImageId'], image['ImageLocation'][:40]+'...', image['CreationDate']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-w",
                        "--windows",
                        help="Only request Windows images",
                        action="store_true")
    parser.add_argument("-hy",
                        "--hypervisor",
                        nargs='?',
                        const='xen',
                        default='xen',
                        choices=['ovm', 'xen'],
                        help="Specify hypervisor")
    parser.add_argument("-a",
                        "--architecture",
                        nargs='?',
                        const='x86_64',
                        default='x86_64',
                        choices=['i386', 'x86_64'],
                        help="Specify the CPU architecture (-a x86_64).")
    parser.add_argument("-o",
                        "--owner-alias",
                        nargs='?',
                        const='*',
                        default='*',
                        choices=['amazon', 'aws-marketplace', 'microsoft'],
                        help="Specify the owner alias.")
    parser.add_argument("-c",
                        "--creation_date",
                        type=int,
                        default=30,
                        help="Specify a number. The number will be subtracted from the current date and results will \
be limited to images created after that date.")
    parser.add_argument("-n",
                        "--name_filter",
                        nargs='?',
                        const='',
                        default='*',
                        help="This filters the name attribute on the server side, is case sensitive, and defaults to \
*. You can specify a word, such as *SQL*, which will only return results containing that string.")
    parser.add_argument("-f",
                        "--filter",
                        help="This filters the ImageLocation response on the client side, and is not case sensitive. \
Specify a string. If the ImageLocation contains that string, only those results will be displayed")
    args = parser.parse_args()

    is_public = 'true'
    architecture = args.architecture
    hypervisor = args.hypervisor
    owner_alias = args.owner_alias
    image_age = (datetime.datetime.now() + datetime.timedelta(-args.creation_date)).isoformat()
    name_filter = args.name_filter
    main()