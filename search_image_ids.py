import argparse
import datetime
try:
    import boto3
except ImportError:
    print("[-] This script requires boto3. Try 'pip install boto3', or do an Internet search for installation instructions.")

def main():
    ec2 = boto3.client('ec2')
    if args.windows:
        response = ec2.describe_images(Filters=[
            {'Name': 'platform', 'Values': ['windows']},
            {'Name': 'architecture', 'Values': [architecture]},
            {'Name': 'hypervisor', 'Values': [hypervisor]},
            {'Name': 'is-public', 'Values': [is_public]},
            {'Name': 'owner-alias', 'Values': [owner_alias]},
            {'Name': 'name', 'Values': [search_filter]}
            ])
    else:
        response = ec2.describe_images(Filters=[
            {'Name': 'architecture', 'Values': [architecture]},
            {'Name': 'hypervisor', 'Values': [hypervisor]},
            {'Name': 'is-public', 'Values': [is_public]},
            {'Name': 'owner-alias', 'Values': [owner_alias]},
            {'Name': 'name', 'Values': [search_filter]}
        ])
    images = response.get('Images')
    for image in images:
        if image['CreationDate'] < image_age:
            if not args.windows:
                if 'windows' in image['ImageLocation'].lower():
                    continue
            print(image['ImageLocation'], image['ImageId'])


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
                        help="Specify hypervisor")
    parser.add_argument("-a",
                        "--architecture",
                        nargs='?',
                        const='x86_64',
                        default='x86_64',
                        help="Specify the CPU architecture (-a x86_64).")
    parser.add_argument("-o",
                        "--owner-alias",
                        nargs='?',
                        const='amazon',
                        default='amazon',
                        help="Specify the platform language.")
    parser.add_argument("-c",
                        "--creation_date",
                        type=int,
                        default=30,
                        help="Specify a number. The number will be subtracted from the current date and results will be limited to images created after that date.")
    parser.add_argument("-f",
                        "--filter",
                        nargs='?',
                        const='*',
                        default='*',
                        help="This filters the ImageLocation response, and defaults to *. You can specify a word, such as *SQL*, which will only return results containing that string. See the read me in repository for example filters.")
    args = parser.parse_args()

    is_public = 'true'
    architecture = args.architecture
    hypervisor = args.hypervisor
    owner_alias = args.owner_alias
    image_age = (datetime.datetime.now() + datetime.timedelta(-args.creation_date)).isoformat()
    search_filter = args.filter
    main()