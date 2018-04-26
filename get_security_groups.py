import boto3


def describe_security_groups():
    '''Returns a dictionary containing security group information.
    '''
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_security_groups()
    except Exception as e:
        print('[-] An error occurred!')
        print('[*] {}'.format(e))
        exit()
    return response


def main():
    print('\n[*] Getting your information about your Security Groups...\n')
    security_group_descriptions = describe_security_groups()
    security_groups = security_group_descriptions['SecurityGroups']
    for security_group in security_groups:
        group_id = security_group['GroupId']
        group_name = security_group['GroupName']
        group_desc = security_group['Description']
        print('[+] GroupId: {}'.format(group_id))
        print('    GroupName: {}'.format(group_name))
        print('    Description: {}'.format(group_desc))
        print()


if __name__ == '__main__':
    main()