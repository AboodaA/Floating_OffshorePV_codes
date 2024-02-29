#from statistics import mean
import numpy as np
from scipy.integrate import odeint 
#import sympy
#from sympy import symbols, Function, dsolve


#Just trying to develop this model 
# Qcond_up is (T_cell - T_front)/R_F
# Qconv_front is hc_r*A*(T_front - T_amb)
# Assume heat is "300" and that the P_s is "500"


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
arc_thickness = 100*10**-9
arc_conductivity = 32
arc_density = 2400

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
def define_front_temperature(insolation,  wind_speed,  ambient_temperature,  initial_front_temperature):
    #Make sure this is in line with the equation in the Rahaman paper 
    sky_temperature = 0.0552*ambient_temperature**(1.5)
    TempF = initial_front_temperature
    convection_param = convection_parameter(wind_speed)
    param_Ps = tau_alpha_param*insolation*area_measurement_for_everything
    param_heat = area_measurement_for_everything*insolation*absorption_coefficient_glass
    front_convection = convection_param*area_measurement_for_everything*(TempF - ambient_temperature)
    front_radiation1 =  stefan_boltzmann_param*glass_emissivity*view_factor*area_measurement_for_everything
    front_radiation2 = (TempF**4) - sky_temperature**4
    front_radiation = front_radiation1*front_radiation2
    dTempF_dt = (param_Ps + param_heat - front_convection - front_radiation)*(1/(glass_mass*glass_specific_heat))
    time_values = np.linspace(0,  1,  3600)
    computed_front_temp = odeint(dTempF_dt,  TempF,  time_values)
    front_temp_value = computed_front_temp[:, 0][3599]
    return front_temp_value

def define_back_temperature(water_temperature,  initial_back_temperature):
    #Now for the back equation 
    #Equation 47
    
    TempB = initial_back_temperature
    Q_b_conv =12
    Q_b_rad = back_layer_emissivity*stefan_boltzmann_param*view_factor*area_measurement_for_everything*((TempB**4) -  (water_temperature**4) )
    Q_cond_bw = (TempB-water_temperature)*(1/back_layer_resistance_total)
    dTempB_dt = (1/(back_cover_mass*back_cover_specific_heat))*(Q_cond_down -(Q_b_conv + Q_b_rad + Q_cond_bw))
   
   
   

def define_cell_temperature(input_values,  t,  *temps):
    
    
    #We don't have to make this simultaneous differential equations if we're only interested in Temp C
    
    #TempF = temps[0]
    TempC = input_values[0]
    #TempB = temps[1]
    
    wind_speed_given = temps[2]
    insolation_given = temps[3]
    wind_speed = wind_speed_given
    insolation = insolation_given
    ambient_temperature = ambient_temperature_given
    water_temperature = water_temperature_given    
    
    
    #See the descirption above 
    
    
    #We define the equation for the front of the panel, see Equation 
    #Equation 45    
    #Now for the cell equation
    #Equation 46
    param_Ps = tau_alpha_param*insolation*area_measurement_for_everything
    P_e = param_Ps*eta_ref*beta_ref*(TempC - 45)
    Q_cond_down = (TempC - TempF)*(1/resistance_front)
    Q_cond_up = -2
    Q_j = simple_fractional_power_loss(insolation)
    dTempC_dt = (1/(silicon_mass*silicon_specific_heat))*(Q_j -(Q_cond_down + P_e + Q_cond_up))
    
    return [dTempC_dt]


wind_speed_given = 25 
insolation_given  = 900 
ambient_temperature_given = 18
water_temperature_given = 35

time_values = np.linspace(0, 1, 3600)
#bidayat = np.array([25,  {25,  25}])
print("Here is our first attempt")

args_for_input = np.ndarray((6, ),  int)
args_for_input[0] = 12
args_for_input[1] = 15
args_for_input[2] = 2.5
args_for_input[3] = 700
args_for_input[4] = 21
args_for_input[5] = 14

#wind_speed_given = 5 
#insolation_given  = 700 
#ambient_temperature_given = 15
#water_temperature_given = 20

#balloons = odeint(define_three_equations,  25,  time_values,  args = args_for_input)
print(balloons[:, 0][0])
#print(balloons[:, 1][3599])
#print(balloons[:, 2][3599])
print(len(balloons[:, 0]))

time_values = np.linspace(0, 100, 4000)
#bidayat = np.array([25, {25,  25}])
print("Here is our second attempt")
balloons = odeint(define_three_equations,  25,  time_values,  args = (12,  15, ))
print(balloons[:, 0][3599])
#print(balloons[:, 1][3599])
#print(balloons[:, 2][3599])
print(len(balloons[:, 0]))




