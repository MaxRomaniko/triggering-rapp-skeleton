FROM cellwizeplatform/chime-python:7.22

# set the working directory in the container
# WORKDIR /code

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "./main.py" ]
