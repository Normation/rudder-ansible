FROM debian:bullseye
ARG USER_ID=1000
COPY ci/user.sh .
RUN ./user.sh $USER_ID

RUN apt-get -y update && \
    apt-get install -y ansible git python3-pip
RUN pip install pycodestyle voluptuous yamllint

ENTRYPOINT ["/bin/bash", "-c"]