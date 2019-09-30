# AutoBench
Many businesses use machine learning models in various applications, but testing and choosing the right model for a particular use case can be time-consuming and tedious. This project simplifies the process of model evaluation by implementing a workflow for benchmarking multiple models in parallel and outputting visualizations of metrics for model comparison.

The code included in this repository specifically evaluates three sentiment analysis models, but the concept can be extended to apply to other models and machine learning tasks.

## Tech Stack
Tools: AWS S3, AWS EC2, PostgreSQL, Docker, Dash

Each process in the workflow (PostgreSQL database, each model to be tested, calculation of benchmarking metrics) is containerized using Docker, and the containers are deployed on AWS EC2. AWS S3 is used for storage of necessary files, and Docker images are stored on dockerhub. The testing data and model results are stored in PostgreSQL tables, and benchmarking metrics are visualized using Dash.

## Running this example
The file `docker-compose.yml` is set up to run three sentiment analysis models, a PostgreSQL database, and calculation of some benchmarking metrics. This file can be run on an AWS EC2 instance which has an associated Elastic IP and has Docker Compose installed (see `install-docker-compose.sh` for commands to install Docker Compose) by transferring the file to the instance and running the command `docker-compose up`. When the models have finished running, the Dash visualizations can be viewed at <INSTANCE ELASTIC IP>:8080

To stop the process, press `CTL+d` and then run the command `docker-compose down`.
