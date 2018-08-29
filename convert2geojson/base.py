# -*- coding: utf-8 -*-
# base packages
import pandas as pd
import json
import re
import os

# visualization packages
import ipyleaflet
from ipywidgets import HTML


class Convert2GeoJson(object):
    """
    Turn a dataframe containing point data into a geojson formatted python dictionary

    df : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
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

        self.df = self.df.dropna(subset=[self.lat, self.lon], axis=0, inplace=False)

    def _replace(self, file, pattern, subst):
        # Read contents from file as a single string
        file_handle = open(file, 'r')
        file_string = file_handle.read()
        file_handle.close()

        # Use re package to allow for replacement (also allowing for (multiline) REGEX)
        file_string = (re.sub(pattern, subst, file_string))

        # Write contents to file.
        # Using mode 'w' truncates the file.
        file_handle = open(file, 'w')
        file_handle.write(file_string)
        file_handle.close()

    def _getLookupDict(self, column):
        retDict = {x: y for x, y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

    def _getTranslateDict(self, column):
        retDict = {y: x for x, y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

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
            if row[self.lon] != 'None' and row[self.lat] != 'None':
                feature = {'type': 'Feature',
                           'properties': {'style': {}},
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

        # add attribution and description
        # geojson['attribution'] = attribution
        # geojson['description'] = description

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

    def display(self, style=False):
        cartoLight = {
            'url': 'http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
            'max_zoom': 16,
            'attribution': 'Carto Light',
            'name': 'Carto.Light'
            }
        latList = [x for x in self.df[self.lat].values if type(x) not in [str, list, dict]]
        latMean = sum(latList)/len(latList)
        lonList = [x for x in self.df[self.lon].values if type(x) not in [str, list, dict]]
        lonMean = sum(lonList)/len(lonList)
        center = [latMean, lonMean]
        zoom = 5
        self.displayMap = ipyleaflet.Map(
            center=center,
            zoom=zoom,
            layers=(ipyleaflet.basemap_to_tiles(cartoLight), )
            )
        if not style:
            self.geojsonLayer = ipyleaflet.GeoJSON(data=self.geojsonDict)
            self.displayMap.add_control(ipyleaflet.LayersControl())
            self.displayMap.add_layer(self.geojsonLayer)
            return self.displayMap
        elif style == 'grouped':
            tableTemplate = """<table style="width:100%"><caption>Values at point:</caption><tr><th>key</th><th>value</th></tr>ROWS</table>"""
            rowTemplate = """<tr><td>KEY</td><td>VALUE</td></tr>"""
            markers = []
            for _, row in self.df.iterrows():
                markerTemp = ipyleaflet.Marker(location=[row[self.lat], row[self.lon]], draggable=False)
                # popup information
                message = HTML()
                rowList = []
                for x, y in row.iteritems():
                    rowList.append(re.sub('VALUE', str(y), re.sub('KEY', str(x), rowTemplate)))
                message.value = re.sub('ROWS', ''.join(rowList), tableTemplate)
                message.placeholder = ''
                message.description = ''
                markerTemp.popup = message
                # style of marker
                markerTemp.style = {'icon': 'warning'}
                markers.append(markerTemp)
            self.markerCluster = ipyleaflet.MarkerCluster(markers=markers)
            self.displayMap.add_control(ipyleaflet.LayersControl())
            self.displayMap.add_layer(self.markerCluster)
            return self.displayMap
