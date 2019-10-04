# AutoBench
Many businesses use machine learning models in various applications, but testing and choosing the right model for a particular use case can be time-consuming and tedious. This project simplifies the process of model evaluation by implementing a workflow for benchmarking multiple models in tandem and outputting visualizations of metrics for model comparison.

The code included in this repository specifically evaluates three sentiment analysis models, but the concept can be extended to apply to other models and machine learning tasks.

## Tech Stack
Tools: AWS S3, AWS EC2, Airflow, PostgreSQL, Docker, Dash

Each process in the workflow (PostgreSQL database, loading test data into PostgreSQL, each model to be tested, calculation of benchmarking metrics, and Dash web app) is containerized using Docker, and the containers are deployed on AWS EC2. AWS S3 is used for storage of necessary files, and the Docker images created for the sentiment analysis models are stored at hub.docker.com/chughto/testmodels. Airflow monitors the S3 bucket to detect when the `docker-compose.yml` file is uploaded, then deploys it on the EC2 instance. The testing data and model results are stored in PostgreSQL tables, and benchmarking metrics are visualized using Dash.

## Running this example
The file `docker-compose.yml` is set up to run three sentiment analysis models, a PostgreSQL database, and calculation of some benchmarking metrics. This file can be run on an AWS EC2 instance which has an associated Elastic IP and has Docker installed, and is compatible with both `docker-compose` and `docker stack deploy` methods. When the benchmarking results are ready, the Dash visualizations can be viewed at \<INSTANCE ELASTIC IP\>:8080.

### To run manually

*Using `docker-compose`*: Make sure that Docker Compose is installed on the instance (see `install-docker-compose.sh` for commands to install Docker Compose). In the same directory as the file `docker-compose.yml`, run the command `docker-compose up`. To stop the process, press `CTL+d` and then run the command `docker-compose down` (this will also stop the Dash web app).

*Using `docker stack deploy`*: In the same directory as the file `docker-compose.yml`, run the command `docker swarm init` to initialize swarm mode with the current instance as the manager. If running across multiple instances, update and install Docker on the other instances, then copy the join token command generated when the swarm was initialized on the manager and run it on each worker instance. To deploy the stack, run the command `docker stack deploy -c docker-compose.yml AutoBench` on the manager instance. The status of the process can be check by running `docker service ls`. Completed tasks will show 0/1 Replicas active (the db and dash tasks will run continuously). To stop the process, run `docker stack rm AutoBench`.

### To run using airflow

Create an S3 bucket named `auto-bench`, and upload the folder `airflow` and the file `configure-new-instance.sh`. On an EC2 instance running Amazon AMI, run the command `aws s3 sync s3://auto-bench/ .`, then `bash configure-new-instance.sh` (this may take a couple of minutes). The final command in the bash file starts a docker swarm with the current machine as a manager. If running across multiple instances, update and install Docker on the other instances, then copy the join token command generated when the swarm was initialized on the manager and run it on each worker instance. You can go to \<INSTANCE PUBLIC IP\>:8050 to check the Airflow UI to see that the `deploy_task_on_file_upload` workflow is active. Upload the `docker-compose.yml` file to the auto-bench s3 bucket, which will trigger the workflow to deploy. Once the benchmarking results are ready, they can be viewed at \<INSTANCE PUBLIC IP\>:8080. 
