#from statistics import mean
import numpy as np
from scipy.integrate import odeint 
from statistics import mean
#import sympy
#from sympy import symbols, Function, dsolve


#Numbers copied from the table on p. 178 of Rahaman et al or from the internet
stefan_boltzmann_param = 5.7*10**(-8)
area_measurement_for_everything = 1.75
nusselt_number_free_simple = 25
volume_of_panel_revealed = 0.2
eva_layer_mass = 960*area_measurement_for_everything*500*(10**(-6))
tedlar_back_mass = 1200*area_measurement_for_everything*(1*(10**-4))
back_cover_mass = tedlar_back_mass + eva_layer_mass
back_cover_specific_heat = 2090
#Assuming tthat the specific heat capacity of the EVA layer will be dominant
view_factor = 0.5 
#View factor is fixed since the panels are flat down on the HDPE
eta_ref = 0.172
beta_ref = 4*10**(-3)


#We might have to change this once I find a more reliable value, but the energy which is not accounted for by tau_alpha has to go somewhere
absorption_coefficient_glass = 0.085
tau_alpha_param =0.9


#Values important for the glass/ARC layer
glass_thickness = 0.003
glass_conductivity = 1.8
glass_density = 3000
glass_emissivity = 0.91
glass_mass = glass_density*glass_thickness*area_measurement_for_everything
glass_specific_heat = 500
glass_resistance = glass_thickness/glass_conductivity 
arc_thickness = 100*10**-9
arc_conductivity = 32
arc_density = 2400
arc_resistance = arc_thickness/arc_conductivity 
resistance_front = glass_resistance + arc_resistance



#Values important for the silicon cell 
silicon_thickness = 225*10**-6
silicon_conductivity = 32
silicon_density = 2330
silicon_mass = silicon_density*silicon_thickness*area_measurement_for_everything
silicon_specific_heat = 677


#Values important for the 
back_layer_emissivity = 0.85 
back_layer_thermal_conductivity = 0.2 
hdpe_layer_thermal_conductivity = 0.48
back_layer_thickness = 1*10**(-4)
hdpe_layer_thickness = 2*10**(-3)
back_layer_resistance = back_layer_thickness/(area_measurement_for_everything*back_layer_thermal_conductivity)
hdpe_layer_resistance = hdpe_layer_thickness/(area_measurement_for_everything*hdpe_layer_thermal_conductivity)
back_layer_resistance_total = back_layer_resistance + hdpe_layer_resistance


#We will need to know the Ohmic power lost for the equation for the 
def simple_fractional_power_loss(insolation):
	adjusted_insolation = insolation/1000
	#We are assuming that all 72 cells in the module of 320 W are 
	# connected in a single series
	#
	current_generated = adjusted_insolation*9.28
	voltage_in_string = 36.6
	power_generated = voltage_in_string * current_generated
	power_lost_ohmic = 0.0268*power_generated
	return power_lost_ohmic

def convection_parameter(wind_speed):
#I simplified things by using the data found in the paper by 
# Hagishima, Tanimoto, Narita; 2005
    conv_param = 0
    if wind_speed > 0 and wind_speed <6:
        conv_param = 8 + 2.33*wind_speed
    elif wind_speed == 0:
        conv_param = 8
    elif wind_speed >= 6:
        conv_param = 25
    return conv_param

#Parameters which we will use for Equation 1: heat transfer from the cell to the front of the panel 
#We will just use a linear interpolation from 
#We need the mass of the glass    
 
def define_cell_temperature(input_values,  t,  *temps):
    
    #We don't have to make this simultaneous differential equations if we're only interested in Temp C
    
    TempF0 = input_values[0]
    TempC0 = input_values[1]
    TempB0 = input_values[2]    
    wind_speed_given = temps[0]
    insolation_given = temps[1]
    ambient_temperature = temps[2]
    water_temperature = temps[3]    
    
    #See the descirption above 
    
    #insolation,  wind_speed,  ambient_temperature,  initial_front_temperature
    #water_temperature,  initial_back_temperature)
    #TempB = define_back_temperature(water_temperature_given,  TempB0)
    
    sky_temperature = 0.0552*ambient_temperature**(1.5)
    convection_param = convection_parameter(wind_speed_given)
    param_Ps = tau_alpha_param*insolation_given*area_measurement_for_everything
    param_heat = area_measurement_for_everything*insolation_given*absorption_coefficient_glass
    front_convection = convection_param*area_measurement_for_everything*(TempF0 - ambient_temperature)
    front_radiation1 =  stefan_boltzmann_param*glass_emissivity*view_factor*area_measurement_for_everything
    front_radiation2 = (TempF0**4) - sky_temperature**4
    front_radiation = front_radiation1*front_radiation2
    dTempF_dt = (param_Ps + param_heat - front_convection - front_radiation)*(1/(glass_mass*glass_specific_heat))
    
    #We define the equation for the front of the panel, see Equation 
    #Equation 45    
    #Now for the cell equation
    #Equation 46
    param_Ps = tau_alpha_param*insolation_given*area_measurement_for_everything
    P_e = param_Ps*eta_ref*beta_ref*(TempC0 - 45)
    Q_cond_down = (TempC0 - TempB0)*(1/back_layer_resistance_total)
    Q_cond_up =(TempC0 - TempF0)*(1/resistance_front)
    Q_j = simple_fractional_power_loss(insolation_given)
    dTempC_dt = (1/(silicon_mass*silicon_specific_heat))*(Q_j -(Q_cond_down + P_e + Q_cond_up))
    
    #This is where we define the back panel temperature 
    #Equation 47 
    Q_b_conv =convection_param*area_measurement_for_everything*(TempB0-water_temperature)
    Q_b_rad = back_layer_emissivity*stefan_boltzmann_param*view_factor*area_measurement_for_everything*((TempB0**4) -  (water_temperature**4) )
    Q_cond_bw = (TempB0-water_temperature)*(1/back_layer_resistance_total)
    dTempB_dt = (1/(back_cover_mass*back_cover_specific_heat))*(Q_cond_down -(Q_b_conv + Q_b_rad + Q_cond_bw))

    return [dTempF_dt,  dTempC_dt,  dTempB_dt]





def simple_cell_temperature(input_values,  t,  *temps):
    #We don't have to make this simultaneous differential equations if we're only interested in Temp C
    TempF0 = input_values[0]
    TempC0 = input_values[1]
    wind_speed_given = temps[0]
    insolation_given = temps[1]
    ambient_temperature = temps[2]
    water_temperature = temps[3]
    TempB0 = input_values[2]    
    
    #See the descirption above     
    #insolation,  wind_speed,  ambient_temperature,  initial_front_temperature
    #water_temperature,  initial_back_temperature)
    #TempB = define_back_temperature(water_temperature_given,  TempB0)
    
    sky_temperature = 0.0552*ambient_temperature**(1.5)
    convection_param = convection_parameter(wind_speed_given)
    param_Ps = tau_alpha_param*insolation_given*area_measurement_for_everything
    param_heat = area_measurement_for_everything*insolation_given*absorption_coefficient_glass
    front_convection = convection_param*area_measurement_for_everything*(TempF0 - ambient_temperature)
    front_radiation1 =  stefan_boltzmann_param*glass_emissivity*view_factor*area_measurement_for_everything
    front_radiation2 = (TempF0**4) - sky_temperature**4
    front_radiation = front_radiation1*front_radiation2
    dTempF_dt = (param_Ps + param_heat - front_convection - front_radiation)*(1/(glass_mass*glass_specific_heat))
    
    #We define the equation for the front of the panel, see Equation 
    #Equation 45    
    #Now for the cell equation
    #Equation 46
    param_Ps = tau_alpha_param*insolation_given*area_measurement_for_everything
    P_e = param_Ps*eta_ref*beta_ref*(TempC0 - 45)
    Q_cond_down = (TempC0 - TempB0)*(1/back_layer_resistance_total)
    Q_cond_up =(TempC0 - TempF0)*(1/resistance_front)
    Q_j = simple_fractional_power_loss(insolation_given)
    dTempC_dt = (1/(silicon_mass*silicon_specific_heat))*(Q_j -(Q_cond_down + P_e + Q_cond_up))
    
    #What happens if we just set the back temperature = water temperature
    #There is no convection here since there is no temperature difference
    #Same for radiation back and others 
    Q_b_conv = 0
    Q_b_rad = 0
    Q_cond_bw = 0
    dTempB_dt = (1/(back_cover_mass*back_cover_specific_heat))*(Q_cond_down -(Q_b_conv + Q_b_rad + Q_cond_bw))

    return [dTempF_dt,  dTempC_dt,  dTempB_dt]



