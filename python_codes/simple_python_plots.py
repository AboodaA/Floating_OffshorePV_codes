import pvlib
import os
from scipy.integrate import odeint
from rahaman_thermal_model2 import define_cell_temperature
import pandas as pd
import numpy as np 
import json
from pvlib import pvsystem
from pvlib import pvarray
from pvlib.temperature import sapm_cell, TEMPERATURE_MODEL_PARAMETERS 
from pvlib import irradiance
import matplotlib.pyplot as plt


files_in_directory = os.listdir("/home/abed/Documents/begin_analysis/cell_temperature_files/")
index_length_of_list = len(files_in_directory)
print(files_in_directory)

for i in range(0, index_length_of_list):
    string_to_read_file_name = "/home/abed/Documents/begin_analysis/cell_temperature_files/" + files_in_directory[i]
    place_name = os.path.splitext(files_in_directory[i])[0]
    string_to_show_plot = "/home/abed/Documents/begin_analysis/cell_temperature_special_plots/" + place_name + ".png"    
   
    data_read_in = pd.read_excel(string_to_read_file_name)
    data_read_in = data_read_in[(data_read_in['poa_for_offshore'] >= 200)]
    number_of_rows = data_read_in.shape[0]
    series_of_rows = pd.Series(range(1,  number_of_rows + 1))
    ambient_temp_read_in = data_read_in['T2M']
    water_temperatures_read_in = data_read_in['TS']

#Let's plot it 
    plt.figure().clear()
    plt.figure(figsize=(18, 7))
    plt.scatter(series_of_rows,  data_read_in['TempCell_PVL'],  color = "blue",  label = "PVL T Cell",  linestyle = "-")
    plt.scatter(series_of_rows,  ambient_temp_read_in,  color = "red",  label = "T 2M",  linestyle = ":")
    plt.scatter(series_of_rows,  data_read_in['TempC_RM'],  color = "green",  label = "RM T Cell",  linestyle = "--")
    plt.scatter(series_of_rows,  water_temperatures_read_in,  color = "purple",  label = "TS",  linestyle = "-.")
    plt.legend()
    plt.savefig(string_to_show_plot)
    plt.close(string_to_show_plot)
