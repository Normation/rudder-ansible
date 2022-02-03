FROM debian:bullseye
ARG USER_ID=1000
COPY ci/user.sh .
RUN ./user.sh $USER_ID
COPY ci/requirements.txt .

RUN apt-get -y update && \
    apt-get install -y ansible git python3-pip shellcheck
RUN pip install -r requirements.txt

# Uncomment if you want to use it on your machine
#RUN mkdir -p /tmp/ansible_collections/rudder/rudder
#COPY . /tmp/ansible_collections/rudder/rudder/
#WORKDIR "/tmp/ansible_collections/rudder/rudder/"

ENTRYPOINT ["/bin/bash", "-c"]
