## LAZ TO PRODUCTS

## Jason Jordan
## jason.jordan@usace.army.mil

## 8 Aug 2018


import arcpy, datetime, os, subprocess
from arcpy import *
from arcpy.sa import *
import arcpy.cartography as CA
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")


#Script start time
startTime = datetime.datetime.now()
print("\n" + "Script start time - " + startTime.strftime("%d %B %Y %H:%M:%S") + "\n")

#CUSTOMIZE===========================================================================================================================================

#INPUTS
inFolder = r'C:\Users\m2ecojj9\Desktop\LAS\LAS'                                                                                                               #Input folder containing LAZ/LAS files
inDEM = r''                                                                                                                                 #Enter a DEM path to skip LAZ/LAS conversion, else leave blank
outFolder=r'X:\ELEV\OPS\LE_Lewisville\2016_Lidar_Survey_1Ft'                                                                                                                           #Output folder to create DEM products
baseFileName = 'LE_2016'                                                                                                                     #Prefix file name for outputs
rawDataProjection = r'I:\PRJ\TXSP 4202 North Central US Feet\NAD 1983 StatePlane Texas N Central FIPS 4202 (US Feet).prj'
#rawDataProjection = r'D:\WGS 1984 Web Mercator (auxiliary sphere).prj'                                                                 #PRJ file of original LAS,LAZ, or DEM
nad83Projection = r'I:\PRJ\TXSP 4202 North Central US Feet\NAD 1983 StatePlane Texas N Central FIPS 4202 (US Feet).prj'                     #PRJ for NAD83/NAVD88 projection
nad27Projection = r'I:\PRJ\TXSP 4202 North Central US Feet\NAD 1927 StatePlane Texas N Central FIPS 4202.prj'                               #PRJ for NAD27/NGVD29 projection
inUnits = 'ft'                              #Units of inDEM if applicable

#LAKE INFO
conservationElevation = ''                 #Elevations to create lake contours, enter '' to skip
feeElevation = ''
easementElevation = ''

#LIDAR PARAMETERS
samplingValue = "1"  #Meters
workingLasDatasetBoundary = r''
#Constraint: 'path field function'
#workingLasDatasetSurfaceConstraint = "C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-flowline_utm14.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-flowline_utm15.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-line_utm14.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-line_utm15.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-rail_utm14.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-rail_utm15.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-trans_utm14.shp <None> Hard_Line;C:/Users/m2ecojj9/Downloads/fema_2006_140cm_breaklines/fema06-140cm-breaklines-trans_utm15.shp <None> Hard_Line"  #Only replace first string
workingLasDatasetSurfaceConstraint =''
workingLasDatasetCode =[2]  # 2 = Bare earth measurements; Ground elevation values

#OUTPUTS
projectNAD83 = 'no'                        #Enable or disable projections
projectNAD27 = 'yes'
createHillshade = 'no'                     #Create Hillshade
createASCII = 'no'                          #Create ASCII txt file
createWaterSurfaces = 'no'                 #Create polygons of water surfaces at 1' intervals
createHydrography = 'no'                   #Create GBD with basic hydrographic data

#HYDRO PARAMETERS
pourPoints = ''                           #Path to feature used for pour points, leave '' to automatically compute.
threshValue = .01                         #Decimal percent of maximum flow accumulation (.01 = 1%) to use as threshold. Lower values produce larger basins, smaller values extract smaller basins.
snapdistance = 200	                  #Distance to snap pour points to stream lines

#====================================================================================================================================================

if 'y' not in projectNAD83.lower() and 'y' not in projectNAD27.lower():
    raise Exception('One of the projections must be enabled')

if os.path.isfile(r'C:/Program Files/QGIS 3.0\OSGeo4W.bat') == True:
    beginningGdal = r'C:/Program Files/QGIS 3.0\OSGeo4W.bat gdalwarp '
elif os.path.isfile(r'C:\Program Files\QGIS 2.18\bin\OSGeo4W.bat') == True:
    beginningGdal = r'C:\Program Files\QGIS 2.18\bin\OSGeo4W.bat gdalwarp '
else:
    raise Exception('QGIS must be installed')

arcpy.env.workspace = outFolder

statePlane = arcpy.Describe(nad83Projection).SpatialReference.name.split('FIPS_')[1][0:4]

if 'Texas' in arcpy.Describe(nad83Projection).SpatialReference.name:
    state = 'TX'
elif Oklahoma in arcpy.Describe(nad83Projection).SpatialReference.name:
    state = 'OK'
elif Mississippi in arcpy.Describe(nad83Projection).SpatialReference.name:
    state = 'MS'
elif New_Mexico in arcpy.Describe(nad83Projection).SpatialReference.name:
    state = 'NM'

def waterSurfaces(pathNad,setDEM):
    print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Water Surfaces")

    contourList = range(int(conservationElevation), int(easementElevation)+10)
    polyList = []
    for i in contourList:
        arcpy.sa.ContourList(setDEM, pathNad + baseFileName + '_Contours.gdb/tempContours_'+ str(i), i)

    for dirpath, dirnames, filenames in arcpy.da.Walk(pathNad + baseFileName + '_Contours.gdb'):
        for file in filenames:
            if 'tempContours' in file:
                with arcpy.da.UpdateCursor(pathNad + baseFileName + '_Contours.gdb/'+ file, "SHAPE@LENGTH") as cursor:
                    for row in cursor:
                        if row[0] < 500:
                            cursor.deleteRow()
                CA.SimplifyLine(pathNad + baseFileName + '_Contours.gdb/'+ file, pathNad + baseFileName + '_Contours.gdb/'+ file + '_Smoothed','BEND_SIMPLIFY', '20 Feet')
                try:
                    arcpy.FeatureToPolygon_management(pathNad + baseFileName + '_Contours.gdb' + '/'+ file + '_Smoothed',pathNad + baseFileName + '_Contours.gdb/'+ file + '_Poly')
                    arcpy.AddField_management(pathNad + baseFileName + '_Contours.gdb/' + file + '_Poly', 'Contour','SHORT')
                    with arcpy.da.SearchCursor(pathNad + baseFileName + '_Contours.gdb/' + file + '_Poly', ['SHAPE@AREA']) as cursor:
                        largest = 0
                        for row in cursor:
                            if row[0] > largest:
                                largest = row[0]
                    with arcpy.da.UpdateCursor(pathNad + baseFileName + '_Contours.gdb/' + file + '_Poly', ['Contour','SHAPE@AREA']) as cursor:
                        largest = largest * .1
                        for row in cursor:
                            if row[1] >= largest:
                                row[0] = int(str(file)[13:16])
                                cursor.updateRow(row)
                            else:
                                cursor.deleteRow()
                    polyList.append(pathNad + baseFileName + '_Contours.gdb/' + file + '_Poly')
                except:
                    pass
    arcpy.Merge_management(polyList,pathNad + baseFileName + '_Contours.gdb/WaterSurfaces')

    for dirpath, dirnames, filenames in arcpy.da.Walk(pathNad + baseFileName + '_Contours.gdb'):
        for file in filenames:
            if 'tempContours' in file:
                arcpy.Delete_management(pathNad + baseFileName + '_Contours.gdb/'+ file)

def gdal(DEM, fSource, fTarget, outDEM):
    if 'f' in inUnits:
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Projecting to NAD83/NAVD88")
        callString = beginningGdal + inDEM + ' ' + outDEM + ' -s_srs epsg:' + fSource + ' -t_srs epsg:' + fTarget + ' -q'
        subprocess.check_call(callString)
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Skipping Conversion to Meters")
    if 'm' in inUnits:
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Projecting to NAD83/NAVD88")
        callString = beginningGdal + inDEM + ' ' + DEM + ' -s_srs epsg:' + fSource + ' -t_srs epsg:' + fTarget + ' -q'
        subprocess.check_call(callString)
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Converting to Meters")
        inRas = Raster(DEM)
        outRas = inRas * 3.2808333
        outRas.save(outDEM)
        arcpy.Delete_management(DEM)

def hydro(DEM,path):
    arcpy.env.workspace = path
    hydroDem = Fill(DEM)
    hydroDem.save("fill")
    fdr = FlowDirection("fill")
    fdr.save("fdr")
    fac = FlowAccumulation("fdr")
    fac.save("fac")
    getThreshold = arcpy.GetRasterProperties_management("fac", "MAXIMUM")
    threshold = float(getThreshold.getOutput(0))*threshValue
    strm = SetNull("fac",1,"Value <" + str(threshold))
    strm.save("strm")

    if pourPoints == "":
        StreamToFeature("strm", "fdr", "tempDrainage","NO_SIMPLIFY")
        arcpy.FeatureVerticesToPoints_management("tempDrainage","pourPoints","END")
        outlet = SnapPourPoint("pourPoints", "fac", snapdistance)
        outlet.save("outlet")
    else:
        outlet = SnapPourPoint(pourPoints, "fac", snapdistance)
        outlet.save("outlet")

    wshed = Watershed("fdr", "outlet")
    wshed.save("wshed")
    strlnk = StreamLink("strm","fdr")
    strlnk.save("strlnk")
    catchmentGrid = Watershed("fdr", "strlnk")
    catchmentGrid.save("CatchmentGrid")
    StreamToFeature("strlnk", "fdr", "DrainageLine","NO_SIMPLIFY")
    arcpy.RasterToPolygon_conversion("CatchmentGrid", "Catchments", "NO_SIMPLIFY")
    arcpy.Dissolve_management("Catchments", "Basin")

source = str(arcpy.SpatialReference(rawDataProjection).factoryCode) + '+6360'
contourList = []
contourList.append(conservationElevation)
contourList.append(feeElevation)
contourList.append(easementElevation)


rasterList = []
if inDEM == '':
    try:
        subprocess.check_call(r'\\155.84.56.200\RefGIS\SWF_GIS_TOOLS\LAStools\bin\laszip.exe ' + inFolder + '\*.laz')
    except:
        pass
    inDEM = inFolder + '/' + baseFileName + '_Merged.img'
    for dirpath, dirnames, filenames in os.walk(inFolder):
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Converting LAZs to IMGs")

        for file in filenames:
            if '.las' in file and '.lasx' not in file:
                try:
                    basename = arcpy.Describe(dirpath + '/' + file).baseName
                    workingLasDataset = inFolder + '/' + basename + '_FULL.lasd'
                    workingLasDatasetLyr = inFolder + '/' + basename + '_FULL_Layer.lyr'

                    # Execute CreateLasDataset
                    arcpy.management.CreateLasDataset(input=inFolder + '/' + file, out_las_dataset=workingLasDataset, folder_recursion="NO_RECURSION", in_surface_constraints=workingLasDatasetSurfaceConstraint, spatial_reference=rawDataProjection, compute_stats="COMPUTE_STATS", relative_paths="RELATIVE_PATHS", create_las_prj="ALL_FILES")

                    # Make LAS Dataset Layer
                    arcpy.MakeLasDatasetLayer_management(in_las_dataset=workingLasDataset, out_layer=os.path.basename(workingLasDatasetLyr).replace(".lyr",""), class_code="2", return_values="", no_flag="INCLUDE_UNFLAGGED", synthetic="INCLUDE_SYNTHETIC", keypoint="INCLUDE_KEYPOINT", withheld="EXCLUDE_WITHHELD", surface_constraints="")
                    # Execute SaveToLayerFile
                    arcpy.SaveToLayerFile_management(os.path.basename(workingLasDatasetLyr).replace(".lyr",""), workingLasDatasetLyr, "ABSOLUTE")

                    # LAS Dataset to Raster (LASD set to ground)
                    raster01Name = inFolder + '/' +basename + '.img'
                    arcpy.conversion.LasDatasetToRaster(in_las_dataset=os.path.basename(workingLasDatasetLyr).replace(".lyr",""), out_raster=raster01Name, value_field="ELEVATION", interpolation_type="BINNING AVERAGE LINEAR", data_type="FLOAT", sampling_type="CELLSIZE", sampling_value=samplingValue, z_factor="1")
                    rasterList.append(inFolder + '/' +basename + '.img')

                    arcpy.Delete_management(workingLasDatasetLyr)
                    arcpy.Delete_management(workingLasDataset)

                except Exception as Errdesc:
                    print(Errdesc)
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Merging IMG Files")

    arcpy.MosaicToNewRaster_management(rasterList,inFolder, baseFileName + '_Merged.img', rawDataProjection, '32_BIT_FLOAT',samplingValue,1,'LAST','FIRST')
    
try:
    os.makedirs(outFolder + '/' + 'METADATA')
except:
    pass

if 'y' in projectNAD83.lower():
    target = str(arcpy.SpatialReference(nad83Projection).factoryCode) + '+6360'
    DEM83 = inFolder + '/' +baseFileName + '_NAVD99.img'
    pathNad83 = outFolder + '/' + state + statePlane + 'NAD83_NAVD88_FeetUS/' 
    setDEM83 = pathNad83 + baseFileName + '_NAD_1983_NAVD_1988_Elevation_3Ft.img'
    os.makedirs(pathNad83)
    arcpy.CreateFileGDB_management(pathNad83,os.path.basename(baseFileName + '_Contours'))
    gdal(DEM83,source,target,setDEM83)
    for contour in [1,2,5,10]:
        print (datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Producing " + str(contour) + ' Ft Contours (NAVD88)')
        nad88Contour = pathNad83 + baseFileName + '_Contours.gdb/' + baseFileName + '_NAD_1983_NAVD_1988_Elevation_' + str(contour) + 'ft_Contours'
        arcpy.Contour_3d(setDEM83, out_polyline_features=nad88Contour, contour_interval=contour, base_contour="0", z_factor="1")
    if 'y' in createHillshade.lower():
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Hillshade (NGVD88)")
        outHillShade = Hillshade(setDEM83, "315", "45", "NO_SHADOWS", "1")
        outHillShade.save(pathNad83 + baseFileName + '_NAD_1983_NAVD_1988_Hillshade.img')
    if conservationElevation != '':
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Lake Contours (NAVD88)")
        lakeContours83 = pathNad83 + baseFileName + '_Contours.gdb/' + baseFileName + '_NAD_1983_NAVD_1988_Elevation_Contours'
        arcpy.gp.ContourList_sa(setDEM83, lakeContours83, contourList)
    if 'y' in createASCII.lower():
        print (datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Creating ASCII (NAVD88)")
        arcpy.RasterToASCII_conversion(setDEM83, pathNad83 + baseFileName + '_NAD_1983_NAVD_1988_Elevation.asc')
    if 'y' in createWaterSurfaces.lower():
        waterSurfaces(pathNad83,setDEM83)
    if 'y' in createHydrography:
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Hydrography Dataset (NAVD88)")
        arcpy.CreateFileGDB_management(pathNad83,os.path.basename(baseFileName + '_Hydrography'))
        hydro(setDEM83,pathNad83 + baseFileName + '_Hydrography.gdb/')

arcpy.env.workspace = outFolder

if 'y' in projectNAD27.lower():
    target2 = str(arcpy.SpatialReference(nad27Projection).factoryCode) + '+5702'
    DEM27 = inFolder + '/' +baseFileName + '_NGVD29.img'
    pathNad27 = outFolder + '/' + state + statePlane + 'NAD27_NGVD29_FeetUS/'
    setDEM27 = pathNad27 + baseFileName + '_NAD_1927_NGVD_1929_Elevation_3Ft.img' 
    os.makedirs(pathNad27)
    arcpy.CreateFileGDB_management(pathNad27,os.path.basename(baseFileName + '_Contours'))    
    gdal(DEM27,source,target2,setDEM27)
    for contour in [1,2,5,10]:
        print (datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Producing " + str(contour) + ' Ft Contours (NGVD29)')
        nad88Contour = pathNad27 + baseFileName + '_Contours.gdb/' + baseFileName + '_NAD_1927_NGVD_1929_Elevation_' + str(contour) + 'ft_Contours'
        arcpy.Contour_3d(setDEM27, out_polyline_features=nad88Contour, contour_interval=contour, base_contour="0", z_factor="1")
    if 'y' in createHillshade.lower():
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Hillshade (NGVD29)")
        outHillShade = Hillshade(setDEM27, "315", "45", "NO_SHADOWS", "1")
        outHillShade.save(pathNad27 + baseFileName + '_NAD_1927_NGVD_1929_Hillshade.img')
    if conservationElevation != '':
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Lake Contours (NGVD29)")
        lakeContours29 = pathNad27 + baseFileName + '_Contours.gdb/' + baseFileName + '_NAD_1927_NGVD_1929_Elevation_Contours'
        arcpy.gp.ContourList_sa(setDEM27, lakeContours29, contourList)
        with arcpy.da.UpdateCursor(lakeContours29, "SHAPE@LENGTH") as cursor:
            for row in cursor:
                if row[0] < 1000:
                    cursor.deleteRow()
    print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Smoothing Lake Contours")
    arcpy.SmoothLine_cartography(in_features=lakeContours29, out_feature_class=lakeContours29 + "_smoothed", algorithm="PAEK", tolerance="20 Feet", endpoint_option="FIXED_CLOSED_ENDPOINT", error_option="NO_CHECK")
    if 'y' in createASCII.lower():
        print (datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Creating ASCII (NGVD29)")
        arcpy.RasterToASCII_conversion(setDEM27, pathNad27 + baseFileName + '_NAD_1927_NGVD_1929_Elevation.asc')
    #if 'y' in createWaterSurfaces.lower():
        #waterSurfaces(pathNad27,setDEM27)
    if 'y' in createHydrography:
        print(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S")+ " Generating Hydrography Dataset (NGVD29)")
        arcpy.CreateFileGDB_management(pathNad27,os.path.basename(baseFileName + '_Hydrography'))
        hydro(setDEM27,pathNad27 + baseFileName + '_Hydrography.gdb/')
            
arcpy.Delete_management(inDEM)

