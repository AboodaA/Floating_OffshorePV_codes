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
 

start_time = time.time()
		
#print("Check the file")
files_in_directory = os.listdir("/home/abed/Documents/Port Renfrew Inland for SZA")

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
index_length_of_list = len(files_in_directory)

#Changing the index a little bit to skip over Port Renfrew for now
#Then also only opening the folder for Port Renfrew
for x in range(0, index_length_of_list):
    start_time = time.time()
    start_individual_site = time.time()
    string_to_read_file_name = "/home/abed/Documents/Port Renfrew Inland for SZA/" + files_in_directory[x]
    string_to_print_file_name = "/home/abed/Documents/terrestrial_files_output_for_poa/" + files_in_directory[x]
    data_read_in =  pd.read_excel(string_to_read_file_name)
    print("We have opened a file")
    print(string_to_read_file_name)
    albedo_read_in = data_read_in['ALLSKY_SRF_ALB']
    ghi_read_in = data_read_in['ALLSKY_SFC_SW_DWN']
    dni_read_in = data_read_in['ALLSKY_SFC_SW_DNI']
    solar_zenith_angle = data_read_in['SZA']
    horizontal_diffuse_irradiance = data_read_in['CLRSKY_SFC_SW_DIFF']*data_read_in['CLRSKY_KT']
    complete_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt = surface_tilt_fixed, surface_azimuth = 180, solar_zenith 		=solar_zenith_angle, solar_azimuth = 180, dni = dni_read_in, ghi = ghi_read_in, dhi = horizontal_diffuse_irradiance, 
        dni_extra=None, airmass=None,  albedo=albedo_read_in, surface_type=None, model='isotropic', model_perez='allsitescomposite1990')
    #Let's calculate the POA based on the isotropic model presented by PVLIB
    poa_calculated = complete_irradiance['poa_global']
    data_read_in['poa_calculated'] = poa_calculated
    data_read_in_as_df = pd.DataFrame(data_read_in)
    data_read_in_as_df.to_excel(string_to_print_file_name, index=False)
    ending_time = time.time()
    elapsed_time = ending_time - start_time
    print("Elapsed time is")
    print(elapsed_time)
    

