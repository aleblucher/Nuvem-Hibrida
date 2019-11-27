import boto3
import time

ec2_R_OHIO = boto3.resource('ec2', region_name= 'us-east-2')
ec2_C_OHIO = boto3.client('ec2', region_name= 'us-east-2')
ec2_R_NV = boto3.resource('ec2', region_name= 'us-east-1')
ec2_C_NV = boto3.client('ec2', region_name= 'us-east-1')
ec2_C_ELB = boto3.client('elb')
ec2_C_AUTOSCALING = boto3.client('autoscaling')


def createKeyOHIO():
    print("Criando chave KEY_OHIO \n")
    key_pair = ec2_R_OHIO.create_key_pair(KeyName='KEY_OHIO')

    actual_key = str(key_pair.key_material)

    with open('key_ohio.pem','w') as file:
        file.write(actual_key)


def createKeyNV():
    print("Criando chave KEY_OHIO \n")
    key_pair = ec2_R_NV.create_key_pair(KeyName='KEY_NV')

    actual_key = str(key_pair.key_material)

    with open('key_nv.pem','w') as file:
        file.write(actual_key)



# OHIO
def createInstConnector(private_IP, security_group):
    print("Subindo a máquina conectora\n")
    resp_con = ec2_R_OHIO.create_instances(
    ImageId='ami-0d5d9d301c853a04a',
    InstanceType='t2.micro',
    KeyName='KEY_OHIO',
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
    for i in resp_con:
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
    print("Subindo a máquina da DataBase\n")
    resp_db = ec2_R_OHIO.create_instances(

    ImageId='ami-0d5d9d301c853a04a', #OHIO IMAGE
    InstanceType='t2.micro',
    KeyName='KEY_OHIO',
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
    print("Alocando um IP elástico \n")
    allocation = ec2_C_NV.allocate_address(Domain='vpc')
    return allocation

def clearElasticIP():
    print('Liberando um IP elástico \n')
    response = ec2_C_NV.describe_addresses()
    aloc = response['Addresses'][0]['AllocationId']
    pubip = response['Addresses'][0]['PublicIp']


    response2 = ec2_C_NV.release_address(
    AllocationId=aloc,
)

# OHIO
def createSecurityGroupWithElasticIP(elastic_IP):
    print("Criando o security group\n")
    sec_group = ec2_R_OHIO.create_security_group(
    GroupName='Nott', Description='Projeto final')
    sec_group.authorize_ingress(
    CidrIp= elastic_IP+'/32',
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


# OHIO
def createSecurityGroup():
    print("Criando o security group: Caleb\n")
    sec_group = ec2_R_OHIO.create_security_group(
    GroupName='Caleb', Description='Projeto final')
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
def createSecurityGroupNV():
    print("Criando o security group: Jester\n")
    sec_group = ec2_R_NV.create_security_group(
    GroupName='Jester', Description='Projeto final')
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
def createInsOutsider(allocation_ID, pub_IP, sg_id):
    print("Subindo a instancia: Outsider\n")

    resp_out = ec2_R_NV.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='KEY_NV',
    MaxCount=1,
    MinCount=1,

    SecurityGroupIds=[
        sg_id,
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
    
        time.sleep(3)
        
    if instance_status == 'running':
        resp_ass = ec2_C_NV.associate_address(
        AllocationId=allocation_ID,
        InstanceId=tt[0].id,
        )

        return resp_ass, tt[0].id
    else:
        return 'erro'


# NORTH VIRGINIA
def createConnectorPublicIp(pub_IP, sg_id):
    print("Subindo a instancia: Brigde\n")
    resp_db = ec2_R_NV.create_instances(

    ImageId='ami-04763b3055de4860b',
    InstanceType='t2.micro',
    KeyName='KEY_NV',
    MaxCount=1,
    MinCount=1,

    SecurityGroupIds=[
        sg_id,
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
                    'Value': 'Bridge'
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


    return resp_db, tt[0].id, response.public_ip_address



# NORTH VIRGINIA
def createSecurityGroupLoadBalancer():
    print("Criando o security group: Beau\n")
    sec_group = ec2_R_NV.create_security_group(
    GroupName='Beau', Description='Load Balancer')
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
def createLoadBalancer(security_group):
    print("Criando o Load Balancer: Cadeuceus\n")
    responseLB = ec2_C_ELB.create_load_balancer(
    LoadBalancerName='Cadeuceus',
    Listeners=[
        {
            'Protocol': 'TCP',
            'LoadBalancerPort': 5000,
            'InstanceProtocol': 'TCP',
            'InstancePort': 5000,
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


# NORTH VIRGINIA
def createAutoScalling(instance_id):
    print("Criando o Auto Scalling Group: Fjord\n")
    waiter = ec2_C_NV.get_waiter('instance_running')

    waiter.wait(
    InstanceIds=[
        instance_id,
    ]
)

    responseAS = ec2_C_AUTOSCALING.create_auto_scaling_group(
    AutoScalingGroupName='Fjord',
    InstanceId=instance_id,
    MinSize=1,
    MaxSize=10,
    HealthCheckGracePeriod=300,
    LoadBalancerNames=[
        'Cadeuceus',
    ],
    Tags=[
        {
            'Key': 'Name',
            'Value': 'AutoScaller'
        }
    ]
)
    return responseAS


# OHIO ou NV
def terminateInstance(ec2_C, instance_name):

    num_ins = 0
    r = ec2_C.describe_tags()
    for i in r['Tags']:
        if i['Key'] == 'Name' and i['Value'] == instance_name:
            num_ins += 1


    response = ec2_C.describe_instances(Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                instance_name,
            ]
        },
    ])

    instanceId = []
    for i in response['Reservations']:
        for j in i['Instances']:
            instanceId.append(j['InstanceId'])
            

    print('Terminando a instancia: %s \n' % instance_name)
    if instanceId:
        ec2_C.terminate_instances(InstanceIds=instanceId)
        waiter = ec2_C.get_waiter('instance_terminated')

        waiter.wait(InstanceIds=instanceId)


# OHIO ou NV
def deleteSecurityGroup(ec2_C, sg_name):
    securityGroupId = ''
    try:
        sec_group = ec2_C.describe_security_groups(GroupNames=[sg_name])
        for i in sec_group['SecurityGroups']:
            securityGroupId = i['GroupId']
    except:
        print("Não foi encontrado nenhum security group\n")
    
    try:
        ec2_C.delete_security_group(GroupId=securityGroupId)
        print('Deletando o security group: %s \n' % (sg_name))
    except:
        print('Não foi possível deletar o security group: %s\n' % (sg_name))


# OHIO ou NV
def deleteLoadBalancer(lb_name):
    try:
        response = ec2_C_ELB.describe_load_balancers(
                LoadBalancerNames=[lb_name]
            )

        resp = response['LoadBalancerDescriptions'][0]['LoadBalancerName']
    except:
        print('Não existe nenhum load balancer com esse nome \n')
    try:        
        response = ec2_C_ELB.delete_load_balancer(
            LoadBalancerName=resp
)

        time.sleep(15)
        print('Deletando o load balancer: %s \n' % (lb_name))
    except:
        print('Não foi possível deletar o load balancer: %s\n' %(lb_name))    

def deleteAutoScaller(as_name):
    try:
        response = ec2_C_AUTOSCALING.delete_auto_scaling_group(
    AutoScalingGroupName=as_name,
    ForceDelete=True
)

        print('Deletando o auto scaling group: %s \n' % (as_name))
        while True:
            is_it_gone = ec2_C_AUTOSCALING.describe_auto_scaling_groups(
                AutoScalingGroupNames=[as_name]
            )

            yet = len(is_it_gone['AutoScalingGroups'])
            if yet == 0:
                break

            time.sleep(3)
        

    except:
        print('Não foi possível deletar o auto scaling group: %s \n' % (as_name))


def deleteLaunchConfiguration(lc_name):
    try:
        response = ec2_C_AUTOSCALING.delete_launch_configuration(
            LaunchConfigurationName=lc_name
        )
        print('Deletando o launch configuration: %s \n' % (lc_name))
    except:
        print('Não foi possível deletar o launch configuration: %s \n' % (lc_name))




# Limpa tudo antes de rodar o script de criação
clearElasticIP()
deleteAutoScaller('Fjord')
deleteLoadBalancer('Cadeuceus')
deleteLaunchConfiguration('Fjord')

try:
    terminateInstance(ec2_C_OHIO, 'Database')
except:
    print("Essa instancia ainda não existe!\n")

try:
    terminateInstance(ec2_C_OHIO, 'Connector')
except:
    print("Essa instancia ainda não existe!\n")

try:
    terminateInstance(ec2_C_NV, 'Outsider')
except:
    print("Essa instancia ainda não existe!\n")

try:
    terminateInstance(ec2_C_NV, 'Bridge')
except:
    print("Essa instancia ainda não existe!\n")


deleteSecurityGroup(ec2_C_OHIO, 'Caleb')
deleteSecurityGroup(ec2_C_OHIO, 'Nott')
deleteSecurityGroup(ec2_C_NV, 'Beau')
deleteSecurityGroup(ec2_C_NV, 'Jester')



# Cria os key pairs para as duas regiões
try:
    createKeyNV()
except:
    print("Chave KEY_NV já existe. \n")


try:
    createKeyOHIO()
except:
    print("Chave KEY_OHIO já existe. \n")


# Primeiro security group
first_sg = createSecurityGroup()
ohio_sg = createSecurityGroupNV()

# Sobe a maquina do DB
resp_db, response, pip = createInstDB(first_sg.id)

# Aloca um IP elástico
temp = createElasticIP()
elastic_IP = temp['PublicIp']
allocation_ID = temp['AllocationId']

# Cria um SG baseado no IP elástico
security_group = createSecurityGroupWithElasticIP(elastic_IP)

# Sobe o conector com o SG e o IP privado do DB 
oi , pp = createInstConnector(pip, security_group.id)
print(pp)
# Sobe a máquina 'outsider', correspondente a segunda cloud
resp, id_maquina = createInsOutsider(allocation_ID, pp, ohio_sg.id)

resp, id_maquina, ipp = createConnectorPublicIp(elastic_IP, ohio_sg.id)


# Cria um SG para o Load Balancer
lb_group = createSecurityGroupLoadBalancer()

# Cria o Load Balncer
i_lb_u = createLoadBalancer(lb_group)

# Cria Auto Scalling
createAutoScalling(id_maquina)