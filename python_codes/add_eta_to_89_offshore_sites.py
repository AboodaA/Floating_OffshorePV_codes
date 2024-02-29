import pvlib 
import pandas as pd
import xlsxwriter
import numpy as np 

import os, time, glob, re
import heat_index_function

from pvlib import pvsystem
from pvlib import pvarray
from pvlib.temperature import sapm_cell, TEMPERATURE_MODEL_PARAMETERS 
#from pvlib.pvarray import pvefficiency_adr
from pvlib import irradiance

#The ADR parameters are important for the calculation of the efficiencies
parameter_a = -2.81
parameter_b = -0.0455
parameter_delta_T = 0 
adr_params = {'k_a': 0.99924,
              'k_d': -5.49097,
              'tc_d': 0.01918,
              'k_rs': 0.06999,
              'k_rsh': 0.26144
              }


files_in_directory_offshore = os.listdir("/home/abed/Documents/begin_analysis/november/offshore_sites_need_outputs/")
index_length_of_list = len(files_in_directory_offshore)


 

for i in range(0, index_length_of_list):
	string_to_read_file_name = "/home/abed/Documents/begin_analysis/november/offshore_sites_need_outputs/" + files_in_directory_offshore[i]
	string_to_print_file_name = "/home/abed/Documents/begin_analysis/november/offshore_sites_with_outputs/" + files_in_directory_offshore[i] 
	place_name = os.path.splitext(files_in_directory_offshore[i])
	print(place_name)
	data_read_in = pd.read_excel(string_to_read_file_name)
	rahaman_cell_temps = data_read_in['TempC_RM']
	pvlib_cell_temps = data_read_in['TempCell_PVL']
	poa_global = data_read_in['poa_for_offshore']
	module_eta_RM = pvlib.pvarray.pvefficiency_adr(poa_global, rahaman_cell_temps, **adr_params)
	module_eta_M2 = pvlib.pvarray.pvefficiency_adr(poa_global, pvlib_cell_temps, **adr_params)
	data_read_in['module_eta_RM'] = module_eta_RM
	data_read_in['module_eta_M2'] = module_eta_M2
	print("Here we go")
	#We are adding another sheet, so we have to use this "Writer" object
	writer = pd.ExcelWriter(string_to_print_file_name, engine = "xlsxwriter")
	data_read_in.to_excel(writer, sheet_name = "with_eta")
	writer.close()
	print("And there we are")
