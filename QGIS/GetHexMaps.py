shp_path = 'D:/Research Files/Orientational Order Parameter/Counties/Alabama/Alabama_counties.shp'
file_path = 'D:/Research%20Files/Orientational%20Order%20Parameter/Counties/Alabama/Alabama_2hex_order.csv'
uri = 'file:///%s?type=csv&maxFields=10000&detectTypes=no&geomType=none&subsetIndex=no&watchFile=no' % (file_path)

csv = QgsVectorLayer(uri, 'temp', 'delimitedtext')
QgsProject.instance().addMapLayer(csv)

shp = QgsVectorLayer(shp_path, 'alabama', 'ogr')
QgsProject.instance().addMapLayer(shp)

shpField = 'COUNTYFP'
csvField = 'County'

joinObject = QgsVectorLayerJoinInfo()
joinObject.setJoinLayerId(csv.id())
joinObject.setJoinFieldName(csvField)
joinObject.setTargetFieldName(shpField)
joinObject.setJoinLayer(csv)
shp.addJoin(joinObject)

#project = QgsProject.instance()
#layout = QgsPrintLayout(project)
#layout.initializeDefaults()
#layout.setName("PRINT")
##project.layoutManager().addLayout(layout)
#
#map = QgsLayoutItemMap(layout)
#map.setRect(QRectF(20, 20, 200, 100))  # The Rectangle will be overridden below
#
## Extent
#map.setExtent(shp.extent())
#layout.addLayoutItem(map)

# Move & Resize
#   Demo of map origin and map size in mixed units
map.attemptMove(QgsLayoutPoint(0.25, 0.25, QgsUnitTypes.LayoutInches))
map.attemptResize(QgsLayoutSize(250,  200, QgsUnitTypes.LayoutMillimeters))


#map = QgsLayoutItemMap(layout)
## Set map item position and size (by default, it is a 0 width/0 height item placed at 0,0)
#map.attemptMove(QgsLayoutPoint(5,5, QgsUnitTypes.LayoutMillimeters))
#map.attemptResize(QgsLayoutSize(200,200, QgsUnitTypes.LayoutMillimeters))
## Provide an extent to render
#map.zoomToExtent(iface.mapCanvas().extent())
#layout.addLayoutItem(map)
#print(shp.extent())
#map.setExtent(shp.extent())
#layout.addLayoutItem(map)


myStyle = QgsStyle().defaultStyle()
defaultColorRampNames = myStyle.colorRampNames()
ramp = myStyle.colorRamp(defaultColorRampNames[-6])
myRenderer = QgsGraduatedSymbolRenderer.Quantile(10)
myRenderer.setSourceColorRamp(ramp)
shp.setRenderer(myRenderer)
shp.triggerRepaint()
myRenderer.updateColorRamp(ramp)