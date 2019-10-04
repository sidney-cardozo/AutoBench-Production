sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo yum install -y gcc-c++ python-devel python-setuptools
sudo yum install -y postgresql postgresql-server postgresql-devel postgresql-contrib postgresql-docs
sudo service postgresql initdb
sudo service postgresql start
pip install --user "apache-airflow[s3,postgres]"
sudo -u postgres createuser -s ec2-user
sudo -u postgres createdb ec2-user
sudo -u postgres createdb airflow
pip uninstall -y marshmallow-sqlalchemy
pip install --user marshmallow-sqlalchemy==0.17.1
airflow initdb
airflow webserver -p 8050 -D
airflow scheduler -D
sudo docker swarm init
