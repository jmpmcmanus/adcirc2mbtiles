#!/usr/bin/env python
import os, sys, json, warnings
from functools import wraps
import numpy as np

from PyQt5.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMeshLayer,
    QgsMeshDatasetIndex,
    QgsMeshUtils,
    QgsProject,
    QgsRasterLayer,
    QgsRasterFileWriter,
    QgsRasterPipe,
    QgsCoordinateReferenceSystem,
    QgsColorRampShader,
    QgsRasterShader,
    QgsSingleBandPseudoColorRenderer,
    QgsRasterHistogram,
    QgsErrorMessage
)

# Ignore warning function
def ignore_warnings(f):
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response
    return inner

# Initialize application
def initialize_qgis_application():
    sys.path.append('/opt/conda/envs/mbtiles/share/qgis')
    sys.path.append('/opt/conda/envs/mbtiles/share/qgis/python/plugins')
    app = QgsApplication([], False)
    return (app)

# Add the path to processing so we can import it next
@ignore_warnings # Ignored because we want the output of this script to be a single value, and "import processing" is noisy
def initialize_processing(app):
    # import processing module
    import processing
    from processing.core.Processing import Processing

    # Initialize Processing
    Processing.initialize()
    return (app, processing)

# Convert mesh layer as raster and save as a GeoTiff
def exportRaster(parameters):
    # Open layer from infile 
    infile = parameters['INPUT_LAYER']
    meshfile = infile.strip().split('/')[-1]
    meshlayer = meshfile.split('.')[0]
    layer = QgsMeshLayer(infile, meshlayer, 'mdal')

    # Check if layer is valid
    if layer.isValid() is True:
        # Get parameters for processing
        dataset  = parameters['INPUT_GROUP'] 
        timestep = parameters['INPUT_TIMESTEP']
        mupp = parameters['MAP_UNITS_PER_PIXEL'] 
        extent = layer.extent()
        output_layer = parameters['OUTPUT_RASTER']
        width = extent.width()/mupp 
        height = extent.height()/mupp 
        crs = layer.crs() 
        crs.createFromSrid(4326)
        transform_context = QgsProject.instance().transformContext()
        output_format = QgsRasterFileWriter.driverForExtension(os.path.splitext(output_layer)[1])

        # Open output file for writing
        rfw = QgsRasterFileWriter(output_layer)
        rfw.setOutputProviderKey('gdal') 
        rfw.setOutputFormat(output_format) 

        # Create one band raster
        rdp = rfw.createOneBandRaster( Qgis.Float64, width, height, extent, crs)

        # Get dataset index
        dataset_index = QgsMeshDatasetIndex(dataset, timestep)

        # Regred mesh layer to raster
        block = QgsMeshUtils.exportRasterBlock( layer, dataset_index, crs,
                transform_context, mupp, extent) 

        # Write raster to GeoTiff file
        rdp.writeBlock(block, 1)
        rdp.setNoDataValue(1, block.noDataValue())
        rdp.setEditable(False)

        return(output_layer)

    if layer.isValid() is False: 
        raise Exception('Invalid mesh')

# Add color and set transparency to GeoTiff
def styleRaster(filename):
    # Create outfile name
    outfile = "".join(filename.strip().split('.raw'))

    # Open layer from filename
    rasterfile = filename.strip().split('/')[-1]
    rasterlayer = rasterfile.split('.')[0]
    rlayer = QgsRasterLayer(filename, rasterlayer, 'gdal')

    # Check if layer is valid
    if rlayer.isValid() is True:
        # Get layer data provider
        provider = rlayer.dataProvider()

        # Calculate histrogram
        provider.initHistogram(QgsRasterHistogram(),1,100)
        hist = provider.histogram(1)

        # Get histograms stats
        nbins = hist.binCount
        minv = hist.minimum
        maxv = hist.maximum

        # Create histogram array, bin array, and histogram index
        hista = np.array(hist.histogramVector)
        bins = np.arange(minv, maxv, (maxv - minv)/nbins)
        index = np.where(hista > 5)

        # Get bottom and top color values from bin values
        bottomcolor = bins[index[0][0]]
        topcolor = bins[index[0][-1]]

        # Calculate range value between the bottom and top color values
        if bottomcolor < 0:
            vrange = topcolor + bottomcolor
        else:
            vrange = topcolor - bottomcolor 

        # Calculate values for bottom middle, and top middle color values
        if rasterlayer == 'maxele':
            bottommiddle = vrange * 0.3333
            topmiddle = vrange * 0.6667
        else:
            bottommiddle = vrange * 0.375
            topmiddle = vrange * 0.75

        # Create list of color values
        valueList =[bottomcolor, bottommiddle, topmiddle, topcolor]

        # Create color dictionary
        if rasterlayer == 'maxele':
            colDic = {'bottomcolor':'#0000ff', 'bottommiddle':'#00ffff', 'topmiddle':'#ffff00', 'topcolor':'#ff0000'}
        else:
            colDic = {'bottomcolor':'#000000', 'bottommiddle':'#ff0000', 'topmiddle':'#ffff00', 'topcolor':'#ffffff'}

        # Create color ramp function and add colors
        fnc = QgsColorRampShader()
        fnc.setColorRampType(QgsColorRampShader.Interpolated)
        lst = [QgsColorRampShader.ColorRampItem(valueList[0], QColor(colDic['bottomcolor'])),\
               QgsColorRampShader.ColorRampItem(valueList[1], QColor(colDic['bottommiddle'])), \
               QgsColorRampShader.ColorRampItem(valueList[2], QColor(colDic['topmiddle'])), \
               QgsColorRampShader.ColorRampItem(valueList[3], QColor(colDic['topcolor']))]
        fnc.setColorRampItemList(lst)

        # Create raster shader and add color ramp function
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fnc)

        # Create color render and set opacity
        renderer = QgsSingleBandPseudoColorRenderer(provider, 1, shader)
        renderer.setOpacity(0.75)

        # Get output format
        output_format = QgsRasterFileWriter.driverForExtension(os.path.splitext(outfile)[1])

        # Open output file for writing
        rfw = QgsRasterFileWriter(outfile)
        rfw.setOutputProviderKey('gdal')
        rfw.setOutputFormat(output_format)

        # Add EPSG 4326 to layer crs
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(4326)

        # Create Raster pipe and set provider and renderer
        pipe = QgsRasterPipe()
        pipe.set(provider.clone())
        pipe.set(renderer.clone())

        # Get transform context
        transform_context = QgsProject.instance().transformContext()

        # Write to file
        rfw.writeRaster(
            pipe,
            provider.xSize(),
            provider.ySize(),
            provider.extent(),
            crs,
            transform_context
        )
    if not rlayer.isValid():
        raise Exception('Invalid raster')


app = initialize_qgis_application() 
app.initQgis()
app, processing = initialize_processing(app)

parameters = json.loads(sys.argv[1])
filename = exportRaster(parameters)
styleRaster(filename)

app.exitQgis()

