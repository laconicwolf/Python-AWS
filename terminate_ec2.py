#!/usr/bin/env python3


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180727'
__version__ = '0.01'
__description__ = '''Terminates an EC2 instance when supplied an instance ID.'''


import sys
try:
    import boto3
except ImportError:
    print("[-] This script requires boto3. Try 'pip install boto3', or do an Internet search \
for installation instructions.")


def terminate_ec2_instance(instance_id):
    """Terminates the EC2 instance associated with the specified instance Id and returns the response."""
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    try:
        response = instance.terminate()
    except Exception as e:
        print('[-] An error occurred!')
        print('[*] {}'.format(e))
        exit()
    return response


def check_instance_id(instance_id):
    """Checks if the instance ID appears to be valid."""
    if not instance_id.startswith('i-'):
        print('That doesn\'t look like an InstanceId...They \
            look like this: i-01e4b573fedecdf41')
        print('Double check and try again.')
        exit()


def main():
    if len(sys.argv) != 2:
        print('\nUsage: ./terminate_ec2.py <InstanceId>')
        print('Example: ./terminate_ec2.py i-01e4b573fedecdf41')
        exit()
    instance_id = sys.argv[1]
    check_instance_id(instance_id)
    response = terminate_ec2_instance(instance_id)
    term_data = response['TerminatingInstances'][0]
    for key in term_data.keys():
        print('[*] {}: {}'.format(key, term_data[key]))


if __name__ == '__main__':
    main()
