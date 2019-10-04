from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.sensors import S3KeySensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
schedule = timedelta(minutes=10)

args = {
    'owner': 'airflow',
    'start_date': datetime(2019, 10, 1),
    'depends_on_past': False,
    'retries': 0,
    # 'retry_delay': timedelta(minutes=5),
    # 'execution_timeout': timedelta(minutes=10),
}

dag = DAG(
    dag_id='deploy_stack_on_file_upload',
    schedule_interval=schedule,
    default_args=args,
    catchup=False,
)

file_sensor = S3KeySensor(
    task_id='s3_key_sensor_task',
    poke_interval=60 * 1, # seconds
    timeout=60 * 10, # seconds
    bucket_key="s3://auto-bench/docker-compose.yml",
    bucket_name=None,
    wildcard_match=False,
    dag=dag
)

move_file = BashOperator(
    task_id="move_yml",
    bash_command="aws s3 mv s3://auto-bench/docker-compose.yml /home/ec2-user/docker-compose.yml",
    dag=dag
)

rm_prev_stack = BashOperator(
    task_id="rm_prev_stack",
    bash_command="docker stack rm AutoBench",
    dag=dag
)

docker_prune = BashOperator(
    task_id="docker_prune",
    bash_command="docker system prune -f",
    dag=dag
)

update_images = BashOperator(
    task_id="update_images",
    bash_command="docker pull chughto/testmodels -a",
    dag=dag
)

deploy_stack = BashOperator(
    task_id="deploy_stack",
    bash_command="docker stack deploy -c /home/ec2-user/docker-compose.yml AutoBench",
    dag=dag
)

file_sensor >> move_file >> rm_prev_stack >> docker_prune >> update_images >> deploy_stack
