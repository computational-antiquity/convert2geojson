# -*- coding: utf-8 -*-
# base packages
from .base import Convert2GeoJson

import ipywidgets as widgets
import pandas as pd
from IPython.display import clear_output


class SelectGUI(Convert2GeoJson):
    """
    GUI for selective plotting of Geo-Data on maps.
    """
    def __init__(
            self, dataframe, properties,
            lat='latitude', lon='longitude'
            ):
        super(DisplayGUI, self).__init__(dataframe, properties, lat, lon)

        self.df_select = pd.DataFrame()

        self.valueList = ['None']

        self.selectColumn = widgets.Dropdown(
            options=self.df.columns,
            description='Select column:'
        )
        self.selectColumn.observe(self._on_change_values)

        self.selectValue = widgets.Dropdown(
            options=self.valueList,
            description='Select value:'
        )
        self.selectValue.observe(self._on_change_reduce_data)

        self.displayMap = widgets.Button(
            description='Display map',
            button_style='info',
            tooltip='Click me',
            icon='check'
        )
        self.displayMap.on_click(self._on_button_clicked)

        self.out = widgets.Output()

    def _on_change_values(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.valueList = list(self.df[change['new']].unique())
            self.valueList = sorted(self.valueList)
            self.valueList.insert(0, 'reset')
            if len(self.valueList) < 30:
                self.selectValue.options = self.valueList
                with self.out:
                    clear_output()
            else:
                with self.out:
                    print('To many different values in column.')

    def _on_change_reduce_data(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            if change['new'] == 'reset':
                self.df_select = self.df
                self.tempMap = Convert2GeoJson(self.df_select, self.df_select.columns).convert()
            else:
                self.df_select = self.df[self.df[self.selectColumn.value] == change['new']]
                self.tempMap = Convert2GeoJson(self.df_select, self.df_select.columns).convert()

    def _on_button_clicked(self, b):
        with self.out:
            clear_output()
            display(self.tempMap.display(style='grouped'))

    def display(self):
        """Display GUI for convert2GeoJSON"""
        columnSelection = widgets.HBox([self.selectColumn])
        valueSelection = widgets.HBox([self.selectValue, self.displayMap])
        selectMatrix = widgets.VBox([columnSelection, valueSelection, self.out])

        display(selectMatrix)
