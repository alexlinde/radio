import xml.etree.ElementTree as ET
from urllib.request import urlopen

IMDA_BRANDS = 'http://www.bbc.co.uk/radio/imda/imda_brands.xml'
IMDA_TRANSPORTS = 'http://www.bbc.co.uk/radio/imda/imda_transports.xml'

class IMDA:
    def __init__(self):
        self._stations = []
        brands = ET.parse(urlopen(IMDA_BRANDS)).getroot()
        transports = ET.parse(urlopen(IMDA_TRANSPORTS)).getroot()
        for brand in brands.findall('./brand'):
            id = brand.attrib['id']
            title = brand.find('./title/short').text
            stream = transports.find(
                f"./brand[@refid='{id}']/transport/media[@type='dash']/stream[@physical='$intl']")
            if stream is not None:
                self._stations.append((title,stream.attrib['url']))

    @property
    def stations(self):
        return self._stations
