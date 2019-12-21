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

## Install nvidia apex
#RUN git clone https://github.com/NVIDIA/apex && \
#    cd apex && \
#    pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./ && \
#    cd ..

# Install python libs
RUN pip install --no-cache-dir --upgrade pip
RUN mkdir /server
COPY ./requirements.txt /server/requirements.txt
RUN pip install --no-cache-dir -r /server/requirements.txt


# === PROJECT INFO SETTINGS ===
ARG BUILD_DATE=None
ARG SOURCE=None
ARG BRANCH=None
ARG VCS_REF=None

ENV BUILD_DATE ${BUILD_DATE}
ENV SOURCE ${SOURCE}
ENV BRANCH ${BRANCH}
ENV VCS_REF ${VCS_REF}
# === PROJECT INFO SETTINGS ===


ARG PROJECT_DIRPATH="/project"
ENV PROJECT_DIRPATH ${PROJECT_DIRPATH}
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIRPATH}"

WORKDIR ${PROJECT_DIRPATH}

# Dev target
FROM base as dev

ARG DOCKER_USER_NAME="root"
ARG DOCKER_USER_PASS="pass"
ARG DOCKER_SSH_PORT=22
ENV APP_ENV="development"

# SSH settings
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd && \
    echo "${DOCKER_USER_NAME}:${DOCKER_USER_PASS}" | chpasswd && \
    sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config && \
    sed "s@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g" -i /etc/pam.d/sshd

EXPOSE ${DOCKER_SSH_PORT}
CMD ["/usr/sbin/sshd", "-D"]

# Prod target
FROM base as prod

ENV APP_ENV="production"
# TODO: COPY project instead mounting
# TODO: CMD create entrypoint to workflow