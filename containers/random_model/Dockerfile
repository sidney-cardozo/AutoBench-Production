# base parent image
FROM python:3.7.4-slim

# Set the working directory to /app
WORKDIR /app

# Copy the python script into the container at /app
COPY run_random.py /app

# bash setup
RUN apt-get update
RUN apt-get -y install sudo
RUN apt-get -y install postgresql
RUN apt-get -y install libpq-dev gcc
RUN apt-get -y install python3-dev
RUN pip3 install psycopg2~=2.6

# Install any needed packages specified in requirements.txt
#RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run run_random.py when the container launches
CMD ["python", "-u", "run_random.py"]
