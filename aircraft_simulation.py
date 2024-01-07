import math
import numpy as np
import matplotlib.pyplot as plt
#calculate technical parameters of aircraft flight

#constants
g = 9.807#for atmosphere calculations we are just going to assume g is a constant 9.807 m/s, which is close enough to be true when very close to the earth

#airline statistics
#structure_statistics = [empty_mass,wing_area,fuselage_length,fuselage_width,zero_lift_cd,lift_to_drag_ratio_linear,max_linear_angle_of_attack,max_linear_lift_coefficient,critical_lift_coefficient,critical_angle,angle_of_incidence]
B787_structure_statistics = [129000,377,57,5.8,0.012,40,13,1.3,20,3]
#engine_statistics = [fuel_energy,intake_efficiency,turbine_efficiency,air_fuel_ratio,bypass_ratio,max_thrust,max_thrust_density]
B787_engine_statistics = [43,0.95,0.45,35,9,320,1.2]
#also note B787, max_fuel = 101'000kg, max_passenger = 400, mtow = 255'000kg
#calculates the air density at specific latitudes 
#Based off calculations  found here https://en.wikipedia.org/wiki/Barometric_formula#Density_equations
#translated from an equivalent MATLAB calculator I built for my AMME2500 Assignment 3
def calculate_air_density(altitude : float) -> float:
    molar_mass_air = 0.02896#molar mass of earths air, kg/mol
    R = 8.314;#the universal gas constant.
    max_altitudes = [11000,20000,32000,47000,51000,71000,86000]#maximum altitude in atmospheric layers
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
    air_density = 0
    return air_density

    #velocity angle of the plane, function only valid for positive x_velocity

def calculate_velocity_angle(x_velocity : float,y_velocity : float) -> tuple[float,float]:
    velocity = math.sqrt((x_velocity**2)+(y_velocity**2))
    angle = math.asin(y_velocity/velocity)
    return velocity,angle

class Structure():
    def __init__(self,empty_mass : float,wing_area : float,fuselage_length : float,fuselage_width : float,zero_lift_cd : float,lift_to_drag_ratio_linear : float,max_linear_angle_of_attack : float,max_linear_lift_coefficient : float,critical_angle : float,angle_of_incidence : float):
        self.empty_mass = empty_mass #mass with no fuel or passengers
        self.wing_area = wing_area #area of the wings, m^2
        self.fuselage_length = fuselage_length #length of the fuselage (cabin cylinder), m
        self.fuselage_width = fuselage_width #width of the fuselage, m
        self.zero_lift_cd = zero_lift_cd #drag coefficient (/m^2 wing area), unrelated to lift
        self.lift_to_drag_ratio_linear = lift_to_drag_ratio_linear #amount of lift generated per unit drag during the linear region (note drag will continue increasing linearly beyond this region even as lift does not)
        self.max_linear_angle_of_attack = math.radians(max_linear_angle_of_attack) #angle of attack (in degrees) where lift stops linearing increasing with angle of attack
        self.max_linear_lift_coefficient = max_linear_lift_coefficient#lift coefficient at the max_linear_angle_of_attack
        self.linear_lift_coefficient = self.max_linear_lift_coefficient/self.max_linear_angle_of_attack#lift coefficient per radian
        self.critical_angle = math.radians(critical_angle)#angle of attack at which lift reaches a maximum
        self.additional_lift_angle = self.critical_angle-self.max_linear_angle_of_attack
        self.angle_of_incidence = math.radians(angle_of_incidence)#angle of attack when the aeroplane is in level flight (how much are the wings tilted up/cambered)
        self.fuselage_area = self.fuselage_length*self.fuselage_width

    def calculate_angle_of_attack(self,pitch_angle : float,velocity_angle : float) -> float:
        angle_of_attack = pitch_angle-velocity_angle
        return angle_of_attack
    
    def calculate_effective_angle_of_attack(self,pitch_angle : float,velocity_angle : float) -> float:
        effective_angle_of_attack = (pitch_angle-velocity_angle)+self.angle_of_incidence
        return effective_angle_of_attack

    def calculate_lift_coefficient_at_effective_angle_of_attack(self,effective_angle_of_attack : float) -> tuple[float,bool]:
        if (effective_angle_of_attack >= -self.max_linear_angle_of_attack) and (effective_angle_of_attack <= self.max_linear_angle_of_attack):
            lift_coefficient = self.linear_lift_coefficient*effective_angle_of_attack
            stall = False
        elif (effective_angle_of_attack >= -self.critical_angle) and (effective_angle_of_attack <= self.critical_angle):
            angle_abs = abs(effective_angle_of_attack)
            this_additional_lift_angle = angle_abs-self.max_linear_angle_of_attack
            additional_lift_fraction = this_additional_lift_angle/self.additional_lift_angle
            additional_lift_coefficient = this_additional_lift_angle*((1+(1-additional_lift_fraction))/2)*self.linear_lift_coefficient
            lift_coefficient = additional_lift_coefficient + self.max_linear_lift_coefficient
            if effective_angle_of_attack<0:
                lift_coefficient = -lift_coefficient
            stall = False
        elif (effective_angle_of_attack > -self.critical_angle*2) and (effective_angle_of_attack < self.critical_angle*2):
                if effective_angle_of_attack<0:
                    mirror_angle_of_attack = (-self.critical_angle*2)-effective_angle_of_attack
                else:
                    mirror_angle_of_attack = (self.critical_angle*2)-effective_angle_of_attack
                lift_coefficient,stall = self.calculate_lift_coefficient_at_effective_angle_of_attack(mirror_angle_of_attack)
                stall = True
        else:
            lift_coefficient = 0
            stall = True
        
        return lift_coefficient,stall
    
    #calculate the coefficient of lift based on the actual angle of attack
    def calculate_lift_coefficient_at_angle_of_attack(self,angle_of_attack : float) -> float:
        effective_angle_of_attack = angle_of_attack + self.angle_of_incidence
        lift_coefficient,stall = self.calculate_lift_coefficient_at_effective_angle_of_attack(effective_angle_of_attack)
        return lift_coefficient
    
    #calculate the induced (by lift) drag coefficient for the wing based on the actual angle of attack
    def calculate_induced_wing_drag_coefficient_at_angle_of_attack(self,angle_of_attack : float) -> float:
        effective_angle_of_attack = abs(angle_of_attack + self.angle_of_incidence)
        induced_wing_drag_coefficient = (effective_angle_of_attack*self.linear_lift_coefficient)/self.lift_to_drag_ratio_linear
        return induced_wing_drag_coefficient

    #calculate the induced (by lift) drag coefficient for the fuselage based on the actual angle of attack
    def calculate_induced_fuselage_drag_coefficient_at_angle_of_attack(self,angle_of_attack : float) -> float:
        effective_angle_of_attack = abs(angle_of_attack)
        induced_fuselage_drag_coefficient = (effective_angle_of_attack*self.linear_lift_coefficient)/self.lift_to_drag_ratio_linear
        return induced_fuselage_drag_coefficient

    #calculate lift (N), this is perpindicular to relative wind speed
    def calculate_lift(self,airspeed : float,angle_of_attack : float,air_density : float) -> float:
        lift_coefficient = self.calculate_lift_coefficient_at_angle_of_attack(angle_of_attack)
        lift = air_density*lift_coefficient*self.wing_area*(airspeed**2)*0.5
        return lift
    
    #calculate the drag induced by the wing at a particular angle of attack
    def calculate_induced_wing_drag(self,airspeed : float,angle_of_attack : float,air_density : float) -> float:
        induced_wing_drag_coefficient = self.calculate_induced_wing_drag_coefficient_at_angle_of_attack(angle_of_attack)
        induced_wing_drag = air_density*induced_wing_drag_coefficient*self.wing_area*(airspeed**2)*0.5
        return induced_wing_drag 
    
    #calculate the drag induced by the fuselage not being in line with the airstream (occurs during pitch up/pitch down movements)
    def calculate_fuselage_drag(self,airspeed : float,angle_of_attack : float,air_density : float) -> float:
        induced_fuselage_drag_coefficient = self.calculate_induced_fuselage_drag_coefficient_at_angle_of_attack(angle_of_attack)
        fuselage_drag = air_density*self.fuselage_area*induced_fuselage_drag_coefficient*(airspeed**2)*0.5
        return fuselage_drag

    #calculate the parasitic drag
    def calculate_parasitic_drag(self,airspeed : float,air_density : float) -> float:
        parasitic_drag = air_density*self.wing_area*(airspeed**2)*0.5*self.zero_lift_cd
        return parasitic_drag
    
    #plots lift coefficient by angle of attack
    def plot_lift_coefficient(self,start_angle : float,end_angle : float,increment : float) -> float:
        angles = np.arange(start_angle,end_angle+increment,increment)
        angles_degrees = list(angles)
        angles : list[float] = list(np.radians(angles))
        lift_coefficients : list[float] = []
        for angle in angles:
            lift_coefficient = self.calculate_lift_coefficient_at_angle_of_attack(angle)
            lift_coefficients.append(lift_coefficient)
        #now plot
        #print(angles_degrees)
        #print(lift_coefficients)
        plt.figure(1)
        plt.plot(angles_degrees,lift_coefficients)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Lift Coefficient')
        plt.show(block=False)
    
    #plots lift and the components of drag by angle of attack
    def plot_lift_and_drag(self,airspeed : float,altitude : float,start_angle : float,end_angle : float,increment : float):
        angles = np.arange(start_angle,end_angle+increment,increment)
        angles_degrees = list(angles)
        angles : list[float] = list(np.radians(angles))
        lifts : list[float] = [] 
        lift_induced_wing_drags : list[float] = []
        lift_induced_fuselage_drags : list[float] = []
        parasitic_drags : list[float] = []
        lift_to_drags : list[float] = []
        air_density = calculate_air_density(altitude)
        for angle in angles:
            lift = self.calculate_lift(airspeed,angle,air_density)
            lift_induced_wing_drag = self.calculate_induced_wing_drag(airspeed,angle,air_density)
            lift_induced_fuselage_drag = self.calculate_fuselage_drag(airspeed,angle,air_density)
            parasitic_drag = self.calculate_parasitic_drag(airspeed,air_density)
            lift_to_drag = lift/(parasitic_drag+lift_induced_wing_drag+lift_induced_fuselage_drag)
            lifts.append(lift)
            lift_induced_wing_drags.append(lift_induced_wing_drag)
            lift_induced_fuselage_drags.append(lift_induced_fuselage_drag)
            parasitic_drags.append(parasitic_drag)
            lift_to_drags.append(lift_to_drag)
        #now plot
        plt.figure(1)
        plt.plot(angles_degrees,lifts)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Lift (N)')
        plt.show(block=False)
        plt.figure(2)
        plt.plot(angles_degrees,lift_induced_wing_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Lift Induced Wing Drag (N)')
        plt.show(block=False)
        plt.figure(3)
        plt.plot(angles_degrees,lift_induced_fuselage_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Lift Induced Fuselage Drag (N)')
        plt.show(block=False)
        plt.figure(4)
        plt.plot(angles_degrees,parasitic_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Parasitic Drag (N)')
        plt.show(block=False)
        plt.figure(5)
        plt.plot(angles_degrees,lift_to_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Lift to Drag')
        plt.show(block=False)


class Engine():
    def __init__(self,fuel_energy : float,intake_efficiency : float,turbine_efficiency : float,air_fuel_ratio : float,bypass_ratio : float,max_thrust : float,density_at_max_thrust : float):
        self.fuel_energy = fuel_energy #energy of the fuel in MJ
        self.intake_efficiency = intake_efficiency #intake efficiency (what fraction of momentum of incoming air is preserved) as coefficient
        self.turbine_efficiency = turbine_efficiency #turbine efficiency (what fraction of fuel energy is converted into thrust) as coefficient
        self.air_fuel_ratio = air_fuel_ratio #air fuel ratio, air/fuel, combustion chamber only
        self.bypass_ratio = bypass_ratio #bypass ratio, bypass air/combustion air
        self.total_air_fuel_ratio = air_fuel_ratio*(bypass_ratio+1) #total air (combustion + bypass)/fuel ratio
        self.max_thrust = max_thrust #max thrust, N
        self.density_at_max_thrust = density_at_max_thrust #air density at which max thrust occurs
    
    def calculate_exhaust_velocity(self,intake_airspeed : float) -> tuple[float,float]:
        energy_incoming_air =(intake_airspeed**2)*0.5#energy of incoming air in J/kg
        exhaust_energy = (((energy_incoming_air*self.intake_efficiency)*self.total_air_fuel_ratio)+(self.fuel_energy*1000000)*self.turbine_efficiency)/(self.total_air_fuel_ratio+1)#energy of exhaust stream in J/kg
        exhaust_velocity = math.sqrt(2*exhaust_energy)#calculate the exhaust velocity of exhaust stream
        exhaust_velocity_gain = exhaust_velocity-(intake_airspeed*self.total_air_fuel_ratio/(self.total_air_fuel_ratio+1))#calculate the gain in velocity
        effective_exhaust_velocity = exhaust_velocity_gain*(self.total_air_fuel_ratio+1)#calculate the effective exhaust velocity
        return exhaust_velocity_gain,effective_exhaust_velocity
    
    def calculate_max_thrust(self,intake_air_density : float) -> float:
        if intake_air_density>self.density_at_max_thrust:
            max_thrust = self.max_thrust
        else:
            max_thrust = (intake_air_density/self.density_at_max_thrust)*self.max_thrust
        return max_thrust

class Plane():
    def __init__(self,structure : Structure,engine : Engine,num_engines : int):
        self.structure = structure
        self.engine = engine
        self.num_engines = num_engines
    
    #calculate the weight force in N
    def calculate_weight_force(self,load_mass : float) -> float:
        weight_force = (load_mass+self.structure.empty_mass)*g
        return weight_force



    #calculate x,y forces excluding thrust
    def calculate_balance_of_forces_xy(self,load_mass : float,velocity : float,velocity_angle : float,pitch : float,altitude : float) -> tuple[float,float]:
        air_density = calculate_air_density(altitude)
        weight_force = self.calculate_weight_force(load_mass)
        x_lift,y_lift,x_drag,y_drag = self.calculate_lift_and_drag_x_y(velocity,velocity_angle,pitch,air_density)
        net_x = -x_lift - x_drag
        net_y = y_lift - y_drag - weight_force
        return net_x,net_y
    
    

    #calculate the x and y components of lift and drag
    def calculate_lift_and_drag_x_y(self,velocity : float,velocity_angle : float,pitch : float,air_density : float) -> tuple[float,float,float,float]:
        angle_of_attack = self.structure.calculate_angle_of_attack(pitch,velocity_angle)
        lift = self.structure.calculate_lift(velocity,angle_of_attack,air_density)
        lift_induced_wing_drag = self.structure.calculate_induced_wing_drag(velocity,angle_of_attack,air_density)
        lift_induced_fuselage_drag = self.structure.calculate_fuselage_drag(velocity,angle_of_attack,air_density)
        parasitic_drag = self.structure.calculate_parasitic_drag(velocity,air_density)
        total_drag = lift_induced_fuselage_drag + lift_induced_wing_drag + parasitic_drag
        y_drag = total_drag*math.sin(velocity_angle) #vertical component of drag
        x_drag = total_drag*math.cos(velocity_angle) #horizontal component of drag
        y_lift = lift*math.cos(velocity_angle) #vertical component of lift
        x_lift = lift*math.sin(velocity_angle) #horizontal component of lift
        return x_lift,y_lift,x_drag,y_drag

    #displays a plot of how lift and drag vertical and horizontal components vary by pitch offset from the velocity angle
    def plot_lift_drag_x_y_by_angle(self,velocity : float,velocity_angle : float,start_pitch_offset : float,end_pitch_offset : float,pitch_offset_increment : float,altitude : float):
        angles = np.arange(velocity_angle+start_pitch_offset,velocity_angle+end_pitch_offset,pitch_offset_increment)
        velocity_angle = math.radians(velocity_angle)
        angles_degrees = list(angles)
        angles : list[float] = list(np.radians(angles))
        x_lifts : list[float] = []
        y_lifts : list[float] = []
        x_drags : list[float] = []
        y_drags : list[float] = []
        air_density = calculate_air_density(altitude)
        for angle in angles:
            x_lift,y_lift,x_drag,y_drag = self.calculate_lift_and_drag_x_y(velocity,velocity_angle,angle,air_density)
            #print(x_lift,' ',y_lift,' ',x_drag,' ',y_drag)
            x_lifts.append(x_lift)
            y_lifts.append(y_lift)
            x_drags.append(x_drag)
            y_drags.append(y_drag)
        #now plot
        plt.figure(1)
        plt.plot(angles_degrees,x_lifts)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('X Lift (N)')
        plt.show(block=False)
        plt.figure(2)
        plt.plot(angles_degrees,y_lifts)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Y Lift (N)')
        plt.show(block=False)
        plt.figure(3)
        plt.plot(angles_degrees,x_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('X Drag (N)')
        plt.show(block=False)
        plt.figure(4)
        plt.plot(angles_degrees,y_drags)
        plt.xlabel('Angle (degrees)')
        plt.ylabel('Y Drag (N)')
        plt.show(block=False)
        

#some examples
B787_structure = Structure(*B787_structure_statistics)
B787_engine = Engine(*B787_engine_statistics)
B787 = Plane(B787_structure,B787_engine,2)
