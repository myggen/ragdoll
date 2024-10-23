FROM nvidia/cuda:12.6.1-runtime-ubuntu24.04

#FROM nvidia/cuda:11.7.1-runtime-ubuntu18.04
#FROM nvidia/cuda:11.7.1-runtime-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install build-essential libcurl4-openssl-dev make automake git libjansson-dev libssl-dev autotools-dev wget curl python3 \
                       python3-pip python3-venv net-tools telnet

RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb

RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

RUN apt-get -y update

RUN curl -fsSL https://ollama.com/install.sh | sh


ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install --upgrade pip
RUN pip install requests
RUN pip install bs4
RUN pip install nltk
RUN pip install pypdf
RUN pip install ollama
RUN pip install chromadb
RUN pip install llama_index
RUN pip install llama_index.llms.ollama

EXPOSE 11434
EXPOSE 8000
ENV OLLAMA_HOST=0.0.0.0
#RUN groupadd -g 767 ollama

#RUN useradd ollama -r -d /home/ollama -u 767 -g 767 -s /bin/bash

COPY runserver.sh /usr/local/bin/runserver.sh

#USER ollama
#RUN ollama pull llama3.1:latest

#RUN nohup bash -c "python3 -m http.server --directory /home/espenm/space/projects/data/retningslinjer-met/ &" && sleep 4