#!/bin/bash
# Example run

REPOSPATH=/home/mbtiles/repos
STORAGEPATH=/home/mbtiles/storage

python $REPOSPATH/ADCIRC2mbtiles/getNetCDFile.py 'florence' 'http://tds.renci.org:8080/thredds/fileServer/tc/florence/00/nc_inundation_v9.99_w_rivers/pod.penguincomputing.com/OwiHindcast/hindcast/maxele.63.nc'
python $REPOSPATH/ADCIRC2mbtiles/mesh2tiff.py '{"INPUT_EXTENT" : "-97.85833,-60.040029999999994,7.909559999999999,45.83612", "INPUT_GROUP" : 1, "INPUT_LAYER" : "/home/mbtiles/storage/netCDF/florence/maxele.63.nc", "INPUT_TIMESTEP" : 0,  "OUTPUT_RASTER" : "/home/mbtiles/storage/tiff/florence/maxele.raw.63.tif", "MAP_UNITS_PER_PIXEL" : 0.001}'
python $REPOSPATH/ADCIRC2mbtiles/publisher.py "Start Processing MBTiles for florence"
