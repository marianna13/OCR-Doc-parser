FROM nvidia/cuda:11.1.1-cudnn8-devel-ubuntu18.04
# use an older system (18.04) to avoid opencv incompatibility (issue#3524)

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \ 
    python3.7 python3.7-dev python3.7-distutils python3-pip && \
    apt-get install -y python3-opencv ca-certificates libzbar0 git wget sudo ninja-build && \
    apt install -y poppler-utils mupdf 

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
RUN update-alternatives --config python3

RUN ln -sv /usr/bin/python3.7 /usr/bin/python
 
RUN wget https://bootstrap.pypa.io/pip/3.6/get-pip.py && \
      python3.7 get-pip.py --user && \
      rm get-pip.py

# create a non-root user
ARG USER_ID=1000
RUN useradd -m --no-log-init --system  --uid ${USER_ID} appuser -g sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER appuser
WORKDIR /home/appuser



# install dependencies
# See https://pytorch.org/ for other options if you use a different version of CUDA
RUN pip3 install --user --upgrade pip
RUN pip3 install --user tensorboard cmake onnx
RUN pip3 install --user orch==1.10.1+cu111 torchvision==0.11.2+cu111 -f https://download.pytorch.org/whl/cu113/torch_stable.html
COPY requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt
ARG MUPDF=1.18.0

RUN pip3 install PyMuPDF==1.16.0


RUN pip3 install --user 'git+https://github.com/facebookresearch/fvcore'

# set FORCE_CUDA because during `docker build` cuda is not accessible
ENV FORCE_CUDA="1"
# This will by default build detectron2 for all common cuda architectures and take a lot more time,
# because inside `docker build`, there is no way to tell which architecture will be used.
ARG TORCH_CUDA_ARCH_LIST="Kepler;Kepler+Tesla;Maxwell;Maxwell+Tegra;Pascal;Volta;Turing"
ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN pip3 install 'git+https://github.com/facebookresearch/detectron2.git@v0.4#egg=detectron2' 

RUN sudo apt-get -y update && sudo apt-get -y install djvulibre-bin tesseract-ocr wget gcc
RUN sudo apt-get -y update && sudo apt-get -y install calibre
RUN pip3 install --upgrade pillow==6.2.2

# Set a fixed model cache directory.
ENV FVCORE_CACHE="/tmp"
WORKDIR /
