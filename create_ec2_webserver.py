import boto3
import time

image_id = 'ami-1853ac65' # Amazon Linux AMI
instance_type = 't2.micro'
security_group_id = 'INSERT_SECURITY_GROUP_ID'
key_name = 'INSERT_KEY_NAME'
user_data = '''
#!/bin/bash
yum update -y
yum install httpd php mysql-server php-mysql -y
service httpd start
'''

def create_ec2_instance():
    ec2 = boto3.resource('ec2')
    try:
        instance = ec2.create_instances(ImageId=image_id, 
                                        InstanceType=instance_type,
                                        SecurityGroupIds=[security_group_id],
                                        KeyName=key_name,
                                        MinCount=1, 
                                        MaxCount=1,
                                        UserData=user_data
                                        )
    except Exception as e:
        print('[-] An error occurred!')
        print('[*] {}'.format(e))
        exit()
    instance_id = instance[0].instance_id
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
    instance_id = create_ec2_instance()
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
    print('[*] Note: It may take ~1 minute for the web server to be fully operational')

if __name__ == '__main__':
    main()