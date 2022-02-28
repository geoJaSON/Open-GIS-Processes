
import arcpy
import os
import datetime
import csv
import sys

#inputWorkspace = "C:\User\Documents"
inputWorkspace = arcpy.GetParameterAsText(0)

#inputWorkspace = "C:\User\Documents"
outPath = arcpy.GetParameterAsText(1)

#task == "Broken Layer Inventory"
#task = "Total Layer Inventory"
task = arcpy.GetParameterAsText(2)

#Process to run for total inventory
def totalInventory(inputWorkspace):
    brokeCount = 0                                                          #Set initial counters for end report
    emptyCount = 0
    mxdCount = 0
    layerCount = 0
    for dirpath, dirnames, filenames in os.walk(inputWorkspace):            #Walks through files (arcpy.da.walk does not register map files)
        for filename in filenames:  
            if '.mxd' in filename:                                          #Tests if file is *.mxd
                mxdCount += 1                                               #Increment mxd counter for each map file
                writer.writerow((filename,))                                    #Write section (MXD file name)
                mxd = arcpy.mapping.MapDocument(filename)
                for df in arcpy.mapping.ListDataFrames(mxd):
                    for layer in arcpy.mapping.ListLayers(mxd, "", df):
                        if not layer.isGroupLayer:                              #test if is a group layer. Group layers break the process
                            if not layer.isBroken:                              #test if layer is broken. Proceeds to inventory if not. If yes, it skips below
                                layerCount += 1                                 #update layer counter
                                desc = arcpy.Describe(layer)                        #fetch layer description
                                if desc.dataType == "FeatureLayer":                     #tests if is a feature layer. Raster layers are below
                                    if arcpy.GetCount_management(layer)[0] == "0":                  #tests if the layer is empty in order to note
                                        writer.writerow(("", layer.name, desc.shapeType, desc.path, str(desc.SpatialReference.name), "EMPTY LAYER"))
                                        emptyCount += 1                                 #increase empty layer counter
                                    else:                                                           #if it is not empty
                                        writer.writerow(("", layer.name, desc.shapeType, desc.path, str(desc.SpatialReference.name)))
                                if desc.dataType == "RasterLayer":                                  #if layer is raster
                                    writer.writerow(("", layer.name, "" ,desc.path, str(desc.SpatialReference.name)))

                            elif layer.isBroken:                                                    #test if layer is broken
                                writer.writerow(("", layer.name, "","*******IS BROKEN*****"))       #notate broken layer
                                brokeCount += 1                                                     #increase broken layer counter

                            else:
                                pass
                            
                    writer.writerow(("",))                                      #skip line between MXD sections
                   
    #Write final counts
    writer.writerow((str(mxdCount) + " map files found",))
    writer.writerow((str(layerCount) + " good layers found",))                
    writer.writerow((str(emptyCount) + " empty layers found",))
    writer.writerow((str(brokeCount) + " broken layers found",))

#Process to run broken inventory, lines are same as above but skips the layers that are not broken or empty
def brokenInventory(inputWorkspace):
    brokeCount = 0
    for dirpath, dirnames, filenames in os.walk(inputWorkspace):  
        for filename in filenames:  
            if '.mxd' in filename:
                writer.writerow((filename,))
                mxd = arcpy.mapping.MapDocument(filename)
                for df in arcpy.mapping.ListDataFrames(mxd):
                    for layer in arcpy.mapping.ListLayers(mxd, "", df):
                        if layer.isBroken:
                            writer.writerow(("", layer.name))
                            brokeCount += 1
                writer.writerow(("",))

    writer.writerow((str(brokeCount) + " broken layers found",))    

#Process to run emtpy layer inventory , lines are same as above but only tests if a layer is empty                         
def emptyInventory(inputWorkspace):
    emptyCount = 0    
    for dirpath, dirnames, filenames in os.walk(inputWorkspace):  
        for filename in filenames:  
            if '.mxd' in filename:
                writer.writerow((filename,))
                mxd = arcpy.mapping.MapDocument(filename)
                for df in arcpy.mapping.ListDataFrames(mxd):
                    for layer in arcpy.mapping.ListLayers(mxd, "", df):
                        if not layer.isGroupLayer:
                            if not layer.isBroken:
                                desc = arcpy.Describe(layer)
                                if desc.dataType == "FeatureLayer":
                                    if arcpy.GetCount_management(layer)[0] == "0":
                                        writer.writerow(("", layer.name, desc.shapeType, desc.path, str(desc.SpatialReference.name), "EMPTY LAYER"))
                                        emptyCount += 1
                writer.writerow(("",))
         
    writer.writerow((str(emptyCount) + " empty layers found",))

#initial workflow    
try:
    outPathSet = str(outPath) + "\MXD " + task +" " + str(datetime.date.today()) + ".csv"
    
    #Test if Python 3x or 2x
    if (sys.version_info >= (3, 0)):
        exp = [outPathSet, "w",1,'cp1252',"strict",""]
    elif (sys.version_info < (3, 0)):
        exp = [outPathSet,"wb"]
        
    outFile = open(*exp)                                #set path to create .csv output file with write permission
    writer = csv.writer(outFile)                                #initiates the csv.write module

    writer.writerow((task,))                                    #print header starting with the task
    writer.writerow(("Input Workspace: '" + inputWorkspace,))   #Print workspace header
    writer.writerow((str(datetime.date.today()),))              #Print date header
    writer.writerow("")                                         #skip row

    if task == "Total Layer Inventory":                         #Run operation based on task parameter, will either run total, empty, or broken Inventory funcitons
        totalInventory(inputWorkspace)
        
    elif task == "Broken Layer Inventory":
        brokenInventory(inputWorkspace)
        
    else:
        emptyInventory(inputWorkspace)

    outFile.close()                                             #End read/write with output .csv file
    
except Exception as ErrDesc:
    print(ErrDesc)
