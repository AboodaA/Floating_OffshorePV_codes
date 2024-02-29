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


 

#We will want to compare the Rahaman Model with the typical stuff from PVLIB
parameter_a = -2.81
parameter_b = -0.0455
parameter_delta_T = 0 
adr_params = {'k_a': 0.99924,
              'k_d': -5.49097,
              'tc_d': 0.01918,
              'k_rs': 0.06999,
              'k_rsh': 0.26144
              }
                  
                           

#We will read in the files which have the appropriate meteorological data. Note that our script assumes that the data comes from 
# NASAPOWER. If you are using different column headings for your meteorological data, you will need to shift accordingly below (see note)	
files_in_directory_offshore = os.listdir(YOUR DIRECTORY WHERE YOU READ IN THE FILES WITH THE METEOROLOGICAL DATA)
index_length_of_list = len(files_in_directory_offshore)



for i in range(0, index_length_of_list):
    string_to_read_file_name = "/home/abed/Documents/begin_analysis/november/offshore_sites_need_outputs/" + files_in_directory_offshore[i]
    string_to_print_file_name = "/home/abed/Documents/begin_analysis/november/offshore_sites_with_outputs/" + files_in_directory_offshore[i]
    place_name = os.path.splitext(files_in_directory_offshore[i])[0]
    string_to_show_plot = "/home/abed/Documents/offshore_files_output/plots_images/" + place_name + ".png"    
    complete_path_to_save_stats = "/home/abed/Documents/offshore_sites_19_outputs/summary/" + place_name + ".txt"
    
    data_read_in = pd.read_excel(string_to_read_file_name)
    number_of_rows = data_read_in.shape[0]
    series_of_rows = pd.Series(range(1,  number_of_rows + 1)) 
    
    #Note that we have used the NASA POWER data; make sure to change the codes as appropriate based on where your meteorolgical data is coming from
    #Giving names to the columns coming in
    albedo_read_in = data_read_in['ALLSKY_SRF_ALB']
    ghi_read_in = data_read_in['ALLSKY_SFC_SW_DWN']
    dni_read_in = data_read_in['ALLSKY_SFC_SW_DNI']
    solar_zenith_angle = data_read_in['SZA']
    ambient_temp_read_in = data_read_in['T2M']
    relative_humidity_read_in = data_read_in['RH2M']
    wind_speeds_read_in = data_read_in['WS2M']
    water_temperatures_read_in = data_read_in['TS']
    horizontal_diffuse_irradiance = data_read_in['CLRSKY_SFC_SW_DIFF']*data_read_in['CLRSKY_KT']

    #Calculate the POA, but note that for the panels which are offshore, tilt = 0
    
    ground_reflected_diffuse = pvlib.irradiance.get_ground_diffuse(0, ghi = ghi_read_in, albedo = albedo_read_in)
    combined_diffuse_irradiance = horizontal_diffuse_irradiance + ground_reflected_diffuse
    poa_for_offshore = combined_diffuse_irradiance + dni_read_in
    data_read_in['poa_for_offshore'] = poa_for_offshore
    data_read_in['TempF_RM'] = 0
    data_read_in['TempF_RM'] = data_read_in['TempF_RM'].astype(float)
    data_read_in['TempC_RM'] = 0
    data_read_in['TempC_RM'] = data_read_in['TempC_RM'].astype(float)
    data_read_in['TempB_RM'] = 0 
    data_read_in['TempB_RM'] = data_read_in['TempB_RM'].astype(float)

    
    temperature_cells_calculated = poa_for_offshore
    temperature_front_calculated = temperature_cells_calculated
    temperature_back_calculated = temperature_cells_calculated
    #data_read_in['TempsC_S'] = 0
    print("We have opened the file")
    
    
    #Calculate the values using the alternate method to begin with 
    module_temperature = pvlib.temperature.sapm_module(poa_global=poa_for_offshore, 
    temp_air = ambient_temp_read_in, wind_speed = wind_speeds_read_in, a = parameter_a, b = parameter_b)
    cell_temperatures = pvlib.temperature.sapm_cell_from_module(module_temperature, poa_for_offshore, 0)
    module_eta = pvlib.pvarray.pvefficiency_adr(poa_for_offshore, cell_temperatures, **adr_params)
    
    
    for j in range(0,  number_of_rows): 
        #There are additional arguments for the ODE function
        args_for_input = np.ndarray((4, ),  float)
        args_for_input[0] = wind_speeds_read_in[j]
        args_for_input[1] = poa_for_offshore[j]  #insolation 
        args_for_input[2] = ambient_temp_read_in[j] 
        args_for_input[3] = water_temperatures_read_in[j] #water temperature
        args_for_input = tuple(args_for_input)
        #We give it 200 time steps for the temperature to reach some kind of 
        # equilibrium 
        time_values = np.linspace(0,  1,  900)

        #We will strart this blank message to be modified if there is an unsuccessful integration. 
        blank_message = "We first assume that there are no issues."
        #Are there any singularities? 
        singularity_value = 0
        singularity_message = "See the singularities which arise at  "
        
        module_temperatures_first_method =  pvlib.temperature.sapm_module(poa_global=poa_for_offshore, 
            temp_air = ambient_temp_read_in, wind_speed = wind_speeds_read_in, a = parameter_a, b = parameter_b)
        
        if j == 0:
           
            #data_read_in['TempsC_S'][j] = 0.12*poa_for_offshore[j]*ambient_temp_read_in[j]
            #For the first row, we take the initial values to be based on the ambient and water temperatures
            ambient = ambient_temp_read_in[0]
            waterT = water_temperatures_read_in[0]
            wind_speed = wind_speeds_read_in[0]
            temperatures = np.array([ambient,  waterT])
            averaged = np.mean(temperatures)
            input_values = np.array( [ambient,  averaged,  waterT])
            calculated_values = odeint(define_cell_temperature,  input_values,  
            time_values, args = (args_for_input[0],  args_for_input[1],  args_for_input[2],  args_for_input[3], ),  full_output=1)
            
            #The real results are in the final row of a 3-column array which we convert to a 
            # dataframe and give names to the columns
            actual_values = pd.DataFrame([calculated_values[0][899]],  columns = ['FT',  'CT',  'BT']).copy()
            data_read_in.loc[j, 'TempF_RM'] = actual_values.loc[0,  'FT']
            print(data_read_in['TempF_RM'][j])
            print("Is the Temp F in row 0")
            data_read_in.loc[j, 'TempC_RM'] = actual_values.loc[0,  'CT']
            data_read_in.loc[j, 'TempB_RM'] = actual_values.loc[0,  'BT']
            
            #The second part of the results include messages which we will spit out into the commentary files 
            the_dict = calculated_values[-1]
            keys_of_the_dict = the_dict.keys()
            #print(keys_of_the_dict)
            the_message = the_dict["message"]
            
            


           

         
        
        elif j > 0:
            #For all rows after the first, we need to take the previous results as the 
            # input values/initial conditions of the ODEs 
            #What the below means: for hours n > 1, the initial conditions (Temperatures for Front, Cell and Back)
            # are the solutions to the previous hour's. o
            # are the solutions to the previous hour's. 
            tempF_prev = data_read_in.loc[j-1,'TempF_RM']
            tempC_prev = data_read_in.loc[j-1,  'TempC_RM']
            tempB_prev = data_read_in.loc[j-1,  'TempB_RM']
            input_values = np.array( [tempF_prev,  tempC_prev,  tempB_prev])
            input_values = np.array( [tempF_prev,  tempC_prev,  tempB_prev])
            #We need to return the results of the ordinary differential equations 
            calculated_values = odeint(define_cell_temperature,  input_values,  
            time_values, args = (args_for_input[0],  args_for_input[1],  args_for_input[2],  args_for_input[3], ),  full_output=1)
            
            #As above, we extract the results we care about and place them in the data frame
            actual_values = pd.DataFrame([calculated_values[0][899]],  columns = ['FT',  'CT',  'BT']).copy()
            data_read_in.loc[j, 'TempF_RM'] = actual_values.loc[0,  'FT']
            data_read_in.loc[j, 'TempC_RM'] = actual_values.loc[0,  'CT']
            data_read_in.loc[j, 'TempB_RM'] = actual_values.loc[0,  'BT']
            


            messages_here = calculated_values[-1]['message']
            keys_included = calculated_values[-1].keys()
            
            
            if messages_here != "Integration successful.":
                error_message = "We have a problem at row number  " + str(j)
                blank_message = blank_message + "  " + error_message
            
            if "tcrit" in keys_included:
                singularity_value = singularity_value + 1
                singularity_message = singularity_message + str(j) + "  and here" 
            
        with open(complete_path_to_save_stats, 'w',  encoding='utf8') as fyt:
            fyt.write(blank_message)
            if singularity_value >= 1:
                fyt.write(singularity_message)
            
            
            
        if j % 10000 == 0:
            string_to_print_progress = "We are at row  " + str(j) + "  of the file" + string_to_read_file_name
            print(string_to_print_progress)
            print("Now we are modifying the data")

            
    
    
    #What does PVLIB say the module temperatures should be?
    data_read_in['TempMod_PVL'] = module_temperatures_first_method
    data_read_in['TempCell_PVL'] = cell_temperatures

    print("We have done the calculations")
        

    data_read_in.to_excel(string_to_print_file_name)
    
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
