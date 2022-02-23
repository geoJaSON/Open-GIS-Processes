#This takes a Pandas dataframe and syncs an ArcGIS Online or Portal feature service to it.

#Current limitations:
# -Geometry is currently not enabled
# -Multiple types of date fields may cause errors
# -Tables are not supported yet
# -This pushes all records in a dataframe, currently working on a way to only push rows with different values from original data.

# # ItemID, Pandas Dataframe, layer ID (defaults to 0)
# update() # REQUIRED -> ItemID, Dataframe of updated data, OPTIONAL -> layer=<layerID>, xfield=<Longitude field>, yfield=<Latitude field>, timeformat=<String format of time columns>
# loadTarget()   # OPTIONAL ->>   username = <AGOL Username>, password=<AGOL Password>
# stageData()   # REQUIRED ->>  Dictionary of {columnSource: columnTarget}. The first item MUST BE the join field
# pushUpdates()  # Commit the update

# EXAMPLE
# updates = update('s2323r3fdffa83fo32fgona73r08',df_from_smartsheet)
# updates.loadTarget('jason.jordan@galv')
# updates.stageData(smartsheet_columns_to_agol_columns)
# updates.pushUpdates()



from arcgis.gis import GIS
import time
import datetime


class update:

    updates_to_push = []
    adds_to_push = []

    def __init__(self, itemID, sourceData, layer=0, xfield='', yfield='', timeformat=''):
        self.itemID = itemID
        self.sourceData = sourceData
        self.layer = layer
        self.xfield = xfield
        self.yfield = yfield
        self.timeformat = timeformat
        if len(self.xfield) > 0 and len(self.yfield) > 0:
            self.spatial = True

    def loadTarget(self, username='', password=''):           #This is designed to connect to an IWA-enabled portal if no username is specified.
        if len(username) < 1:
            print('Logged into uCOP')
            self.gis = GIS(
                "https://xxxxxxxxxxxxxx/s0portal")
        else:
            print('Logged into AGOL')
            self.gis = GIS(username=username, password=password)

        layer_item = self.gis.content.get(self.itemID)
        layers = layer_item.layers
        self.flayer = layers[self.layer]
        fset = self.flayer.query()
        self.features = fset.features
        self.column_types = {f['name']: f['type']
                             for f in self.flayer.properties.fields}
        self.oid = list(self.column_types.keys())[list(
            self.column_types.values()).index('esriFieldTypeOID')]

    def stageData(self, column_map):
        self.column_map = column_map
        foundColumns = [value for value in self.column_types if value in list(
            self.column_map.values())]
        self.column_types = {k: self.column_types[k] for k in foundColumns}
        print('The following columns were successfully matched:')
        for k, v in self.column_types.items():
            print(k, f"({v})")
        try:
            self.sourceData = self.sourceData.rename(self.column_map, axis=1)
            self.sourceData = self.sourceData[list(self.column_types.keys())]
        except Exception as e:
            print('Column Map Error:', e)
        self.feature_keys = {f.attributes[list(self.column_map.keys())[
            0]]: f.attributes[self.oid] for f in self.features}

    def formatValue(self, value, vtype):
        self.value = value
        self.vtype = vtype
        if str(self.value) in ['nan', ''] or self.value is None:
            return None

        else:
            if self.vtype == 'esriFieldTypeString':
                return str(self.value)
            elif self.value == 'esriFieldTypeInteger':
                try:
                    return int(self.value)
                except:
                    return int(float(self.value))
            elif self.value == 'esriFieldTypeDouble':
                return float(self.value)
            elif self.value == 'esriFieldTypeDate':
                try:
                    if len(self.timeformat) > 0:
                        return int(time.mktime((value).timetuple()) * 1000 + 63200000)
                    else:
                        return int(time.mktime(datetime.strptime(str(value), self.timeformat).timetuple())) * 1000 + 63200000
                except:
                    return None

    def assembleUpdates(self, row):
        self.row = row
        try:
            edit_feature = {
                self.oid: self.feature_keys[row[list(self.column_map.keys())[0]]]}
            for k, v in self.column_types.items():
                edit_feature[k] = self.formatValue(row[k], v)
            feat = {'attributes': edit_feature}
            self.updates_to_push.append(feat)
            print(str(row.name + 1) + "/" + str(len(self.sourceData)), end="\r")

        except KeyError:
            add_feature = {list(self.column_map.keys(
            ))[0]: row[list(self.column_map.keys())[0]]}
            for k, v in self.column_types.items():
                add_feature[k] = self.formatValue(row[k], v)
            feat = {'attributes': add_feature}
            self.adds_to_push.append(feat)
            print(str(row.name + 1) + "/" + str(len(self.sourceData)), end="\r")

    def pushUpdates(self):
        self.sourceData.apply(lambda row: self.assembleUpdates(row), axis=1)
        self.update_result = self.flayer.edit_features(
            updates=self.updates_to_push, adds=self.adds_to_push, rollback_on_failure=False)
        print(self.update_result)
# %%
