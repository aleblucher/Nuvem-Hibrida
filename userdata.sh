Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
sudo apt update -y
sudo apt-get install language-pack-pt -y
sudo apt-get install python3-pip -y
git clone https://github.com/aleblucher/Nuvem-Hibrida
sudo apt-get install python-pip python-dev libmysqlclient-dev -y
sudo apt install mysql-server -y
sudo apt install python3-venv -y
mkdir my_flask_app
cd my_flask_app
python3 -m venv venv
source venv/bin/activate
pip install Flask
cd ..
cd Nuvem-Hibrida
pip install requests
export SERVER="http://localhost:5000"; python connector.py


sudo apt -y update
sudo apt -y install mysql-server
sudo apt install language-pack-pt -y
sudo apt install python3-pip -y
git clone https://github.com/aleblucher/Nuvem-Hibrida
sudo apt -u install python-pip python-dev
sudo pip3 install flask
cd Nuvem-Hibrida
sudo mysql < ./scripts/123.sql
sudo pip3 install requests

export SERVER="http://localhost:5000"; python connector.py



# export SERVER="http://localhost:5000"
# python connector.py
