var portal = Portal('https://xxxxx.maps.arcgis.com');
var layer1 = Filter(FeatureSetByPortalItem(
    portal,
    "xxxxxxxxxxxxxxxxxxxxxxx",
    0,
    ["*"],
    true
),"LERRD = 'Relocation'");

var features = [];
var feat;

for (var t in layer1) {
    var att = Attachments(t)
	  var html = ''
    for (var a in att) {
       var oid = t['OBJECTID']
       var aid = att[a]['id']
       var name = att[a]['name']
       html = html + '<a href="https://services2.arcgis.com/xxxxxxxxxx/arcgis/rest/services/xxxxxxx/FeatureServer/0/' + oid + '/attachments/' + aid + '">' + name + '</a><br>'
    }
    
    feat = {
        attributes:{
            GlobalID : t['GlobalID'],
            Utility_ID : t['Utility_ID'],
            Owner : t['Owner'],
            C_Contract : t['C_Contract'],
            AOC_Tract : t['AOC_Tract'],
			      LERRD_ID : t['LERRD_ID'],
            htmlfield: html,
			i
        },
        'geometry': Geometry(t)
    }
    Push(features, feat)
}

var joinedDict = {
    fields: [
        { name: "GlobalID", type: "esriFieldTypeGUID" },
        { name: "Owner", type: "esriFieldTypeString" },     
        { name: "C_Contract", type: "esriFieldTypeString" },             
        { name: "AOC_Tract", type: "esriFieldTypeString" },
        { name: "htmlfield", type: "esriFieldTypeString" },
        { name: "Utility_ID", type: "esriFieldTypeString" },
		{ name: "LERRD_ID", type: "esriFieldTypeString" }
       
    ],
    'geometryType': "esriGeometryPolygon",
    'features':features
};

return FeatureSet(Text(joinedDict));
