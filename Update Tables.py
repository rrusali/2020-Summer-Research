from PyQt5.QtCore import QVariant

layer = iface.activeLayer()
#layer_provider=layer.dataProvider()
#layer_provider.addAttributes([QgsField("Length",QVariant.Double)])
#layer.updateFields()

with open("C:/Users/Ryan Rusali/Desktop/test.txt", 'r') as f:
    content = f.read()

with edit(layer):
    for feature in layer.getFeatures():
        feature['Length'] = content
        layer.updateFeature(feature)