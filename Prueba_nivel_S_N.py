from copy import copy
import pyopenms as pyo
import numpy as np
import Class_Spectrum_Model as csm
import os
import Class_parser as cp
import statistics
import Input_plantilla as ip
import Filter_Functions as ff
import Grass_Functions as gf



def main():
    path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    list_of_values = ip.open_negative_template("pos_neg_template.csv", path_in, ";")
    user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    number_of_windows = len(list_of_values[0])

    max_peak_list = []
    grass_level_list = []
    signal_noise_ratio_list = []

    reference_masses_list = []

    coelution_peaks_list = []

    crosstalk_list = []

    for window in range(number_of_windows):

        #### Template values
        name = list_of_values[0][window]
        name_file = name + ".mzML"

        retention_time = list_of_values[1][window]

        number_of_scans = list_of_values[2][window]

        quality = list_of_values[3][window]

        precursor_mz = float(list_of_values[4][window])

        precursor_intensities = float(list_of_values[5][window])
        
        approximate_grass_level = list_of_values[6][window]

        coelution_template = list_of_values[7][window]

        reference_masses_template = list_of_values[8][window]

        detected_peaks = list_of_values[9][window]
        
        delta_mz = 0.01



        #### Find S/N

        ## Find spectra within RT and MZ window
        ms1_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, precursor_mz, retention_time[0], delta_mz, retention_time[1], ms_level_1 = True)
        ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, precursor_mz, retention_time[0], delta_mz, retention_time[1])


        ## Average spectra found
        average_ms1 = cp.average_spectra_ordered(ms1_spectra_found, 0.03, ms1 = True)
        average_ms2 = cp.average_spectra_ordered(ms2_spectra_found, delta_mz)


        ## Grass level in MS2
        be_grass_level = gf.be_measure_grass_level(average_ms2, increase = 10)
        end_grass_level = gf.end_measure_grass_level_stdev(average_ms2, increase = 10)
        grass_level = (be_grass_level + end_grass_level)/2

        grass_level_list.append(grass_level)


        ## Find coelution
        coelution_peaks = ff.is_coelution(average_ms1, average_ms2.get_precursor_mz()[0], percentage_accetable_coelution = 40)

        coelution_peaks_list.append(coelution_peaks)


        ## Find maximum intensity peak and reference masses
        max_peak, refence_masses_found = average_ms2.get_most_intense_peak(user_reference_masses_list, delta_mz)
        reference_masses = ff.filter_masses_by_intensity(max_peak, refence_masses_found, grass_level, 40)
        
        max_peak_list.append(max_peak)
        reference_masses_list.append(reference_masses)


        ## Find crosstalk
        crosstalk_found = ff.find_crosstalk_peaks(average_ms2)
        crosstalk = ff.filter_masses_by_intensity(max_peak, crosstalk_found, max_peak.get_intensity()*0.1, 40)

        crosstalk_list.append(crosstalk)


        ## Calculate S/N
        maximum_intensity = max_peak.get_intensity()
        signal_noise_ratio = maximum_intensity / grass_level

        signal_noise_ratio_list.append(signal_noise_ratio)

        
        print("Template coelution:", end="")
        for mz in coelution_template:
            print("MZ:", mz, end=",")
        print("")

        print("")


        # Reference masses
        print("Reference masses found:", end = "")
        for peak in refence_masses_found:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Reference massses template:", end = "")
        for mz in reference_masses_template:
            print("MZ:", mz, end=",")
        print("")


        print("")


        # Crosstalk
        print("Cross talk peaks found:", len(crosstalk[2]))


        print("")


        # Signal to noise ratio
        print("Signal to noise ratio:", signal_noise_ratio)
        print("Max peak:", "MZ:", max_peak.get_mz(), "I:", max_peak.get_intensity())

        

        print("")
        print("Spectrum", window, "done")
        print("______________________________")

    
    # Print results
    for spectrum_index in range(len(list_of_values[0])):
        print("")
        print("")
        print("##########################################################################################")
        print("__________________________________________________________________________________________")
        
        print("Number spetrum:", spectrum_index)
        
        # Name
        print("Experiment name:", list_of_values[0][spectrum_index])

        # Retention time
        print("Retention time:", list_of_values[1][spectrum_index][0])

        # Quality
        print("Quality:", list_of_values[3][spectrum_index])

        # Precursor
        print("Precursor: MZ:", list_of_values[4][spectrum_index], "I:", list_of_values[5][spectrum_index])

        print("")

        # Coelution
        print("Proper coelution found peaks:", end = "")
        for peak in coelution_peaks_list[spectrum_index][0]:
            print(peak.get_mz(), end = ", ")
        print("")

        print("Coelution template peaks:", end = "")
        for mz in list_of_values[7][spectrum_index]:
            print(mz, end = ", ")
        print("")

        print("")


        # Reference masses
        print("Reference masses found:", end = "")
        for peak in reference_masses_list[spectrum_index][2]:
            print(peak.get_mz(), end = ", ")
        print("")

        print("Refeence masses template peaks:", end = "")
        for mz in list_of_values[8][spectrum_index]:
            print(mz, end = ", ")
        print("")

        print("")


        # Crosstalk peaks
        print("Crosstalk peaks found:", end = "")
        for peak in crosstalk_list[spectrum_index][2]:
            print(peak.get_mz(), end = ", ")
        print("")

        print("")


        # S/N ratio
        print("Signal to noise ratio:", signal_noise_ratio_list[spectrum_index])
        print("Max peak:", "MZ:", max_peak_list[spectrum_index].get_mz(), "I:", max_peak_list[spectrum_index].get_intensity())

        ###############################################################################################################################

    
    with open("Signal_to_noise_ratio.txt", "w") as f:
        f.write("Name,Quality,S/N,Strong_Coelution,Weak_Coelution,Strong_Reference_masses,Weak_Reference_masses,Strong_Crosstalk,Weak_Crosstalk\n")
        for item in range(len(signal_noise_ratio_list)):
            f.write(str(list_of_values[0][item]) + "," + str(list_of_values[3][item]) + "," + str(signal_noise_ratio_list[item]) + ",")
            
            coelution_peaks = coelution_peaks_list[item][0]
            f.write(str(len(coelution_peaks)) + ",")

            weak_coelution_peaks = coelution_peaks_list[item][1]
            f.write(str(len(weak_coelution_peaks)) + ",")

            reference_masses = reference_masses_list[item][2]
            f.write(str(len(reference_masses)) + ",")

            weak_reference_masses= reference_masses_list[item][1]
            f.write(str(len(weak_reference_masses)) + ",")

            crosstalk_peaks = crosstalk_list[item][2]
            f.write(str(len(crosstalk_peaks)) + ",")

            weak_crosstalk_peaks = crosstalk_list[item][1]
            f.write(str(len(weak_crosstalk_peaks)) + "\n")






if __name__ == "__main__":
    main()