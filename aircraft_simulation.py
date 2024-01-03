import math
import numpy as np
#calculate technical parameters of aircraft flight

#constants
g = 9.807#for atmosphere calculations we are just going to assume g is a constant 9.807 m/s, which is close enough to be true when very close to the earth


#calculates the air density at specific latitudes 
#Based off calculations  found here https://en.wikipedia.org/wiki/Barometric_formula#Density_equations
#translated from an equivalent MATLAB calculator I built for my AMME2500 Assignment 3
def air_density_calc(altitude):
    molar_mass_air = 0.02896#molar mass of earths air, kg/mol
    R = 8.314;#the universal gas constant.
    max_altitudes =[11000,20000,32000,47000,51000,71000,86000]#maximum altitude in atmospheric layers
    temperature_lapse_rates = [-0.0065,0,0.001,0.0028,0,-0.0028,-0.002]#temperature lapse rate in that layer, K/m
    base_density = [1.225,0.36391,0.08803,0.01322,0.00143,0.00086,0.000064]#base density at bottom of each layer, kg/m^3
    base_temperature = [288.15,216.65,216.65,228.65,270.65,270.65,214.65]#temperature at the bottom of each layer, kelvin
    num_layers = len(max_altitudes)#number of layers in our atmospheric model
    current_layer = 0#current layer of the atmosphere we are testing
    while current_layer<num_layers:#go through all layers of the atmosphere till we find the correct layer
        if altitude<max_altitudes[current_layer]:#if we are within the current layer, calculate stuff
            base_density = base_density[current_layer]#extract base data for current layer
            base_temperature = base_temperature[current_layer]
            local_lapse_rate = temperature_lapse_rates[current_layer]
            #determine the base altitude of the current layer
            if current_layer==0:
                base_altitude = 0
            else:
                base_altitude = max_altitudes[current_layer-1];
            if local_lapse_rate==0:#if no temperature lapse, use below equation
                exponent = (-g*molar_mass_air*(altitude-base_altitude)/(R*base_temperature))
                air_density = base_density*math.exp(exponent)
                return air_density#we have sucessfully calculated the air density
            else:#if there is a temperature lapse, use below equation
                exponent = (1 + ((g*molar_mass_air)/(R*local_lapse_rate)))
                temperature_ratio = (base_temperature/(base_temperature+local_lapse_rate*(altitude-base_altitude)))
                air_density = base_density*(temperature_ratio**exponent)
                return air_density#we have sucessfully calculated the air density

        else:#if above maximum altitude for current layer
            current_layer = current_layer+1#move up to next layer
    #we have run out of layers of the atmosphere, so we must be in space, where
    #air density is negligible
    air_density = 0;
    return air_density