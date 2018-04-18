import boto3
import sys


def terminate_ec2_instance(instance_id):
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
    if not instance_id.startswith('i-'):
        print('That doesn\'t look like an InstanceId...They \
            look like this: i-01e4b573fedecdf41')
        print('Double check and try again.')
        exit()


def main():
    if len(sys.argv) != 2:
        print('\nUsage: ./terminate_ec2_instance.py <InstanceId>')
        print('Example: ./terminate_ec2_instance.py i-01e4b573fedecdf41')
        exit()
    instance_id = sys.argv[1]
    check_instance_id(instance_id)
    response = terminate_ec2_instance(instance_id)
    term_data = response['TerminatingInstances'][0]
    for key in term_data.keys():
        print('[*] {}: {}'.format(key, term_data[key]))


if __name__ == '__main__':
    main()