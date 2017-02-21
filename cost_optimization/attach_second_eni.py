s program queries all servers in the AWS account
that dont have a second network attached.
Program attach the correct AZ ENI.
It only attach the interface to running instances
"""

import time
import json
import boto3

start_time = time.time()

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
subnet_main = ['subnet-xxxx1', 'subnet-xxxx2', 'subnet-xxxx3'] # Check instances on these subnets
owner_main = ['30995619944', '309956199498'] # this uses the owner of the AMI for reference on what instance to check in this case RHEL and AWS
groups_main = ['']


def collect_subnets():
    """
    Query Network information on the account
    Print all VPCs,  Subnets, AZ available on the account
    """
    list_subnet = {"id" : []}
    for vpc in ec2.vpcs.all():
        for az in ec2.meta.client.describe_availability_zones()["AvailabilityZones"]:
            for subnet in vpc.subnets.filter(Filters=[{"Name": "availabilityZone", "Values": [az["ZoneName"]]}]):
                info_subnet = {
                    "vpc" : vpc.id,
                    "az" : az["ZoneName"],
                    "subnet" : subnet.id
                }
                list_subnet = info_subnet
                print(list_subnet)
    json_subnet = json.dumps(list_subnet)
    print(json_subnet)

def query_gdriver():
    """
    Findd exact subnet and security group that the network 
    needs to be attached to
    """ 

    global gdriver
    if vpc_id == 'vpc-xxxx' and network_az == 'us-east-1a':
        gdriver = ('subnet-xx1', 'sg-8f0xxx')
    elif vpc_id == 'vpc-xxxx' and network_az == 'us-east-1b':
        gdriver = ('subnet-xxx', 'sg-8f0xxxx')
    elif vpc_id == 'vpc-xxxx' and network_az == 'us-east-1c':
        gdriver = ('subnet-xxx', 'sg-xxxx')
    elif vpc_id == 'vpc-xxx' and network_az == 'us-east-1c':
        gdriver = ('subnet-xxx', 'sg-xxxx')

    return gdriver


if __name__ == "__main__":

    collect_subnets()

    for instance in ec2.instances.all():
        image_owner = instance.image.owner_id
        image_ami_id = instance.image._id
        instance_state = instance.state['Name']
        network_eni = instance.network_interfaces
        vpc_id = instance.vpc_id
        network_az = instance.placement['AvailabilityZone']
        list_size = len(network_eni)

        for owner_find in owner_main:
            if owner_find in image_owner:
                company_owner = 'True'
                break

        if instance_state == 'running' and company_owner == 'True':
            i = 0
            gdriver_network = 'False'
            while i < list_size:
                subnet_id = network_eni[i].subnet_id
                i += 1
                for subnet_find in subnet_main:
                    if subnet_find in subnet_id:
                        gdriver_network = 'True'
                        break
            datalist = {

                "instance_id" : instance.id,
                "vpc_id" : vpc_id,
                "network_az" : network_az
            }
            json_datalist = json.dumps(datalist)
            print(json_datalist)
            result_gdriver = query_gdriver()
            print('The following subnet has been identify', result_gdriver)
            network_interface = ec2_client.create_network_interface(SubnetId=result_gdriver[0], Description = 'Gdriver', Groups = [result_gdriver[1]])
            network_eni = network_interface['NetworkInterface']['NetworkInterfaceId']
            print('the following ENI will be attached to instance ', instance.id, network_eni)
            attach_network_interface = ec2_client.attach_network_interface(NetworkInterfaceId = network_eni, InstanceId = instance.id, DeviceIndex = 1)

    print("--- The program took %s seconds----" % (time.time() - start_time))
