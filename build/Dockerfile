# set the base image
FROM continuumio/anaconda3

# author
MAINTAINER Jim McManus

# extra metadata
LABEL version="1.0"
LABEL description="adcirc2mbtiles image with Dockerfile."

# Set user environment info
ENV USER=mbtiles GROUP=mbtiles USER_ID=1001 USER_GID=1001 CONDAENV=mbtiles

# update sources list, and install basic apps, one per line for better caching
RUN apt-get clean && apt-get update &&\
    apt-get install -qy nano \
    libgl1 \
    libgl1-mesa-dev \
    vim \
    aria2 

# define working directory
WORKDIR /home/$USER

# add user, and group mbtiles, specific to adcirc-db and general setup, respectively
RUN groupadd -r -g $USER_GID $GROUP && useradd --no-log-init -r -u $USER_ID -g $USER_GID $USER 

# Make RUN commands use `bash --login`:
SHELL ["/bin/bash", "--login", "-c"]

###### Create run directory for QGis
RUN mkdir -p /run/user/$USER_ID &&\
 chown -R $USER:$GROUP /run/user/$USER_ID &&\
 chmod 0700 /run/user/$USER_ID

# Create the environment, and initialize conda in bash config files:
COPY environment.yml .
RUN conda env create -f environment.yml &&\
 conda init bash &&\
 conda activate $CONDAENV &&\
 conda update -n base -c defaults conda -y --quiet

# Copy bashrc to home directory as .bashrc
ADD bashrc /home/$USER/.bashrc

# Activate conda environment, and clone gdal2mbtiles repository
RUN conda activate $CONDAENV &&\
  mkdir /home/mbtiles/repos &&\
  cd /home/mbtiles/repos &&\
  git clone https://github.com/pchynoweth/gdal2mbtiles.git &&\
  git clone https://github.com/jmpmcmanus/adcirc2mbtiles.git 

# change owner and group to data for /home/data
RUN chown -R $USER:$GROUP /home/$USER
