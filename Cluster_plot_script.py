import numpy as np
import pandas as pd
import os
from bokeh.io import output_notebook
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, CustomJS, Slider,Label
from bokeh.layouts import column

# ========================DATA PREPARATION===========================

# Read <Project Name>-MMGBSA_1-001.maegz-generated csv file with QikProp and Smiles 
data = pd.read_csv('input_file.csv')

 # Clear empty data columns
data.dropna(axis=1, how='all', inplace=True)
data = data.loc[:, (data != 0).any(axis=0)]

# Filter results based on a 25% docking score cutoff according to the range of values
for f in [i for i in range(0,55,5)]:
    max_docking_score = data['docking score'].max()
    min_docking_score = data['docking score'].min()
    range_docking_score = abs(max_docking_score - min_docking_score)
    docking_filtering_threshold = -(range_docking_score * f *(0.01)) + max_docking_score
    data[str(f)] = np.where(data['docking score'] < docking_filtering_threshold, 1, 0)

# Adjust here the name that you provided for the files.
suppliers ={
    'molport_name_on_pandas_df' : 'Molport',
    'ENAMINE_name_on_pandas_df': 'ENAMINE',
    'UORSY_name_on_pandas_df' : 'UORSY'
}

supplier='molport_name_on_pandas_df|ENAMINE_name_on_pandas_df|UORSY_name_on_pandas_df'
data['Supplier'] = data.Title.str.extract('('+supplier+')', expand=False)
data['Supplier'] = data['Supplier'].map(suppliers)

# Substract 1 to convert cluster numbering from 0 --> n instead of 1 --> n. Canvas cluster numbering starts with 1, here from 0
data['Canvas Cluster Index'] = data['Canvas Cluster Index'].apply(lambda x: x - 1)

# Define number of clusters
clusters = []
num_clusters = data['Canvas Cluster Index'].max()+1

# Divide compounds in clusters
for i in range(0,num_clusters):
    clusters.append(pd.DataFrame(data[data['Canvas Cluster Index'] == i]))
    clusters[i].reset_index(drop=True,inplace=True)

cut_offs = [i for i in range(0,55,5)]
clusters_isnot_0 = {}
clusters_is_0 = {}
test = pd.DataFrame(columns=['ENAMINE','Molport', 'UORSY','Molecules','Cluster'])
sources = {'level0' : ColumnDataSource(test)}
for f in cut_offs:    
    test = pd.DataFrame(columns=['ENAMINE','Molport', 'UORSY','Molecules','Cluster'])
    for i in range(0,num_clusters):
        temp_list = []
        temp_list.append(clusters[i][(clusters[i]['Supplier'] == 'ENAMINE')& (clusters[i][str(f)] == 1)].shape[0])
        temp_list.append(clusters[i][(clusters[i]['Supplier'] == 'Molport') & (clusters[i][str(f)] == 1)].shape[0])
        temp_list.append(clusters[i][(clusters[i]['Supplier'] == 'UORSY') & (clusters[i][str(f)] == 1)].shape[0])
        temp_list.append(clusters[i][(clusters[i]['Supplier'] == 'Molport') & (clusters[i][str(f)] == 1)].shape[0] + \
                         clusters[i][(clusters[i]['Supplier'] == 'UORSY') & (clusters[i][str(f)] == 1)].shape[0]+\
                         clusters[i][(clusters[i]['Supplier'] == 'ENAMINE')& (clusters[i][str(f)] == 1)].shape[0])
        temp_list.append(i)
        row = pd.Series(temp_list, index=test.columns)
        test = test.append(row, ignore_index=True)  
        sources["_" + str(f)] =  test
        clusters_isnot_0["_" + str(f)] = sources["_" + str(f)][sources["_" + str(f)]['Molecules'] != 0].shape[0]
        clusters_is_0["_" + str(f)] = sources["_" + str(f)][sources["_" + str(f)]['Molecules'] == 0].shape[0]
        sources["_" + str(f)] =  ColumnDataSource(test)

# Below code snippet take from https://rebeccabilbro.github.io/interactive-viz-bokeh/
dict_of_sources = dict(zip(
                      [f for f in cut_offs],
                      ['_%s' % f for f in cut_offs])
                      )
js_source_array = str(dict_of_sources).replace("'", "")

# =======================BOKEH PLOT CREATION=======================
output_file("clusters_plot_test.html")

# Define sources
renderer_source = sources['level0']
suppliers_ = ['ENAMINE','Molport', 'UORSY']
colors = ["dodgerblue","purple","goldenrod"]

p = figure(plot_width=1800, plot_height=850)
p.vbar_stack(suppliers_, x='Cluster', width=0.9, color=colors, source=renderer_source,
             legend_label=suppliers_)
p.xaxis.axis_label = "Cluster index"
p.yaxis.axis_label = "Number of compounds"
p.yaxis.ticker = [0,5,10,15,20,25, 50, 75, 100]
p.legend.click_policy="hide"
label_opts = dict(
    x=0, y=0,
    x_units='screen', y_units='screen'
)
msg1 = 'clusters with 0 molecules: ' + str(clusters_is_0).replace("'", "").replace("'", "")[1:-1]
caption1 = Label(text=msg1,text_font_size = '8pt', **label_opts)
p.add_layout(caption1, 'below')
msg2 = 'clusters without 0 molecules: ' + str(clusters_isnot_0).replace("'", "").replace("'", "")[1:-1]
caption2 = Label(text=msg2,text_font_size = '8pt', **label_opts)
p.add_layout(caption2, 'below')

# Slider JS code setup
code = """
    var cutoff = slider.value;
    var sources = %s;
    var new_source_data = sources[cutoff].data;
    renderer_source.data = new_source_data;
    renderer_source.change.emit();
""" % js_source_array
callback = CustomJS(args=sources, code=code)
slider = Slider(start=0, end=50, value=0, step=5, title="Cut-off value")
callback.args["renderer_source"] = renderer_source
callback.args["slider"] = slider
slider.js_on_change("value", callback)

layout = column(
    p,
    slider,
)

save(layout)