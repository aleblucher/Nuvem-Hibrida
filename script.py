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

    resp = ec2r.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='2nd',
    MaxCount=1,
    MinCount=1,


    SecurityGroups=[
        'banana_group',
    ],
    UserData='''#!/bin/bash
sudo apt -y update

sudo apt install language-pack-pt -y
sudo apt install python3-pip -y
git clone https://github.com/aleblucher/Nuvem-Hibrida
sudo apt -y install python-pip python-dev
sudo pip3 install flask
cd Nuvem-Hibrida
echo "instalando mysql"
echo 'debconf debconf/frontend select Dialog' | sudo debconf-set-selections
yes "" | sudo apt -y install mysql-server-core-5.7 << EOF




EOF
sudo mysql < ./scripts/123.sql
sudo pip3 install requests
sudo apt install tmux
sudo tmux new -d -s execution 'export SERVER="http://localhost:5000"; sudo python3 ./database/connector.py'
'''
    )
    return resp

print(createInstance())