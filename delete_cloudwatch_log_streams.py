import boto3


def get_log_stream_names(log_group_name):
    """Returns a list of log stream names."""
    client = boto3.client('logs')
    streams = client.describe_log_streams(logGroupName=log_group_name)
    log_stream_names = []
    i = 0
    for stream in streams['logStreams']:
        log_stream_names.append(streams['logStreams'][i]['logStreamName'])
        i += 1
    return log_stream_names


def delete_log_streams(log_group_name, log_stream_name):
    """Deletes log streams."""
    client = boto3.client('logs')
    response = client.delete_log_stream(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        )


def main():
    print('[*] Searching for logstreams in {}...'.format(log_group_name))
    try:
        log_stream_names = get_log_stream_names(log_group_name)
    except Exception as e:
        print('[-] An error has occured!')
        print('[*] {}'.format(e))
    for log_stream_name in log_stream_names:
        print('[*] Deleting logstream {}'.format(log_stream_name))
        try:
            delete_log_streams(log_group_name, log_stream_name)
        except Exception as e:
            print('[-] An error has occured!')
            print('[*] {}'.format(e))


if __name__ == '__main__':
    log_group_name = 'INSERT_LOG_GROUP_NAME_HERE'
    main()
