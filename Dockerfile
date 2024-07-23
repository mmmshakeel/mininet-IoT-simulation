# Use Ubuntu as the base image
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    build-essential \
    pkg-config \
    libboost-system-dev \
    libboost-filesystem-dev \
    libboost-thread-dev \
    libboost-chrono-dev \
    libboost-test-dev \
    libevent-dev \
    libhiredis-dev \
    libjansson-dev \
    python3 \
    python3-pip \
    tcpdump \
    tshark \
    iputils-ping \
    iproute2 \
    hping3 \
    slowhttptest \
    openvswitch-switch

ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Mininet from source
RUN git clone https://github.com/mininet/mininet && \
    cd mininet && \
    util/install.sh -a

# Install Python packages
RUN pip3 install pandas scapy

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/usr/local/lib/python3.8/dist-packages"

# Start Open vSwitch services
RUN service openvswitch-switch start && \
    /usr/share/openvswitch/scripts/ovs-ctl start

# Copy the Mininet topology script
COPY topology.py /topology.py

# Copy the processing script
COPY process_pcap.py /process_pcap.py

# Set the entrypoint to run Mininet
ENTRYPOINT ["python3", "/topology.py"]
