import pvlib 

import pandas as pd

import numpy as np 

import os, time, glob, re
import heat_index_function

from pvlib import pvsystem
from pvlib import pvarray
from pvlib.temperature import sapm_cell, TEMPERATURE_MODEL_PARAMETERS 
#from pvlib.pvarray import pvefficiency_adr
from pvlib import irradiance
import matplotlib.pyplot as plt 

start_time = time.time()

#We will model the Sandia modules, and take a cell temperature from the module temperature
#sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
#We will assume an insulated back and glass/polymer rack for the terristrial PV modules

parameter_a = -2.81
parameter_b = -0.0455
parameter_delta_T = 0 
surface_tilt_fixed =10


#We also borrowed the ADR parameters from:
# https://pvlib-python.readthedocs.io/en/v0.9.5/gallery/adr-pvarray/plot_simulate_system.html 

adr_params = {'k_a': 0.99924,
              'k_d': -5.49097,
              'tc_d': 0.01918,
              'k_rs': 0.06999,
              'k_rsh': 0.26144
              }
                            

#We will run this for the list of input excel files 
#Python starts with 0 but we have to take 1 off in return to make the array length work
string_to_read_file_name = "/home/abed/Documents/begin_analysis/november/" + "wind_speed_example.xlsx"
string_to_print_file_name = "/home/abed/Documents/begin_analysis/november/" + "wind_speed_example.xlsx"
data_read_in =  pd.read_excel(string_to_read_file_name)
data_important = data_read_in[data_read_in['poa_calculated'] > 50]
data_important = data_important.iloc[1:1000,]
number_of_rows = data_important.shape[0]
series_of_rows = pd.Series(range(1,  number_of_rows + 1)) 
##All of the stuff has already been read in 
poa_calculated = data_important['poa_calculated']
#The wind speeds column got misnamed here, will try to fix it
wind_speeds_read_in = data_important['WS2M']
ambient_temp_read_in = data_important['T2M'] 
#Now the fun stuff
module_temperature = pvlib.temperature.sapm_module(poa_global=poa_calculated, temp_air = ambient_temp_read_in, wind_speed = wind_speeds_read_in, a = parameter_a, b = parameter_b)
#We use the ADR model for the module efficiency
#Note that the function takes in the cell temperature, not the module temperature
#We use deltaT = 0 for the insulated back, glass on polymer module
cell_temperatures = pvlib.temperature.sapm_cell_from_module(module_temperature, poa_calculated, 0)  
module_eta = pvlib.pvarray.pvefficiency_adr(poa_calculated, cell_temperatures, **adr_params)
#Now use the windspeeds = 0 approach
module_temperature_no_wind = pvlib.temperature.sapm_module(poa_global=poa_calculated, temp_air = ambient_temp_read_in, wind_speed = 0, a = parameter_a, b = parameter_b)
cell_temperatures_no_wind = pvlib.temperature.sapm_cell_from_module(module_temperature_no_wind, poa_calculated, 0)
module_eta_no_wind = pvlib.pvarray.pvefficiency_adr(poa_calculated, cell_temperatures_no_wind, **adr_params)
delta_eta = module_eta - module_eta_no_wind
#Now to plot them and save it 
string_for_wind_plot = "/home/abed/Documents/begin_analysis/november/pictures_final_final/wind_plot.png"
string_for_wind_plot_B = "/home/abed/Documents/begin_analysis/november/pictures_final_final/wind_plot_B.png"
string_for_wind_plot_C = "/home/abed/Documents/begin_analysis/november/pictures_final_final/wind_plot_C.png"
string_for_wind_plot_D = "/home/abed/Documents/begin_analysis/november/pictures_final_final/wind_plot_D.png"

plt.figure().clear()
plt.figure(figsize=(18, 7))
plt.plot(series_of_rows,  module_eta,  color = "red",  label = "Eta",  linestyle = "solid")
plt.legend()
plt.savefig(string_for_wind_plot)
plt.close(string_for_wind_plot)

plt.figure().clear()
plt.figure(figsize=(18, 7))
plt.plot(series_of_rows,  module_eta_no_wind,  color = "purple",  label = "Eta--no wind",  linestyle = "solid")
plt.legend()
plt.savefig(string_for_wind_plot_B)
plt.close(string_for_wind_plot_B)

#We want it in percentages
delta_eta_pc = 100*delta_eta
plt.figure().clear()
plt.figure(figsize=(18, 7))
ax = plt.subplot()
plt.plot(series_of_rows,  delta_eta_pc,  color = "green",  label = "delta_Eta",  linestyle = "solid")
plt.ylabel("Percentage improvement in Module efficiency", fontsize = 19)
plt.xlabel("Hours--1000 arbitrary hours", fontsize = 20)
ax.xaxis.set_tick_params(labelsize=20)
ax.yaxis.set_tick_params(labelsize=17)
plt.rcParams.update({'font.size': 19})
plt.legend()
plt.savefig(string_for_wind_plot_C)
plt.close(string_for_wind_plot_C)	

plt.figure().clear()
plt.figure(figsize=(18, 7))
plt.plot(series_of_rows,  module_eta_no_wind,  color = "purple",  label = "Eta--no wind",  linestyle = "solid")
plt.plot(series_of_rows,  module_eta,  color = "red",  label = "Eta",  linestyle = "solid")
plt.legend()
plt.savefig(string_for_wind_plot_D)
plt.close(string_for_wind_plot_D)	
