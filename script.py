import boto3


ec2 = boto3.client('ec2')
# keypair = ec2.create_key_pair(KeyName='banananana')

# with open("myfile.txt","w")  as f:
    
#     f.write(str(keypair))


# Alocar IP elastico e associar ao security group
def createInstConnector(private_IP):
    ec2r = boto3.resource('ec2')
    resp_con = ec2r.create_instances(

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
sudo pip3 install flask
cd Nuvem-Hibrida
sudo apt install tmux
sudo tmux new -d -s execution 'export SERVER={}; sudo python3 ./database/connector.py'
'''.format(private_IP),

    TagSpecifications=[
        {
            'ResourceType' : 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'Connector'
                },
            ]
        },
    ],
    )


    #allocation = ec2.allocate_address(Domain='vpc')

    return resp_con


def createSecurityGroup():

    ec2.create_security_group(
    Description='myfirstdescritption',
    GroupName='banana_group',
    )


def createInstDB():
    ec2r = boto3.resource('ec2')
    ec2c = boto3.client('ec2')

    resp_db = ec2r.create_instances(

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

echo "mysql-server-5.6 mysql-server/root_password password root" | sudo debconf-set-selections
echo "mysql-server-5.6 mysql-server/root_password_again password root" | sudo debconf-set-selections
sudo apt-get -y install mysql-server
sudo mysql_secure_instalation
sudo apt install expect -y
MYSQL_ROOT_PASSWORD=root
SECURE_MYSQL=$(expect -c "
set timeout 10
spawn mysql_secure_installation
expect \"Enter current password for root (enter for none):\"
send \"$MYSQL\r\"
expect \"Change the root password?\"
send \"n\r\"
expect \"Remove anonymous users?\"
send \"y\r\"
expect \"Disallow root login remotely?\"
send \"y\r\"
expect \"Remove test database and access to it?\"
send \"y\r\"
expect \"Reload privilege tables now?\"
send \"y\r\"
expect eof
")
echo "$SECURE_MYSQL"
sudo apt purge expect -y
mysql -uroot -proot << EOF
CREATE USER IF NOT EXISTS "leca"@"localhost" IDENTIFIED BY "leca";
CREATE DATABASE banana;
GRANT ALL PRIVILEGES ON banana . * TO "leca"@"localhost";
EOF

sudo pip3 install requests
sudo apt install tmux
sudo tmux new -d -s execution 'export SERVER="http://localhost:5000"; sudo python3 ./database/connector.py'
''',

    TagSpecifications=[
        {
            'ResourceType' : 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'Database'
                },
            ]
        },
    ],
    )

    tt = []
    for i in resp_db:
        tt.append(i)

    response = ec2.describe_instances(
    InstanceIds=[
        tt[0].id,
    ]
)

    for i in response:
        tt.append(i)

    return resp_db, tt[0], tt[0].private_ip_address

resp_db, response, pip = createInstDB()
print(response.public_ip_address)
print(createInstConnector(pip))