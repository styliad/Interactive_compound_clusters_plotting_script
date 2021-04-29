## Compound_clusters_plotting_script

# Plot an interactive histogram for clustered compounds from various vendors

This script was used to show how clusters vary based on different docking score cutoff values.
The data came from Molecular Docking results, where compounds were clustered to facilitate selection of representative compounds.

![Interactive Compound Clusters Histogram Plot](https://raw.githubusercontent.com/styliad/Interactive_compound_clusters_plotting_script/main/Interactive_Histogram_plot.png?token=AH274VQF3L5IYEEXVL4VWPLARK6K6)

# Usage
+ Import a csv file(or other alternatives) to generate a pandas Dataframe. The file must contain a column with compound cluster index (Canvas Cluster Index in the script)
+ Set the characteristic names your file has for compounds coming from a specific vendor (eg. vendor1_compound_2000)
+ Set the name of the vendor to be shown in the plot (eg. Vendor1) 


# Dependencies
+ numpy 
+ pandas
+ bokeh 

# References 
+ https://rebeccabilbro.github.io/interactive-viz-bokeh/
