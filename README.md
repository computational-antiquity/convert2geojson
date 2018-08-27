# convert2geojson
Convert databases to geojson, useful for displaying datasets on maps.

A FeatureCollection is generated from those dataframe rows containing values for
latitude and longitude.

_Note:_ To limit the size of the GeoJSON file, lookup tables are generated
automatically for fields with a limited number of values (<20). This is not part of the
GeoJSON standard and can lead to problems with linters.

## Example Application

Have a look at the [notebook](/example/Loading dataset.ipynb) in the `/example` folder
