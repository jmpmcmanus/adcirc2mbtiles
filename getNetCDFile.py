#!/usr/bin/env python
import sys, os, wget

def getDataFile(dirpath, storm, url):
    # Create storm netcdf directory path
    if not os.path.exists(dirpath+storm):
        mode = 0o755
        os.makedirs(dirpath+storm, mode)

    # Get infilename and download netcdf file
    infilename = url.strip().split('/')[-1]
    outfilename = wget.download(url, dirpath+storm+'/'+infilename)

    # Create storm tiff directory path
    tifpath = dirpath.split('/')[0:-2] 
    tifpath.append('tiff')
    tifpath = "/".join(tifpath) 
    if not os.path.exists(tifpath+'/'+storm):
        mode = 0o755
        os.makedirs(tifpath+'/'+storm, mode)

    # Create storm mbtile directory path
    mbtilepath = dirpath.split('/')[0:-2]
    mbtilepath.append('mbtile')
    mbtilepath = "/".join(mbtilepath)
    if not os.path.exists(mbtilepath+'/'+storm):
        mode = 0o755
        os.makedirs(mbtilepath+'/'+storm, mode)

dirpath = '/home/mbtiles/storage/netCDF/'
storm = sys.argv[1] 
url = sys.argv[2]

getDataFile(dirpath, storm, url)

