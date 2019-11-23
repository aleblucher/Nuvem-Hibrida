import boto3


ec2 = boto3.client('ec2')
# keypair = ec2.create_key_pair(KeyName='banananana')

# with open("myfile.txt","w")  as f:
    
#     f.write(str(keypair))

def createSecurityGroup():

    ec2.create_security_group(
    Description='myfirstdescritption',
    GroupName='banana_group',
    )


def createInstance():
    ec2r = boto3.resource('ec2')

    ec2r.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='banananana',
    MaxCount=1,
    MinCount=1,


    SecurityGroups=[
        'banana_group',
    ],
    UserData='userdata.sh'
    )

createInstance()