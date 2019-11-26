import boto3
import time


ec2_R_OHIO = boto3.resource('ec2', region_name= 'us-east-2')
ec2_C_OHIO = boto3.client('ec2', region_name= 'us-east-2')
ec2_R_NV = boto3.resource('ec2', region_name= 'us-east-1')
ec2_C_NV = boto3.client('ec2', region_name= 'us-east-1')


# ec2 = boto3.client('ec2')
# keypair = ec2.create_key_pair(KeyName='banananana')

# with open("myfile.txt","w")  as f:
    
#     f.write(str(keypair))



# Alocar IP elastico e associar ao security group
# OHIO
def createInstConnector(private_IP, security_group):
    print("Subindo a máquina conectora")
    resp_con = ec2_R_OHIO.create_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='KEY_LEK_OHIO',
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
sudo tmux new -d -s execution 'export SERVER=http://{}:5000;python3 ./database/connector.py'
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


    tt = []
    for i in resp_db:
        tt.append(i)

    response = ec2_C_OHIO.describe_instances(
        InstanceIds=[
            tt[0].id,
        ]
    )

    for i in response:
        tt.append(i)
    response = ec2_R_OHIO.Instance(tt[0].id)
    while (response.public_ip_address == None):
        response = ec2_R_OHIO.Instance(tt[0].id)

    return resp_con, response.public_ip_address


# OHIO
def createInstDB(security_group):
    print("Subindo a máquina da DataBase")
    resp_db = ec2_R_OHIO.create_instances(

    ImageId='ami-0d5d9d301c853a04a', #OHIO IMAGE
    InstanceType='t2.micro',
    KeyName='KEY_LEK_OHIO',
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
sudo tmux new -d -s execution 'python3 ./database/server.py'
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

    response = ec2_C_OHIO.describe_instances(
    InstanceIds=[
        tt[0].id,
    ]
)

    for i in response:
        tt.append(i)

    return resp_db, tt[0], tt[0].private_ip_address

# NORTH VIRGINIA
def createElasticIP():
    print("Alocando um IP elástico")
    allocation = ec2_C_NV.allocate_address(Domain='vpc')
    res = allocation['PublicIp']
    return allocation

# OHIO
def createSecurityGroupWithElasticIP(elastic_IP):
    print("Criando o security group")
    sec_group = ec2_R_OHIO.create_security_group(
    GroupName='SecurityDB', Description='Projeto final')
    sec_group.authorize_ingress(
    CidrIp= elastic_IP+'/32',
    IpProtocol='tcp',
    FromPort=5001,
    ToPort=5001
)
    sec_group.authorize_ingress(
    CidrIp= '0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

    return sec_group


# OHIO
def createSecurityGroup():
    print("Criando o security group")
    sec_group = ec2_R_OHIO.create_security_group(
    GroupName='1st', Description='Projeto final')
    sec_group.authorize_ingress(
    CidrIp= '0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=5000,
    ToPort=5000
)
    sec_group.authorize_ingress(
    CidrIp= '0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)
    return sec_group

# NORTH VIRGINIA
def createInsOutsider(allocation_ID, pub_IP): #adicionar o param security group
    print("Subindo a segunda nuvem")

    resp_out = ec2_R_NV.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='2nd',
    MaxCount=1,
    MinCount=1,

    SecurityGroupIds=[
        'sg-0b0f8470d177c6479',
    ],

    UserData='''#!/bin/bash
sudo apt -y update

sudo apt install language-pack-pt -y
sudo apt install python3-pip -y
git clone https://github.com/aleblucher/Nuvem-Hibrida
sudo pip3 install flask
cd Nuvem-Hibrida
sudo apt install tmux
sudo tmux new -d -s execution 'export SERVER=http://{}:5000;python3 ./database/connector.py'
'''.format(pub_IP),

    TagSpecifications=[
        {
            'ResourceType' : 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'Outsider'
                },
            ]
        },
    ],
    )

    tt = []
    for i in resp_out:
        tt.append(i)

    temp = ec2_C_NV.describe_instances(
    InstanceIds=[
        tt[0].id,
    ]

    )
    instance_status = temp['Reservations'][0]['Instances'][0]['State']['Name']
    
    while instance_status == 'pending':

        temp = ec2_C_NV.describe_instances(
        InstanceIds=[
            tt[0].id,
        ])
        instance_status = temp['Reservations'][0]['Instances'][0]['State']['Name']
    

        print(instance_status)
        print("\n")
        time.sleep(3)
        
    if instance_status == 'running':
        resp_ass = ec2_C_NV.associate_address(
        AllocationId=allocation_ID,
        InstanceId=tt[0].id,
        )
        print('agora sim!')

        return resp_ass, tt[0].id, ipp
    else:
        return 'erro'




def createConnectorPublicIp(pub_IP):
    print("Subindo a máquina do outsider com ip externo")
    resp_db = ec2_R_NV.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='2nd',
    MaxCount=1,
    MinCount=1,

    SecurityGroupIds=[
        'sg-0b0f8470d177c6479',
    ],

    UserData='''#!/bin/bash
sudo apt -y update

sudo apt install language-pack-pt -y
sudo apt install python3-pip -y
git clone https://github.com/aleblucher/Nuvem-Hibrida
sudo pip3 install flask
cd Nuvem-Hibrida
sudo apt install tmux
sudo tmux new -d -s execution 'export SERVER=http://{}:5000;python3 ./database/connector.py'
'''.format(pub_IP),

    TagSpecifications=[
        {
            'ResourceType' : 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'Outsider'
                },
            ]
        },
    ],
    )
    tt = []
    for i in resp_db:
        tt.append(i)

    response = ec2_C_NV.describe_instances(
    InstanceIds=[
        tt[0].id,
    ]
    )

    for i in response:
        tt.append(i)

    response = ec2_R_NV.Instance(tt[0].id)
    while (response.public_ip_address == None):
        response = ec2_R_NV.Instance(tt[0].id)

    print(dir(tt[0]))
    print(tt[0].public_ip_address)

    return resp_db, tt[0].id, response.public_ip_address





# NORTH VIRGINIA
def createSecurityGroupLoadBalancer():
    sec_group = ec2_R_NV.create_security_group(
    GroupName='LoadBalancerSG', Description='Load Balancer')
    sec_group.authorize_ingress(
    CidrIp= '0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=5001,
    ToPort=5001
)
    sec_group.authorize_ingress(
    CidrIp= '0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

    return sec_group


def createLoadBalancer(security_group):
    client = boto3.client('elb')
    responseLB = client.create_load_balancer(
    LoadBalancerName='ALECER',
    Listeners=[
        {
            'Protocol': 'TCP',
            'LoadBalancerPort': 5001,
            'InstanceProtocol': 'TCP',
            'InstancePort': 5001,
        },
    ],
    AvailabilityZones=[
            'us-east-1a','us-east-1b','us-east-1c', 'us-east-1e', 'us-east-1f', 'us-east-1d'
    ],
    
    SecurityGroups=[
        security_group.id,
    ],
    )

    return responseLB

def createAutoScalling(instance_id):
    client = boto3.client('autoscaling')
    responseAS = client.create_auto_scaling_group(
    AutoScalingGroupName='ALEUP',
    InstanceId=instance_id,
    MinSize=1,
    MaxSize=10,
    HealthCheckGracePeriod=300,
    LoadBalancerNames=[
        'ALECER',
    ]
)
    return responseAS


# Primeiro security group
first_sg = createSecurityGroup()

# Sobe a maquina do DB
resp_db, response, pip = createInstDB(first_sg.id)

# Aloca um IP elástico
temp = createElasticIP()
elastic_IP = temp['PublicIp']
allocation_ID = temp['AllocationId']
print("\n")
print(elastic_IP)
print(allocation_ID)
print("\n")

# Cria um SG baseado no IP elástico
security_group = createSecurityGroupWithElasticIP(elastic_IP)

# Sobe o conector com o SG e o IP privado do DB 
oi , pp = createInstConnector(pip, security_group.id)
print(pp)
# Sobe a máquina 'outsider', correspondente a segunda cloud
resp, id_maquina, ipp = createConnectorPublicIp(pp)
print(resp,"adhwuidhahwdahwuidhaiwhdawdhawuid", ipp, "aiuduawhduawhdhawdhiuawhduiawhduiawhiudhauidhauidhauiwhduiawhduiahwduiawhduiahdiuawhduihawuidhauidhwaiuhd")

resp, id_maquina, ipp = createConnectorPublicIp(ipp)
print(resp,"adhwuidhahwdahwuidhaiwhdawdhawuid", ipp, "aiuduawhduawhdhawdhiuawhduiawhduiawhiudhauidhauidhauiwhduiawhduiahwduiawhduiahdiuawhduihawuidhauidhwaiuhd")


# Cria um SG para o Load Balancer
print("\n")
print("Criando o Security Group para o Load Balancer")
lb_group = createSecurityGroupLoadBalancer()

# Cria o Load Balncer
print("\n")
print("criando o Load Balancer")
i_lb_u = createLoadBalancer(lb_group)
print(i_lb_u)

# Cria Auto Scalling
print("\n")
print("Criando o AutoScalling")
print(createAutoScalling(id_maquina))