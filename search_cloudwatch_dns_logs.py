import boto3
import sys


def get_log_stream_names(log_group_name):
    ''' Returns a list of log stream names.
    '''
    client = boto3.client('logs')
    streams = client.describe_log_streams(logGroupName=log_group_name)
    log_stream_names = []
    i = 0
    for stream in streams['logStreams']:
        log_stream_names.append(streams['logStreams'][i]['logStreamName'])
        i += 1
    return log_stream_names


def get_log_events(log_group_name, log_stream_name):
    ''' Returns events from a specified log stream.
    '''
    client = boto3.client('logs')
    response = client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        )
    return response


def main():
    print('[*] Searching for logstreams in {}...'.format(log_group_name))
    try:
        log_stream_names = get_log_stream_names(log_group_name)
    except Exception as e:
        print('[-] An error has occured!')
        print('[*] {}'.format(e))
    for log_stream_name in log_stream_names:
        print('[*] Checking logstream {}'.format(log_stream_name))
        logs = get_log_events(log_group_name, log_stream_name)
        events = logs['events'][0]
        message = events['message']
        if search_string in message:
            print('[+] {} found in log message: '.format(search_string))
            print('    Message: {}'.format(message))
    


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('\n[*] Usage: search_cloudwatch_dns_logs.py <string to search for>')
        print('[*] Example: search_cloudwatch_dns_logs.py cuejdliaerjfa.laconicwolf.net')
        exit()

    search_string = sys.argv[1]

    log_group_name = 'INSERT_DNS_LOG_GROUP'

    main()
