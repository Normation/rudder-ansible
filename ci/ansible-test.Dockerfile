FROM debian:bullseye

ARG USER_ID=1000

COPY ci/user.sh .
RUN ./user.sh $USER_ID
COPY ci/requirements.txt .

RUN apt-get -y update && \
    apt-get install -y ansible git python3-pip shellcheck
RUN pip install pycodestyle voluptuous yamllint

ENTRYPOINT ["/bin/bash", "-c"]
