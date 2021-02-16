FROM ubuntu:18.04

ENV PYTHONUNBUFFERED TRUE

ARG tarball_name
ARG requirements
ARG setup

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    fakeroot \
    ca-certificates \
    dpkg-dev \
    g++ \
    python3-dev \
    openjdk-11-jdk \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1

RUN pip install --no-cache-dir torchserve

COPY dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh

RUN mkdir -p /home/model-server/ && mkdir -p /home/model-server/tmp
COPY config.properties /home/model-server/config.properties

WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp
ADD ${tarball_name}.tar.gz /home/model-server/code
RUN if [ -f code/requirements.txt ] && [ ${requirements} = True ]; then pip install --no-cache-dir -r code/requirements.txt; fi
RUN if [ -f code/setup.py ] && [ ${setup} = True ]; then pip install --no-cache-dir -e code; fi

ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD ["serve"]
