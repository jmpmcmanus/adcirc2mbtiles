# ADCIRC2mbtiles
## Converts ADCIRC mode 63 netCDF file to mbtile files

This repository is designed to run in a docker container. When creating the docker container you need to define
a directory which will be added to the container, as the volume (/home/mbtiles). This location should have enough  
disk space to process the input files, intermediate files, and the mbtile files. After cloning this repository you  
should follow the commands below.

#### Build docker images

##### Change directory to build

cd ADCIRC2mbtiles/build

##### Edit Docker file

The user mbtiles, in the docker container, needs to have the same user id, and group id as yours, to be able to 
write to the volume, so you need to replace user id, and gid 1324 with your own, on line:

ENV USER=mbtiles USER_ID=1324 USER_GID=1324 CONDAENV=mbtiles

##### Edit createcontainer.sh file

replace directory path /projects/regionthree/apsviz_mbtiles/storage, with the directory path where you plane to process
the data.

##### Run to build docker image, and container:

./buildimage.sh  
./createcontainer.sh  

##### You now should be able to access the container shell, as root, using the following command:

docker exec -it adcirc2mbtiles_container bash  

##### To access the container as the mbtiles user, use the following command:

docker exec -it --user mbtiles adcirc2mbtiles_container bash

##### Activate mbtiles conda environment

conda activate mbtiles  

##### You can now run the example 

/home/mbtiles/repos/ADCIRC2mbtiles/examplerun.sh

##### You can also run the example from outside of the container on the host machine, using the following
command:

docker exec -t --user mbtiles adcirc2mbtiles_container /bin/bash -c "source /home/mbtiles/.bashrc; conda activate mbtiles; /home/mbtiles/repos/ADCIRC2mbtiles/examplerun.sh

