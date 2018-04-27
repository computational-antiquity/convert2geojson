# -*- coding: utf-8 -*-
import pandas as pd
import requests
import json
import re
import io
import ipywidgets as widgets
import ast
from collections import ChainMap
import difflib
#from ipywidgets import HBox
from IPython.display import HTML,display, clear_output
from matplotlib import pyplot as plt
import networkx as nx
from string import ascii_lowercase

class Convert2GeoJson(object):
    """
    Turn a dataframe containing point data into a geojson formatted python dictionary

    df : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
    lat : the name of the column in the dataframe that contains latitude data
    lon : the name of the column in the dataframe that contains longitude data
    """
    def __init__(
        self,dataframe,properties,links=False,
        lat='latitude',lon='longitude'
        ):
        self.df = dataframe
        self.properties = properties
        self.lat = lat
        self.lon = lon
        self.links = links

        colorList = 'Red Green Yellow Blue Orange Purple Cyan Magenta Lime Pink Teal Lavender Brown Maroon Olive Coral Navy Grey'
        self.colors = colorList.lower().split(' ')
    )

    def replace(self, file, pattern, subst):
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

    def getLookupDict(self,column):
        retDict = {x:y for x,y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

    def getTranslateDict(self,column):
        retDict = {y:x for x,y in enumerate(self.df[column].value_counts().to_dict().keys())}
        return retDict

    def df2geojson(self, visible_name = False,
        attribution= 'Implemented: <a target="_blank" href="http://www.topoi.org">Topoi</a> and <a target="_blank" href="http://www.mpiwg-berlin.mpg.de">MPIWG</a>',
        description='Displaying GeoJson Data from Pandas Dataframe',
        debug=False):

        lookUps = {}
        keyTranslate = {}

        dfTemp = pd.DataFrame()

        if not visible_name:
            visible_name = {x:' '.join(x.split('_')) for x in properties}

        # translate repeating values to dict
        for key in properties:
            if key != 'ObjID' and len(df[key].value_counts()) < 21:
                keyTranslate = getTranslateDict(df,key)
                lookUps[key] = getLookupDict(df,key)
                dfTemp[key] = df[key].apply(lambda row: keyTranslate[row])
            else:
                dfTemp[key] = df[key]

        if debug:
            print(lookUps)

        retDict = {}

        # construct field values
        for cl in properties:
            if cl in lookUps.keys():
                retDict[cl] = {'lookup':lookUps[cl],'name':visible_name[cl]}
            else:
                retDict[cl] = {'name':visible_name[cl]}
        if debug:
            print(retDict)

        dfTemp[lon] = df[lon]
        dfTemp[lat] = df[lat]

        # create a new python dict to contain our geojson data, using geojson format
        geojson = {'type':'FeatureCollection', 'features':[],'properties': {'fields': {}, 'attribution': {}, 'description': {}}}

        # loop through each row in the dataframe and convert each row to geojson format
        for _, row in dfTemp.iterrows():
            # create a feature template to fill in
            feature = {'type':'Feature',
                       'properties':{},
                       'geometry':{'type':'Point',
                                   'coordinates':[]}}

            # fill in the coordinates
            feature['geometry']['coordinates'] = [row[lon],row[lat]]

            # for each column, get the value and add it as a new feature property
            for prop in properties:
                feature['properties'][prop] = row[prop]

            # add this feature (aka, converted dataframe row) to the list of features inside our dict
            geojson['features'].append(feature)


            # add lookup properties
            geojson['properties']['fields'] = retDict

            if links:
                source = (row[lon],row[lat])
                try:
                    linked = ast.literal_eval(row['linkedCities'])
                except:
                    linked= ''
                if linked and type(linked)==list:
                    for idcity in linked:
                        try:
                            dfTemp = df_geo[df_geo.cityid == idcity]
                            if dfTemp.shape[0] > 0:
                                destination = (dfTemp.longitude.values[0],dfTemp.latitude.values[0])

                                feature = {
                                   "type":"Feature",
                                   "properties":{"linkedCities": str(row['city']) + '->' + str(dfTemp['city'].iloc[0])},
                                   "geometry":{"type":"LineString",
                                               "coordinates":[]},
                                   "style": {
                                       "stroke": "#CC0000",
                                       "stroke-opacity": 1,
                                       "stroke-width": 1
                                   },
                                }

                                # fill in the coordinates
                                feature["geometry"]["coordinates"] = [
                                    [
                                        source[0],
                                        source[1]
                                    ],
                                    [
                                        destination[0],
                                        destination[1]
                                    ]
                                ]



                                # add this feature (aka, converted dataframe row) to the list of features inside our dict
                                geojson["features"].append(feature)


                                links.append((source,destination))
                        except:
                            pass
        # add attribution and description
        geojson['properties']['attribution'] = attribution
        geojson['properties']['description'] = description

        return geojson

    def generateGeoDF(self):
        # TODO
        return self.df

    def generateJSON(self,name='data.geojson',path='.'):
        geojson_dict = self.df2geojson(self.generateGeoDF())
        geojson_str = json.dumps(geojson_dict, indent=2)

        with open(os.path.join(path,name),'w') as output_file:
            output_file.write(geojson_str)

        print('Done')
