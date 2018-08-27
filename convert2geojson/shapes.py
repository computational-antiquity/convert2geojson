if self.links:
    source = (row[self.lon],row[self.lat])
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
