#!/usr/bin/env python3


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180727'
__version__ = '0.01'
__description__ = '''Searches a cloudwatch log group for a specified string.'''


import argparse
import sys
try:
    import boto3
except ImportError:
    print("[-] This script requires boto3. Try 'pip install boto3', or do an Internet search \
for installation instructions.")


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


def get_log_events(log_group_name, log_stream_name):
    """Returns events from a specified log stream."""
    client = boto3.client('logs')
    response = client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
    )
    return response


def get_log_groups():
    """Queries the log groups and returns the log group names"""
    client = boto3.client('logs')
    response = client.describe_log_groups()
    groups = response.get('logGroups')
    if groups:
        group_names = [group.get('logGroupName') for group in groups]
        return group_names


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
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="Increase output verbosity",
                        action="store_true")
    parser.add_argument("-g",
                        "--log_group",
                        nargs="?",
                        help="Specify a DNS log group name")
    parser.add_argument("-d",
                        "--data",
                        type=str,
                        help="Specify data to search for.")
    args = parser.parse_args()

    if args.data:
        search_string = args.data
    else:
        search_string = input("Please specify a string to search for: \n")
    if args.log_group:
        log_group_name = args.log_group
    else:
        print("\n[-] No log group specified. You can specify the DNS log group with the -g option.")
        query_answer = input("[!] Would you like to query the names of your existing DNS log groups? Type Y to query or any \
other key to exit.\n")
        if query_answer.lower().startswith('y'):
            log_group_names = get_log_groups()
            if log_group_names:
                print('\n[+] Log Group Name')
                for name in log_group_names:
                    print('    {}'.format(name))
                exit()
            else:
                print('\n[-] Querying existing log groups returned zero results.')
                print('See https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/query-logs.html#query-logs-configuring for more info.')
                exit()
        else:
            parser.print_help()
            print('\n[-] A DNS log group name is required.')
            exit()

    main()
