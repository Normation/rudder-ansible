FROM debian:bullseye

ARG USER_ID=1000
ARG WORKSPACE="/tmp/ansible_collections/rudder/rudder"

COPY ci/user.sh .
RUN ./user.sh $USER_ID
COPY ci/requirements.txt .

RUN apt-get -y update && \
    apt-get install -y ansible git python3-pip shellcheck
RUN pip install -r requirements.txt

RUN mkdir -p ${WORKSPACE}
COPY . ${WORKSPACE}
WORKDIR "${WORKSPACE}"

ENTRYPOINT ["/bin/bash", "-c"]
