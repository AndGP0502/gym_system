from lxml import etree

xml_path = "factura_firmada.xml"
xsd_path = "sri/xsd/factura_V2.1.0.xsd"

xml_doc = etree.parse(xml_path)
xsd_doc = etree.parse(xsd_path)

schema = etree.XMLSchema(xsd_doc)

if schema.validate(xml_doc):
    print("XML válido contra XSD")
else:
    print("XML NO válido contra XSD")

    for error in schema.error_log:
        print(error.message)