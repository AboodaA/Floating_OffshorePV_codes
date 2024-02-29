#This is the script to generate the outputs for the land-based PV systems. It starts with the files which have the meteorological data for the land-based sites. Note that this includes both the port sites and inland sites. 

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
#We will read in the files which have the appropriate meteorological data. Note that our script assumes that the data comes from 
# NASAPOWER. If you are using different column headings for your meteorological data, you will need to shift accordingly below (see note)		
files_in_directory = os.listdir(DIRECTORY WHERE THE INPUT FILES ARE LOCATED)

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
index_length_of_list = len(files_in_directory)

#Note that we have used the NASA POWER data; make sure to change the codes as appropriate based on where your meteorolgical data is coming from
for x in range(0, index_length_of_list):
    start_individual_site = time.time()
    string_to_read_file_name = "/home/abed/Documents/terrestrial_files_input/" + files_in_directory[x]
    string_to_print_file_name = "/home/abed/Documents/terrestrial_files_output/" + files_in_directory[x]
    data_read_in =  pd.read_excel(string_to_read_file_name)
    albedo_read_in = data_read_in['ALLSKY_SRF_ALB']
    ghi_read_in = data_read_in['ALLSKY_SFC_SW_DWN']
    dni_read_in = data_read_in['ALLSKY_SFC_SW_DNI']
    solar_zenith_angle = data_read_in['SZA']
    ambient_temp_read_in = data_read_in['T2M']
    relative_humidity_read_in = data_read_in['RH2M']
    horizontal_diffuse_irradiance = data_read_in['CLRSKY_SFC_SW_DIFF']*data_read_in['CLRSKY_KT']
    complete_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt = surface_tilt_fixed, surface_azimuth = 180, solar_zenith =solar_zenith_angle, solar_azimuth = 180, dni = dni_read_in, ghi = ghi_read_in, dhi = horizontal_diffuse_irradiance, 
        dni_extra=None, airmass=None,  albedo=albedo_read_in, surface_type=None, model='isotropic', model_perez='allsitescomposite1990')
    #Let's calculate the POA based on the isotropic model presented by PVLIB
    poa_calculated = complete_irradiance['poa_global']
    wind_speeds_read_in = data_read_in['WS2M']
#We need the components of diffuse irradiance to feed into the POA
    ground_reflected_diffuse = pvlib.irradiance.get_ground_diffuse(surface_tilt_fixed, ghi = ghi_read_in, albedo = albedo_read_in)
    combined_diffuse_irradiance = horizontal_diffuse_irradiance + ground_reflected_diffuse

	#Now the fun stuff
    module_temperature = pvlib.temperature.sapm_module(poa_global=poa_calculated, temp_air = ambient_temp_read_in, wind_speed = wind_speeds_read_in, a = parameter_a, b = parameter_b)
    data_read_in['module_temp'] = module_temperature
	data_read_in['poa_global'] = poa_calculated
	
	#We use the ADR model for the module efficiency
	#Note that the function takes in the cell temperature, not the module temperature
	#We use deltaT = 0 for the insulated back, glass on polymer module
    cell_temperatures = pvlib.temperature.sapm_cell_from_module(module_temperature, poa_calculated, 0)
    module_eta = pvlib.pvarray.pvefficiency_adr(poa_calculated, cell_temperatures, **adr_params)
    data_read_in['cell_temp_method1'] = cell_temperatures
    data_read_in['module_eta_method1'] = module_eta
	
	

	
	#We now use the heat index to calculate one set of values for module, cell temperatures and also efficiencies
    fahrenheit_temperatures = heat_index_function.convert_celsius_fahrenheit(ambient_temp_read_in)
    apparent_temperatures = heat_index_function.calculate_heat_index(fahrenheit_temperatures, relative_humidity_read_in)
	#These are the temperatures we will use to feed into the model for module temperature, efficiency, etc. 
    apparent_temperatures_celsius = heat_index_function.convert_fahrenheit_celsius(apparent_temperatures)
	
    module_temperature_apparent = pvlib.temperature.sapm_module(poa_global=poa_calculated, temp_air = apparent_temperatures_celsius, wind_speed = wind_speeds_read_in, a = parameter_a, b = parameter_b)
	
    cell_temperatures_apparent = pvlib.temperature.sapm_cell_from_module(module_temperature_apparent, poa_calculated, 0)
	
    module_eta_method2 = pvlib.pvarray.pvefficiency_adr(poa_calculated, cell_temperatures_apparent, **adr_params)
	
    data_read_in['cell_temp_method2'] = cell_temperatures_apparent
    data_read_in['module_eta_method2'] = module_eta_method2
	
	
	#Combine everything into a data frame and export it to Excel
    data_read_in_as_df = pd.DataFrame(data_read_in)
    data_read_in_as_df.to_excel(string_to_print_file_name, index=False)	

#From here on out, we will have the bit where we print out the summary information 
    site_name = re.split(".xlsx", files_in_directory[x])
    text_file_name = site_name[0] + ".txt"
    complete_path_to_save_stats = os.path.join('/home/abed/Documents/text_descriptions/', text_file_name)
    average_ambient_temperatures = ambient_temp_read_in.mean()
    average_apparent_temperatures = apparent_temperatures_celsius.mean()
    average_module_temperature = module_temperature.mean()
    average_module_temperature_method2 = module_temperature_apparent.mean()
    print("We are going to write the data to the file now")
    end_individual_site = time.time()
    individual_elapsed_time = end_individual_site - start_individual_site
    print(individual_elapsed_time)
    #Printing some very high level stuff just to make sure.
    with open(complete_path_to_save_stats, 'w') as fyt:
        fyt.write("The average ambient temperature is" + '\n')
        fyt.write(str(average_ambient_temperatures) + '\n')
        fyt.write("The average module temperature is" + '\n')
        fyt.write(str(average_module_temperature) + '\n')
		
        fyt.write("The average apparent temperature is" + '\n')
        fyt.write(str(average_apparent_temperatures) + '\n')
        fyt.write("The average module temperature per method 2 is" + '\n')
        fyt.write(str(average_module_temperature_method2) + '\n')
        fyt.write("The elapsed time for this site is" + '\n')
        fyt.write(str(individual_elapsed_time) + '\n')
ending_time = time.time()
elapsed_time = ending_time - start_time
print("Elapsed time is")
print(elapsed_time)
