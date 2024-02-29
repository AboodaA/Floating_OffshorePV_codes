#In an earlier version of this paper, we used heat index/apparent temperatures. We show below how this could have been inserted in the code for the land-based PV sites. 

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
