#!/usr/bin/env python3


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180727'
__version__ = '0.01'
__description__ = '''Launches an EC2 instance.'''


import argparse
import time
import os
import sys
try:
    import boto3
except ImportError:
    print("[-] This script requires boto3. Try 'pip install boto3', or do an Internet search \
for installation instructions.")

# For safe backwards compatability with Python2
if sys.version.startswith('2'):
    input = raw_input


def get_security_groups():
    """Queries the existing security groups and returns the group IDs, names, and descriptions"""
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_security_groups()
    except Exception as e:
        print('[-] An error occurred when querying the security groups. Error: {} \nExiting.'.format(e))
        exit()
    security_groups = response.get('SecurityGroups')
    security_group_data = []
    if security_groups:
        for group in security_groups:
            id = group['GroupId']
            name = group['GroupName']
            desc = group['Description']
            security_group_data.append((id, name, desc))
    return security_group_data


def get_key_names():
    """Returns the names of existing SSH keys."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_key_pairs()
    kp = response.get('KeyPairs')
    if not kp:
        key_names = None
    else:
        key_names = [k['KeyName'] for k in kp]
    return key_names


def create_keypair():
    """Creates an AWS key pair, writing the public key file to the current directory. Returns the key name"""
    ec2 = boto3.client('ec2')
    key_name = 'my_ssh_key-{}'.format(time.ctime().split()[3].replace(':', ''))
    response = ec2.create_key_pair(KeyName=key_name)
    key_material = response.get('KeyMaterial')
    key_file_name = key_name + '.pem'
    try:
        with open(key_file_name, 'w') as fh:
            fh.write(key_material)
        print('[+] File written to {}.'.format(key_file_name))
    except Exception as e:
        print('[-] An error occurred when writing the SSH key file. Error: {} \nExiting.'.format(e))
        exit()
    return key_name


def create_ec2_instance(image_id, instance_type, security_group_id, key_name):
    """Launches an EC2 instance using the supplied parameters. Returns the InstanceId."""
    ec2 = boto3.resource('ec2')
    try:
        if not key_name and not security_group_id:
            instance = ec2.create_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                UserData=user_data
            )
        elif not key_name:
            instance = ec2.create_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                SecurityGroupIds=[security_group_id],
                MinCount=1,
                MaxCount=1,
                UserData=user_data
            )
        elif not security_group_id:
            instance = ec2.create_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                UserData=user_data
            )
        else:
            instance = ec2.create_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                SecurityGroupIds=[security_group_id],
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                UserData=user_data
            )
        instance_id = instance[0].instance_id
    except Exception as e:
        print('[-] An error occurred!')
        print('[*] {}'.format(e))
        exit()
    return instance_id


def get_ec2_public_ip_address(instance_id):
    """"Returns the public IPv4 address of the supplied InstanceId."""
    ec2 = boto3.client('ec2')
    data = ec2.describe_instances(InstanceIds=[instance_id])
    reservation_data = data['Reservations'][0]
    instance_data = reservation_data['Instances'][0]
    public_ip_address = instance_data['PublicIpAddress']
    return public_ip_address


def main():
    print('\n[+] You are launching an instance with the following options:')
    print('    Image Id       {}'.format(image_id))
    print('    SSH Key Pair   {}'.format(key_name))
    print('    Instance Type  {}'.format(instance_type))
    print('    Security Group {}\n'.format(security_group_id))
    if not args.force:
        launch_answer = input('Would you like to continue? Type Y to continue launching, type any other key to quit.\n')
        if not launch_answer.lower().startswith('y'):
            exit()
    print('[*] Attempting to launch an ec-2 instance...')
    time.sleep(2)
    instance_id = create_ec2_instance(image_id, instance_type, security_group_id, key_name)
    print('[+] EC2 instance launched!')
    print('    ID: {}'.format(instance_id))
    time.sleep(2)
    print('[*] Getting instance IP address...')
    time.sleep(2)
    public_ip_address = ''
    while not public_ip_address:
        try:
            public_ip_address = get_ec2_public_ip_address(instance_id)
        except Exception as e:
            time.sleep(3)
    print('[+] IP Address: {}'.format(public_ip_address))
    print('[*] Note: It may take 1-2 minutes for all of the services to be fully operational')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="Increase output verbosity",
                        action="store_true")
    parser.add_argument("-k",
                        "--key",
                        help="Specify a SSH private key file.")
    parser.add_argument("-id",
                        "--image_id",
                        nargs="?",
                        const='ami-b70554c8',  # Amazon Linux 2 AMI (HVM), SSD Volume Type 7/27/2018
                        help="Specify an Instance ID (-id ami-b70554c8).")
    parser.add_argument("-it",
                        "--instance_type",
                        nargs="?",
                        const='t2.micro',
                        default='t2.micro',
                        help="Specify the Instance Type. Default is t2.micro. For a listing of all types, please see \
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html")
    parser.add_argument("-ud",
                        "--user_data",
                        help="Specify the file path of a script to run at start up (-ud \
/home/jake/webserver_bootstrap.txt).")
    parser.add_argument("-sg",
                        "--security_group_id",
                        help="Specify a Security Group ID (-sg sg-a31c94ec)")
    parser.add_argument("-f",
                        "--force",
                        help="Launch instance without additional prompting.",
                        action="store_true")
    args = parser.parse_args()

    if args.image_id:
        image_id = args.image_id
    else:
        parser.print_help()
        print('\n[-] Please specify an ImageId (-id). If you do not know any ImageIds, you can use the other tool, \
search_images_ids.py, look up ImageIds in the AWS console, or you can just use this ID \'ami-b70554c8\', which is \
 Amazon Linux 2 AMI (HVM), SSD Volume Type as of 7/27/2018.')
        exit()
    if args.key:
        key_name = args.key
    else:
        print("\n[*] You did not specify an existing SSH key for this instance. You can supply a key with the -k \
option.")
        existing_key_answer = input("[!] Would you like to see your existing keys? Type Y to see existing keys, C \
to continue, or Q to quit.\n")
        if not existing_key_answer.lower().startswith('c'):
            if existing_key_answer.lower().startswith('y'):
                existing_key_names = get_key_names()
                if existing_key_names:
                    print('[+] Existing Key Names:')
                    for name in existing_key_names:
                        print('   ', name)
                    exit()
                else:
                    print('[-] Querying keys returned no existing keys.')
            elif existing_key_answer.lower().startswith('q'):
                exit()
            else:
                print("[-] Invalid input. Quitting.")
                exit()
        creation_answer = input("[!] Would you like a new key created? Type Y to create a key in your current directory. \
Type N to continue without a keypair.\n")
        if creation_answer.lower().startswith('y'):
            key_name = create_keypair()
            print('[+] New key generated! Kay name: {}'.format(key_name))
        elif creation_answer.lower().startswith('n'):
            print("[*] This instance will be launched without an SSH key. Without specifying a key,\
    you will be unable to access the instance.")
            cont_answer = input("[!] Would you like to continue? Type Y to continue or any other key to exit.\n")
            if not cont_answer.lower().startswith('y'):
                exit()
            key_name = None

    if args.security_group_id:
        security_group_id = args.security_group_id
    else:
        print("\n[*] Without specifying a security group, your instance will be launched \
into your default security group. You can specify a security group with the -sg option.")
        existing_group_answer = input("[!] Would you like to see your existing security groups? Type Y to see existing \
groups, C to continue, or Q to quit.\n")
        if not existing_group_answer.lower().startswith('c'):
            if existing_group_answer.lower().startswith('y'):
                existing_group_data = get_security_groups()
                if existing_group_data:
                    print('[+] Existing Security Groups:')
                    print('    {:15}{:20}{:25}'.format('GroupId', 'Name', 'Description'))
                    for data in existing_group_data:
                        print('    {:15}{:20}{:25}'.format(data[0], data[1], data[2]))
                    exit()
                else:
                    print('[-] Querying security groups returned no existing groups.')
            elif existing_group_answer.lower().startswith('q'):
                exit()
            else:
                print("[-] Invalid input. Quitting.")
                exit()

    instance_type = args.instance_type
    if args.user_data:
        user_data_file = args.user_data
        if not os.path.exists(user_data_file):
            print("\n[-] The file cannot be found or you do not have permission to open the file. \
Please check the path and try again\n")
            exit()
        user_data = open(user_data_file).read()
    else:
        user_data = ""
    main()