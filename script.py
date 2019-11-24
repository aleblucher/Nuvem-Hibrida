import boto3


ec2 = boto3.client('ec2')
# keypair = ec2.create_key_pair(KeyName='banananana')

# with open("myfile.txt","w")  as f:
    
#     f.write(str(keypair))


# Alocar IP elastico e associar ao security group
def createInstConnector(private_IP, security_group):
    print("Subindo a máquina conectora")
    ec2r = boto3.resource('ec2')
    resp_con = ec2r.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='2nd',
    MaxCount=1,
    MinCount=1,

    SecurityGroupIds=[
        security_group,
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


    return resp_con



def createInstDB():
    print("Subindo a máquina da DataBase")
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
sudo pip3 install pymsql
sudo python3 -m pip install PyMySQL
sudo tmux new -d -s execution 'sudo python3 ./database/server.py'
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

def createElasticIP():
    print("Alocando um IP elástico")
    allocation = ec2.allocate_address(Domain='vpc')
    res = allocation['PublicIp']
    return res

def createSecurityGroup(elastic_IP):
    print("Criando o security group")
    ec2r = boto3.resource('ec2')
    sec_group = ec2r.create_security_group(
    GroupName='SecurityDB', Description='Projeto final')
    sec_group.authorize_ingress(
    CidrIp= elastic_IP+'/32',
    IpProtocol='tcp',
    FromPort=5001,
    ToPort=5001
)
    return sec_group




# Sobe a maquina do DB
resp_db, response, pip = createInstDB()

# Aloca um IP elástico
elastic_IP = createElasticIP()

# Cria um SG baseado no IP elástico
security_group = createSecurityGroup(elastic_IP)

# Sobe o conector com o SG e o IP privado do DB 
print(createInstConnector(pip, security_group.id))