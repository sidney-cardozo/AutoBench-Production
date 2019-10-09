# base parent image
FROM python:3.7.4-slim

# Set the working directory to /app
WORKDIR /app

# add files
COPY aclImdb /app/aclImdb
COPY make_imdb_psql.py /app

# bash setup
RUN apt-get update
RUN apt-get -y install sudo
RUN apt-get -y install postgresql
RUN apt-get -y install libpq-dev gcc
RUN pip3 install psycopg2~=2.6
RUN apt-get -y install python3-dev

# Run make_imdb_psql.py when the container launches
CMD ["python", "-u", "make_imdb_psql.py"]
