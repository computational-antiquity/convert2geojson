# convert2geojson
Convert databases to geojson, useful for displaying datasets on maps.

A FeatureCollection is generated from those dataframe rows containing values for
latitude and longitude.

_Note:_ To limit the size of the GeoJSON file, lookup tables are generated
automatically for fields with a limited number of values (<20) and saved as a top-level 'properties' key in the JSON file. This is not part of the
GeoJSON standard and can lead to problems with linters, e.g. [GeoJSONLint](http://geojsonlint.com/).

## Content

1. [Installation](#installation)
2. [Basics](#basic-usage)
  - [Loading data](#loading-data)
  - [Generating geojson](#generating-geojson)
  - [Plotting](#plotting)
3. [Examples](#examples)

## Installation

The package can be installed by
```
pip install convert2geojson
``` 

The latest development version of the package can be installed from GitHub by running
```
  pip install git+https://github.com/computational-antiquity/convert2geojson.git
```
This installs the most recent version of the master branch.

If the plotting on maps in JupyterLab is not yielding results, there might be problems with your [ipyleaflet installtion](https://github.com/jupyter-widgets/ipyleaflet#installation) or [ipywidgets installtion](https://ipywidgets.readthedocs.io/en/stable/user_install.html#installing-the-jupyterlab-extension).

## Basic usage

Import the package with
```python
from convert2geojson import Convert2GeoJson
```

### Loading data

The package is instantiated by providing a dataframe containing the geodata ,e.g. `dataframe=df`, a list of columns of the dataframe, which should be shown as information for every geo feature, e.g. `properties=df.columns` to show everything, and the column titles for longitudal and latitudal data (standard parameter names are `lat='latitude'` and `lon='longitude'`).

```python
data = Convert2GeoJson(
          df,
          df.columns,
          lat='latitude',
          lon='longitude'
       )
```

The geo data is expected to be gievn as float numbers. Rows with empty longitudal or latitudel data, or marked as `NaN` are droped from the supplied dataframe.

The original dataframe can however still be accessed as `data.rawDF`.


### Generate geoJson

To generate the geoJSON simple run
```python
data.convert()
```

This generates a geoJSON formated dictionary which is available at
```python
data.geojson()
```

To save the geoJSON to a file, run
```python
data.save()
```
You can provide parameters for the name and path, standards are `name='data.geojson'` and `path='.'`.

### Plotting

For plotting the package is leveraging the [ipyleaflet package](https://github.com/jupyter-widgets/ipyleaflet) which is also available as a JupyterLab extension.

For a first overview use
```python
data.display()
```
This plots the geoJSON features as a layer on a basemap.

The basic plotting can be changed by parameters for the map layout (`mapLayout=dict()`), and the basemap data (`basemap=dict()`).

To use a custom basemap, you can provide a dictionary of the format
```python
customBasemap = {
          'url': 'https://{s}.URL_to_mapdata/{z}/{x}/{y}.png',
          'max_zoom': 'max available zoom level',
          'attribution': 'Attribution',
          'name': 'Name for layer control'
          }
```
##### Screenshot
![Screenshot of generated map](example/mapExample.png "Screenshot of generated map")

#### Grouped Plotting

For densely distributed geographical data, to styling options are available.

By choosing `style='grouped'` ipyleaflets MarkerCluster is used to show groups of markers depending on the zoom level. By clicking on a cluster, the map zooms to the level, which contains the selected markers in the cluster .

Additionally, since markers are now single entities, by clicking on any marker a popup shows the information of the dataframe belonging to the geographical point.

##### Screenshot
![Screenshot of generated cluster map](example/clusterMap.png "Screenshot of generated cluster map")

#### Categorical plotting as pie chart distribution

By choosing `style='pie'` and providing a category found in the dataframe columns, by setting `groupBy='Category'`, the package generates a standalone map showing the clustered markers as pie charts separated into sub-groups by the chosen category.

##### Screenshot
![Screenshot of generated pie charts map](example/pieChartMap.png "Screenshot of generated pie chart map")


## Examples

Have a look at the [Loading datasets](/example/Loading_dataset.ipynb) or the [Advanced Plotting](/example/Advanced_plotting.ipynb) notebooks in the `/example` folder
