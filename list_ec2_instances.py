import boto3
import csv

def get_all_regions():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions

def get_instance_details(region):
    ec2_resource = boto3.resource('ec2', region_name=region)
    instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])

    instance_details = []
    for instance in instances:
        name = ''
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
        instance_details.append({
            'Region': region,
            'Instance ID': instance.id,
            'Name': name,
            'Type': instance.instance_type,
            'vCPUs': instance.cpu_options['CoreCount'] * instance.cpu_options['ThreadsPerCore']
        })
    return instance_details

def write_to_csv(instance_details):
    with open('ec2_instances.csv', mode='w', newline='') as csvfile:
        fieldnames = ['Region', 'Instance ID', 'Name', 'Type', 'vCPUs', 'Memory']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for instance_detail in instance_details:
            writer.writerow(instance_detail)

def upload_to_s3(bucket_name, s3_key):
    s3_client = boto3.client('s3')
    s3_client.upload_file('ec2_instances.csv', bucket_name, s3_key)

def main():
    all_regions = get_all_regions()
    all_instance_details = []

    for region in all_regions:
        instance_details = get_instance_details(region)
        all_instance_details.extend(instance_details)

    write_to_csv(all_instance_details)

    bucket_name = input("Please enter the S3 bucket name (and ensure you have permissions): ")
    s3_key = input("Please enter the S3 key (path) for the CSV file (E.g. your-prefix/ec2_instances.csv): ")

    upload_to_s3(bucket_name, s3_key)

if __name__ == '__main__':
    main()
