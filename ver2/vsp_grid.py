import numpy as np
from itertools import product
from dataclasses import replace
import time
from config import *
from vsp_analysis import VSPAnalyzer, writeAnalysisResults, loadAnalysisResults, visualize_results
from models import *


def runVSPGridAnalysis(aircraftParamConstraint: AircraftParamConstraints,presetValues: PresetValues, baseAircraft: Aircraft):

        ## Variable lists using for optimization
        span_list = np.arange(
                aircraftParamConstraint.span_min, 
                aircraftParamConstraint.span_max + aircraftParamConstraint.span_interval/2, 
                aircraftParamConstraint.span_interval
                )
        AR_list = np.arange(
                aircraftParamConstraint.AR_min, 
                aircraftParamConstraint.AR_max + aircraftParamConstraint.AR_interval/2, 
                aircraftParamConstraint.AR_interval
                )
        taper_list = np.arange(
                aircraftParamConstraint.taper_min, 
                aircraftParamConstraint.taper_max + aircraftParamConstraint.taper_interval/2, 
                aircraftParamConstraint.taper_interval
                )
        twist_list = np.arange(
                aircraftParamConstraint.twist_min, 
                aircraftParamConstraint.twist_max + aircraftParamConstraint.twist_interval/2, 
                aircraftParamConstraint.twist_interval
                )
        total_mass_list = np.arange(
                aircraftParamConstraint.m_total_min, 
                aircraftParamConstraint.m_total_max + aircraftParamConstraint.m_total_interval/2, 
                aircraftParamConstraint.m_total_interval
                )

        print(f"\nspan list: {span_list}")
        print(f"AR list: {AR_list}")
        print(f"taper list: {taper_list}")
        print(f"twist list: {twist_list}")
        print(f"total mass list: {total_mass_list}\n")

        vspAnalyzer = VSPAnalyzer(presetValues)

        total_combinations = np.prod([len(arr) for arr in [span_list,AR_list,taper_list,twist_list,total_mass_list]])

        for i, (span, AR, taper, twist, m_total) in enumerate(product(span_list,AR_list,taper_list,twist_list,total_mass_list)):
                print(f"[{time.strftime('%Y-%m-%d %X')}] VSP Grid Progress: {i+1}/{total_combinations} configurations")
                aircraft = replace(baseAircraft, mainwing_span = span, mainwing_AR = AR , mainwing_taper = taper, mainwing_twist = twist, m_total = m_total)   

                vspAnalyzer.setup_vsp_model(aircraft)
                analResults = vspAnalyzer.calculateCoefficients(
                alpha_start = -3.5, alpha_end = 13, alpha_step = 0.5,
                CD_fuse = np.full(int(round((13 - (-3.5)) / 0.5)) + 1, 0.03),

                AOA_stall = 13,
                AOA_takeoff_max = 10,
                AOA_climb_max = 8,
                AOA_turn_max = 8,

                m_total = m_total,

                clearModel=False)

                # selected_outputs = ["hash", "span", "AR", "taper", "twist", "alpha_list", "CL", "CD_total"]
                writeAnalysisResults(analResults)
                vspAnalyzer.clean()

if __name__ == "__main__":
    runVSPGridAnalysis(
            AircraftParamConstraints (
                #Constraints for constructing the aircraf
                m_total_max = 8600,
                m_total_min = 8500,
                m_total_interval = 100,
                # wing parameter ranges
                span_max = 1800.0,                     # mm
                span_min = 1800.0,
                span_interval = 100.0,
                AR_max = 5.45,
                AR_min = 5.45,
                AR_interval = 0.05,
                taper_max = 0.45,                      # (root chord) / (tip chord)
                taper_min = 0.45,
                taper_interval = 0.05,
                twist_max = 0.0,                       # degree
                twist_min = 0.0,
                twist_interval = 1.0,
                ),
            PresetValues(
                    m_x1 = 0.2,                       # kg
                    x1_flight_time = 30,              # sec
                    max_battery_capacity = 2250,      # mAh (per one battery)
                    Thrust_max = 6.6,                 # kg (two motors)
                    min_battery_voltage = 20,         # V (원래는 3 x 6 = 18 V 인데 안전하게 20 V)
                    propulsion_efficiency = 0.8,      # Efficiency of the propulsion system
                    score_weight_ratio = 1            # mission2/3 score weight ratio
                    ), 
            Aircraft(
               m_total = 8500, m_fuselage = 5000,

               wing_density = 0.0000852, spar_density = 1.0,

               mainwing_span = 1800,        
               mainwing_AR = 5.45,           
               mainwing_taper = 0.65,        
               mainwing_twist = 0.0,        
               mainwing_sweepback = 0,   
               mainwing_dihedral = 5.0,     
               mainwing_incidence = 2.0,    

               flap_start = [0.05, 0.4],            
               flap_end = [0.25, 0.6],              
               flap_angle = [20.0, 15.0],           
               flap_c_ratio = [0.35, 0.35],         

               horizontal_volume_ratio = 0.7,
               horizontal_area_ratio = 0.25, 
               horizontal_AR = 4.0,         
               horizontal_taper = 1,      
               horizontal_ThickChord = 8,

               vertical_volume_ratio = 0.053,
               vertical_taper = 0.6,        
               vertical_ThickChord = 9  
               ))

