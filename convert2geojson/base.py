# -*- coding: utf-8 -*-
# base packages
import pandas as pd
import json
import re
import os
import shutil

# visualization packages
import ipyleaflet
from ipywidgets import HTML, Layout
from jinja2 import Environment, FileSystemLoader
from IPython.display import HTML as displayHTML


class Convert2GeoJson(object):
    """
    Turn a dataframe containing point data into a geojson formated python dictionary

    dataframe : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
        (will be shown as popup information)
    lat : the name of the column in the dataframe that contains latitude data
    lon : the name of the column in the dataframe that contains longitude data
    """
    def __init__(
            self, dataframe, properties,
            lat='latitude', lon='longitude'
            ):
        self.df = dataframe
        self.rawDF = dataframe
        self.geojsonDict = {}
        self.properties = properties
        self.lat = lat
        self.lon = lon

        colorList = 'Red Green Yellow Blue Orange Purple Cyan Magenta Lime Pink Teal Lavender Brown Maroon Olive Coral Navy Grey'
        self.colors = colorList.lower().split(' ')

        self.df = self.df.dropna(subset=[self.lat, self.lon], axis=0, inplace=False).fillna('None')
        self.current_dir = os.path.dirname(os.path.realpath(__file__))

    def _getLookupDict(self, column):
        retDict = {x: y for x, y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

    def _getTranslateDict(self, column):
        retDict = {y: x for x, y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

    def _replace(self, file, pattern, subst):
        # Read contents from file as a single string
        file_handle = open(file, 'r')
        file_string = file_handle.read()
        file_handle.close()

        # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
        file_string = (re.sub(pattern, subst, file_string))

        # Write contents to file.
        # Using mode 'w' truncates the file.
        file_handle = open(file, 'w')
        file_handle.write(file_string)
        file_handle.close()

    def convert(
            self,
            visible_name=False,
            attribution='Implemented: <a target="_blank" href="http://www.topoi.org">Topoi</a> and <a target="_blank" href="https://www.mpiwg-berlin.mpg.de">MPIWG</a>',
            description='Displaying GeoJson Data from Pandas Dataframe',
            debug=False
            ):

        lookUps = {}
        keyTranslate = {}

        dfTemp = pd.DataFrame()

        if not visible_name:
            visible_name = {x: ' '.join(x.split('_')) for x in self.properties}

        # translate repeating values to dict
        for key in self.properties:
            if key != 'ObjID' and len(self.df[key].value_counts()) < 21:
                keyTranslate = self._getTranslateDict(key)
                lookUps[key] = self._getLookupDict(key)
                dfTemp[key] = self.df[key].apply(lambda row: keyTranslate[row])
            else:
                dfTemp[key] = self.df[key]

        if debug:
            print(lookUps)

        retDict = {}

        # construct field values
        for cl in self.properties:
            if cl in lookUps.keys():
                retDict[cl] = {'lookup': lookUps[cl], 'name': visible_name[cl]}
            else:
                retDict[cl] = {'name': visible_name[cl]}
        if debug:
            print(retDict)

        dfTemp[self.lon] = self.df[self.lon]
        dfTemp[self.lat] = self.df[self.lat]

        # create a new python dict to contain our geojson data, using geojson format
        geojson = {'type': 'FeatureCollection', 'features': [], 'properties': {'fields': {}, 'attribution': attribution, 'description': description}}

        # loop through each row in the dataframe and convert each row to geojson format
        for _, row in dfTemp.iterrows():
            # create a feature template to fill in
            if type(row[self.lon]) == float and type(row[self.lat]) == float:
                # if row[self.lon] not in ['None',None] and row[self.lat] not in ['None',None]:
                feature = {'type': 'Feature',
                           'properties': {},
                           'geometry': {'type': 'Point', 'coordinates': []},
                           }

                # fill in the coordinates
                feature['geometry']['coordinates'] = [row[self.lon], row[self.lat]]

                # for each column, get the value and add it as a new feature property
                for prop in self.properties:
                    feature['properties'][prop] = row[prop]

                # add this feature (aka, converted dataframe row) to the list of features inside our dict
                geojson['features'].append(feature)

                # add lookup properties
                geojson['properties']['fields'] = retDict

        self.geojsonDict = geojson

        return self

    def geojson(self):
        return self.geojsonDict

    def save(self, name='data.geojson', path='.'):
        # geojson_dict = self.df2geojson()
        geojson_str = json.dumps(self.geojsonDict, indent=2)

        with open(os.path.join(path, name), 'w') as output_file:
            output_file.write(geojson_str)

        return os.path.join(path, name)

    def _generateMarkers(self):
        popupTemplate = """
        <head>
        <style>
        table {
            border: 1px solid black;
            border-radius: 25px;
        }
        </style>
        </head>
        <body>
        <table style="width:100%">
              <tr>
                <th>Key</th>
                <th>Value</th>
              </tr>
              ROWS
            </table>

        </body>
        """
        # tableTemplate = """<table style="width:100%"><tr><th>key</th><th>value</th></tr>ROWS</table>"""
        rowTemplate = """<tr><td>KEY</td><td>VALUE</td></tr>"""
        markers = []
        for _, row in self.df.iterrows():
            if type(row[self.lon]) == float and type(row[self.lat]) == float:
                markerTemp = ipyleaflet.Marker(location=[row[self.lat], row[self.lon]], draggable=False)
                # popup information
                message = HTML()
                rowList = []
                for x, y in row.iteritems():
                    if x in self.properties:
                        str_x = re.escape(str(x))
                        str_y = re.escape(str(y))
                        rowTemp = re.sub('VALUE', str_y, re.sub('KEY', str_x, rowTemplate))
                        rowTemp = re.sub(r'\\(.)', r'\1', rowTemp)
                        rowList.append(rowTemp)
                message.value = re.sub(r'\\(.)', r'\1', re.sub('ROWS', ''.join(rowList), popupTemplate))
                message.placeholder = ''
                message.description = ''
                markerTemp.popup = message
                # style of marker
                markerTemp.layout = {'padding': '1px'}
                markers.append(markerTemp)
        return markers

    def _renderHTML(self, groupCategory, path, pageTitle='GeoJson Map', inputPath='html/template'):
        environment = Environment(loader=FileSystemLoader([os.path.join(self.current_dir, inputPath)]), trim_blocks=True, lstrip_blocks=True)
        template = environment.get_template(path)
        return template.render(
            geojsonPath='./data.geojson',
            title=pageTitle,
            pieCategory=groupCategory,
            popupProperties=list(self.properties),
            basemapURL=self.basemap['url'],
            centerLat=self.center[0],
            centerLon=self.center[1],
            zoom=self.zoom
            )

    def _writeHTML(self, groupCategory, pageTitle, outputTemplate='index.html', outputPath='html/static'):
        outputFullPath = os.path.join(os.path.abspath('.'), outputPath)
        template_name, _ = os.path.splitext(os.path.join(outputFullPath, '{0}.html'.format(outputTemplate)))

        if not os.path.exists(outputFullPath):
            os.makedirs(outputFullPath)

        geoJsonFile = self.save(name='data.geojson', path=outputPath)

        with open(os.path.join(outputFullPath, outputTemplate), 'w') as f:
            f.write(self._renderHTML(
                path=outputTemplate,
                groupCategory=groupCategory,
                pageTitle=pageTitle
                )
            )

    def _writeCSS(self, groupCategory, colorDict=False, outputPath='html/static'):
        cssFiles = shutil.copy(
            os.path.join(self.current_dir, 'html/template/clusterpies.css'),
            outputPath)

        markerTemplate = '.category-NUMBER{\n  fill: COLOR1;\n  stroke: COLOR2;\n  background: COLOR1;\n  border-color: COLOR2;\n}\n'
        markerString = ''

        fieldValueDict = self.geojsonDict['properties']['fields'][groupCategory]['lookup']

        if colorDict:
            for cl in colorDict.values():
                self.colors.remove(cl)
            for number, value in fieldValueDict.items():
                if value in colorDict.keys():
                    color = colorDict[value]
                    markerString += re.sub('NUMBER', str(number), re.sub('COLOR[12]', color, markerTemplate))
                else:
                    color = self.colors.pop(-1)
                    markerString += re.sub('NUMBER', str(number), re.sub('COLOR[12]', color, markerTemplate))
        else:
            for number, value in fieldValueDict.items():
                color = self.colors.pop(-1)
                markerString += re.sub('NUMBER', str(number), re.sub('COLOR[12]', color, markerTemplate))

        regPat = re.compile('(?<=marker categories begin[*]/\n)(.+)(?=\n/[*]marker categories end)', flags=re.DOTALL)
        markerDestination = re.findall(regPat, open(cssFiles).read())[0]
        self._replace(cssFiles, markerDestination, markerString)

    def display(
            self,
            basemap=False,
            mapLayout=False,
            style=False,
            groupBy=False,
            colorDict=False,
            pageTitle='GeoJSON map',
            outputPath='html/static'
            ):
        if basemap:
            self.basemap = basemap
        else:
            self.basemap = {
                'url': 'https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
                'max_zoom': 16,
                'attribution': '<a href="https://carto.com">Carto Light NoLabels</a>',
                'name': 'Carto Light'
                }
        latList = [x for x in self.df[self.lat].values if type(x) not in [str, list, dict]]
        latMean = sum(latList)/len(latList)
        lonList = [x for x in self.df[self.lon].values if type(x) not in [str, list, dict]]
        lonMean = sum(lonList)/len(lonList)
        self.center = [latMean, lonMean]
        self.zoom = 5
        self.displayMap = ipyleaflet.Map(
            center=self.center,
            zoom=self.zoom,
            layers=(ipyleaflet.basemap_to_tiles(self.basemap), )
            )
        if mapLayout:
            self.displayMap.layout = mapLayout
        if not style:
            markers = self._generateMarkers()
            for marker in markers:
                self.displayMap.add_layer(marker)
            return self.displayMap
        elif style == 'grouped':
            markers = self._generateMarkers()
            self.markerCluster = ipyleaflet.MarkerCluster(markers=markers)
            self.displayMap.add_control(ipyleaflet.LayersControl())
            self.displayMap.add_layer(self.markerCluster)
            return self.displayMap
        elif style == 'pie':
            if not groupBy:
                raise KeyError('Please add groupBy=COLNAME. You need to specify the column containing the categories for the pie chart.')
            html = self._writeHTML(groupCategory=groupBy, pageTitle=pageTitle, outputPath=outputPath)
            css = self._writeCSS(groupCategory=groupBy, colorDict=colorDict, outputPath=outputPath)
            print('Your map has been generated at\n\t"/html/static/index.html".\nDue to CORS issues, most browsers will not load the GeoJSON in an Iframe correctly.\nPlease open the map in a seperate browser window.')
            return displayHTML("<iframe allowfullscreen=”true” mozallowfullscreen=”true” webkitallowfullscreen=”true” height=550px; width=100% src='./html/static/index.html'> <iframe>")
