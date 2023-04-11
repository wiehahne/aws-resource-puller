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
            'Instance ID': instance.id,
            'Name': name,
            'Type': instance.instance_type,
            'vCPUs': instance.cpu_options['CoreCount'] * instance.cpu_options['ThreadsPerCore'],
            'Memory': instance.memory, # Please note that this attribute is not available in Boto3. You will need to map instance types to their memory sizes manually or use another API/library.
        })
    return instance_details

def write_to_csv(instance_details):
    with open('ec2_instances.csv', mode='w', newline='') as csvfile:
        fieldnames = ['Instance ID', 'Name', 'Type', 'vCPUs', 'Memory']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for instance_detail in instance_details:
            writer.writerow(instance_detail)

def main():
    all_regions = get_all_regions()
    all_instance_details = []

    for region in all_regions:
        instance_details = get_instance_details(region)
        all_instance_details.extend(instance_details)

    write_to_csv(all_instance_details)

if __name__ == '__main__':
    main()
