FROM nvidia/cuda:10.1-cudnn7-devel AS base
MAINTAINER "mikhail.chernyshev@x5.ru"
ARG DEBIAN_FRONTEND=noninteractive

# Install python3.7 with pip
RUN apt-get update && apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get install -y \
    python3.7 \
    python3.7-dev \
    python3-pip

# Set python3.7 and pip as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install other stuff
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libturbojpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install python libs
RUN pip install --no-cache-dir --upgrade pip
RUN mkdir /server

# === PROJECT INFO SETTINGS ===
ARG BUILD_DATE
ARG SOURCE
ARG BRANCH
ARG VCS_REF

ENV BUILD_DATE ${BUILD_DATE}
ENV SOURCE ${SOURCE}
ENV BRANCH ${BRANCH}
ENV VCS_REF ${VCS_REF}
# === PROJECT INFO SETTINGS ===

ARG PROJECT_DIRPATH
ENV PROJECT_DIRPATH ${PROJECT_DIRPATH}
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIRPATH}"
WORKDIR ${PROJECT_DIRPATH}



# DEVELOPMENT
FROM base as development
COPY ./requirements/dev-requirements.txt /server/dev-requirements.txt
RUN pip install --no-cache-dir -r /server/dev-requirements.txt

# TODO: move apex to requirements.txt
# Install nvidia apex
RUN git clone https://github.com/NVIDIA/apex && \
    cd apex && \
    pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./ && \
    cd ..

# SSH settings
ARG DOCKER_USER_NAME
ARG DOCKER_USER_PASS
ARG DOCKER_SSH_PORT
RUN echo "${DOCKER_USER_NAME}:${DOCKER_USER_PASS}" | chpasswd
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd && \
    echo "${DOCKER_USER_NAME}:${DOCKER_USER_PASS}" | chpasswd && \
    sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config && \
    sed "s@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g" -i /etc/pam.d/sshd
EXPOSE ${DOCKER_SSH_PORT}
CMD ["/usr/sbin/sshd", "-D"]


## PRODUCTION
#FROM base as production
#COPY . ${PROJECT_DIRPATH}
#
#COPY ./requirements/prod-requirements.txt /server/prod-requirements.txt
#RUN pip install --no-cache-dir -r /server/prod-requirements.txt
#

# TODO: move apex to requirements.txt
## Install nvidia apex
#RUN git clone https://github.com/NVIDIA/apex && \
#    cd apex && \
#    pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./ && \
#    cd ..
