#!/bin/bash
# setup specific to apsviz-maps
docker run -ti --name adcirc2mbtiles_container --shm-size=4g \
  --volume /home/jmcmanus/Work/Surge/Data/storage:/home/mbtiles/storage \
  --volume /srv/mbtiles:/srv/mbtiles \
  -d adcirc2mbtiles_image /bin/bash 
