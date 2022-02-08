FROM debian:bullseye
ARG USER_ID=1000
COPY ci/user.sh .
COPY ci/requirements.txt .

RUN ./user.sh $USER_ID

RUN apt-get -y update && \
    apt-get install -y git python3-pip
RUN pip install -r requirements.txt

# Uncomment if you want to use it on your machine
#RUN mkdir -p /tmp/ansible_collections/rudder/rudder
#COPY . /tmp/ansible_collections/rudder/rudder/
#WORKDIR "/tmp/ansible_collections/rudder/rudder/"

ENTRYPOINT ["/bin/bash", "-c"]