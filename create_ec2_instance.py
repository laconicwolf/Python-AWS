import boto3
import time
import os
import argparse


def create_ec2_instance(image_id, instance_type, security_group_id, key_name):
    ec2 = boto3.resource('ec2')
    try:
        if not key_name and not security_group_id:
            instance = ec2.create_instances(ImageId=image_id, 
                                            InstanceType=instance_type,
                                            MinCount=1, 
                                            MaxCount=1,
                                            UserData=user_data
                                            )
        elif not key_name:
            instance = ec2.create_instances(ImageId=image_id, 
                                            InstanceType=instance_type,
                                            SecurityGroupIds=[security_group_id],
                                            MinCount=1, 
                                            MaxCount=1,
                                            UserData=user_data
                                            )
        elif not security_group_id:
            instance = ec2.create_instances(ImageId=image_id, 
                                            InstanceType=instance_type,
                                            KeyName=key_name,
                                            MinCount=1, 
                                            MaxCount=1,
                                            UserData=user_data
                                            )
        else:
            instance = ec2.create_instances(ImageId=image_id, 
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
    ec2 = boto3.client('ec2')
    data = ec2.describe_instances(InstanceIds=[instance_id])
    reservation_data = data['Reservations'][0]
    instance_data = reservation_data['Instances'][0]
    public_ip_address = instance_data['PublicIpAddress']
    return public_ip_address


def main():
    print('[*] Attempting to launch an ec-2 instance...')
    time.sleep(2)
    instance_id = create_ec2_instance(image_id, instance_type, security_group_id, key_name)
    print('[+] EC2 instance launched!')
    print('    Type: {}'.format(instance_type))
    print('    ID: {}'.format(instance_id))
    time.sleep(2)
    print('[*] Getting instance IP address...')
    time.sleep(2)
    public_ip_address = ''
    while not public_ip_address:
        try:
            public_ip_address = get_ec2_public_ip_address(instance_id)
        except:
            sleep(3)
    print('[+] IP Address: {}'.format(public_ip_address))
    print('[*] Note: It may take 1-2 minutes for all of the services to be fully operational')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-k",
                        "--key",
                        help="Specify a SSH private key file.")
    parser.add_argument("-id",
                        "--imageId",
                        nargs="?",
                        default='ami-467ca739', # Amazon Linux AMI 4/25/2018
                        help="Specify an Instance ID (-id ami-185ac65).")
    parser.add_argument("-it",
                        "--instanceType",
                        nargs="?",
                        default='t2.micro',
                        help="Specify an Instance Type (-it m1.medium).")
    parser.add_argument("-ud",
                        "--userData",
                        help="Specify a script to run at start up.")
    parser.add_argument("-sg",
                        "--securityGroupId",
                        help="Specify a Security Group ID")
    args = parser.parse_args()

    if not args.securityGroupId:
        print("This instance will be launched without a Security Group ID, which defaults\
        to a security group that does not allow any inbound connections.")
        print('You can specify a security group with the -sg option.')
        cont = input("Would you like to continue? Type y or n.\n")
        if not cont.lower().startswith('y'):
            exit()

    if not args.key:
        print("This instance will be launched without an SSH key. Without specifying a key,\
        you will be unable to access the instance.")
        print('You can specify a key name with the -k option.')
        cont = input("Would you like to continue? Type y or n.\n")
        if not cont.lower().startswith('y'):
            exit()

    image_id = args.imageId 
    instance_type = args.instanceType
    security_group_id = args.securityGroupId if args.securityGroupId else None
    key_name = args.key if args.key else None
    if args.userData:
        user_data_file = args.userData
        if not os.path.exists(user_data_file):
            print("\n[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        user_data = open(user_data_file).read()
    else:
        user_data =  ""
    main()