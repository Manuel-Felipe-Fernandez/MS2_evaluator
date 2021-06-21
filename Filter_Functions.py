# Filter Functions
import Class_Spectrum_Model as csm
import Class_parser as cp
import Grass_Functions as gf
import csv
import os
import Input_plantilla as ip
import statistics 

#### Filtering peaks by intensity
def filter_masses_by_intensity(maximum_intensity_peak, peaks, lower_threshold, weak_percentage = False):
    """
    Funcion that classifies input peaks by their intensity relative to a maximum intensity.
    If weak_percentage is not False, it classifies in:
     - not accounted for: means to little intensity to be considered relevant.
     - weak: means that it is relevant, but not as decisive.
     - strong: relevant peak compared to maximum intensity.

    :param maximum_intensity_peak: Peak of maximum intensity in MS2
    :type maximum_intensity_peak: Peak_object
    :param peaks: Reference mass or cross talk peaks to be classified
    :type peaks: [Peak_object] 
    :returns: Classified peaks in format [[not], [weak], [strong]]
    :rtype: List of [Peak_object]
    """

    maximum_intensity = maximum_intensity_peak.get_intensity()
    not_list = []
    weak_list = []
    strong_list = []

    for peak in peaks:
        done = False
        i_peak = peak.get_intensity()
        
        if i_peak < lower_threshold:

            not_list.append(peak)
        
        else:

            if weak_percentage != False:

                medium_threshold = maximum_intensity * weak_percentage / 100
            
                if i_peak < medium_threshold:

                    weak_list.append(peak)
                
                else:

                    strong_list.append(peak)
            
            else:

                strong_list.append(peak)
    
    return_list = [not_list, weak_list, strong_list]
    return(return_list)

            
#### Find cross_talk
def find_crosstalk_peaks(spectrum_in, delta_crosstalk = 1.3):
    """
    Function that finds crosstalk within a spectrum
    """
    peaks = spectrum_in.get_peaks()
    precursor_mz = spectrum_in.get_precursor_mz()[0]
    upper_precursor_mz = precursor_mz + delta_crosstalk
    
    crosstalk_peaks = []

    for peak in peaks:
        
        mz = peak.get_mz()

        if mz > upper_precursor_mz:

            crosstalk_peaks.append(peak)
    
    return(crosstalk_peaks)


#### Finding mass references
def find_reference_massses(spectrum_in, reference_masses, delta_mz = 0.01):
    """
    Function that finds given reference masses in a given MS2 spectrum
    :param spectrum_in: MS2 spectrum in
    :type spectrum_in: Spectrum_object
    :reference_masses: List of reference mz
    :type reference_masses: List of float
    :return: list of reference mass peaks
    :rtype: list of Peak_object 
    """
    reference_masses.sort()

    peaks = spectrum_in.get_peaks()

    pos_peak = 0
    pos_ref_mass = 0
    
    found_ref_mass = []

    while pos_peak < len(peaks) and pos_ref_mass < len(reference_masses):

        reference_mz = reference_masses[pos_ref_mass]

        mz_reference_lower = reference_mz - delta_mz
        mz_reference_upper = reference_mz + delta_mz

        peak = peaks[pos_peak]
        mz_peak = peak.get_mz()

        if mz_reference_lower <= mz_peak and mz_reference_upper >= mz_peak:
            
            found_ref_mass.append(peak)
            
            pos_ref_mass += 1
            pos_peak += 1
        
        if mz_reference_lower > mz_peak:
            
            pos_peak += 1
        
        if mz_reference_upper < mz_peak:

            pos_ref_mass += 1
    
    return(found_ref_mass)

        



#### Finding coelution
def is_coelution(spectrum_in, ms2_precursor, da_after_precursor = 1.3, delta_mz = 0.03, percentage_intensity_not_coelution = 10, percentage_accetable_coelution = False):
    """
    Function that finds if a given MS1 spectrum has coelution in it
    """

    upper_mz = ms2_precursor + da_after_precursor

    precursor_mz_upper = ms2_precursor + delta_mz
    precursor_mz_lower = ms2_precursor - delta_mz

    # Ion +1 to ignore in the spectrum
    ignore_peak_mz = ms2_precursor + 1
    ignore_upper_mz = ignore_peak_mz + delta_mz
    ignore_lower_mz = ignore_peak_mz - delta_mz

    peaks = spectrum_in.get_peaks()
    reverse_peaks = reversed(peaks)

    position = 0
    for peak in reverse_peaks:
        mz = peak.get_mz()

        if mz <= precursor_mz_upper and mz >= precursor_mz_lower:
            precursor_mz = mz
            precursor_intensity = peak.get_intensity()
            precursor_peak = peak
            # print("Found precursor in MS1: Mz:", precursor_mz, "Intensity:", precursor_intensity)
            break
        position += 1

    # print(spectrum_in.get_size())
    position = spectrum_in.get_size() - position

    # Intensity of peak to consider as coelution calculation
    # Below this threshold, nothing is considered coelution
    not_coelution_threshold = precursor_intensity * percentage_intensity_not_coelution / 100
    # Below this threshold, coelution is considered acceptable
    if percentage_accetable_coelution != False:
        acceptable_coelution_threshold = precursor_intensity * percentage_accetable_coelution / 100

    acceptable_coelution = list()
    proper_coelution = list()
    coelution = [proper_coelution, acceptable_coelution, precursor_peak]

    for peak in peaks[position:]:
        mz = peak.get_mz()

        if mz < upper_mz:
            
            # We search for peaks different to the ion +1
            if mz > ignore_upper_mz or mz < ignore_lower_mz:
                intensity = peak.get_intensity()
                
                if intensity > not_coelution_threshold:
                    
                    if percentage_accetable_coelution == False:
                        coelution[0].append(peak)

                    else:
                        
                        if intensity > acceptable_coelution_threshold:
                            coelution[0].append(peak)
                        else:
                            coelution[1].append(peak)          

        else:
            break

    """
    print("Coelution_list")
    print("Proper_coelution:", end="")
    for peak in coelution[0]:
        print("MZ:", peak.get_mz(), "Intensity", peak.get_intensity(), end=",")
    print("\nAcceptable_coelution:", end="")
    for peak in coelution[1]:
        print("MZ:", peak.get_mz(), "Intensity", peak.get_intensity(), end=",")
    print("")
    """

    return(coelution)


            

def is_coelution_2(spectrum_in, da_after_precursor = 1.3, precentage_precursor_intensity = 10, delta_mz = 0.03):
    """
    Function that finds if a given MS1 spectrum has coelution in it
    """
    precursor_mz = spectrum_in.get_precursor_mz()[0]
    precursor_intensity = spectrum_in.get_precursor_intensity()[0]

    precursor_peak_spectrum = find_precursor_in_spectrum(spectrum_in, delta_mz)

    if precursor_peak_spectrum == False:
        coelution = "Precursor not found in spectrum"
        return(coelution)

    # print("Precursor peak values are: MZ:", precursor_peak_spectrum.get_mz(), "I:", precursor_peak_spectrum.get_intensity())

    coelution = False
    intensity_spectrum = precursor_peak_spectrum.get_intensity()
    intensity_spectrum_10 = intensity_spectrum * precentage_precursor_intensity / 100

    spectrum_peaks = spectrum_in.get_peaks()
    for peak in reversed(spectrum_peaks):
        
        if peak.get_mz() > precursor_peak_spectrum.get_mz():

            if peak.get_intensity() >= intensity_spectrum_10:
                coelution = True
                break

    return(coelution)

        
        


#### Put this function inside Spectrum_object later
def find_precursor_in_spectrum(spectrum_in, delta_mz = 0.03):
    """
    Function that finds the precursor intensity and mz inside the spectrum
    :param delta_mz: delta to be consider a peak as the precursor peak
    :type: float
    :return: peak with values of mz and intensity
    :rtype: Peak_object
    """
    # We define precursor mz and intensity
    precursor_mz = spectrum_in.get_precursor_mz()[0]
    precursor_intensity = spectrum_in.get_precursor_intensity()[0]
    print("Precursor values are", "MZ:", precursor_mz, "I:", precursor_intensity)

    # We define delta for precursor peak in spectrum
    mz_upper = precursor_mz + delta_mz
    mz_lower = precursor_mz - delta_mz

    spectrum_peaks = spectrum_in.get_peaks()
    for peak in reversed(spectrum_peaks):
        
        mz = peak.get_mz()

        if mz >= mz_lower and mz <= mz_upper:

            precursor_mz_spectrun = peak.get_mz()
            precursor_i_spectrun = peak.get_intensity()
            
            print("Found precursor in spectrum", "MZ:", precursor_mz_spectrun, "I:", precursor_i_spectrun)
            
            return(peak)
    
    return(False)


    
def open_template(template_file, path_in):
    """
    Reads template file, reads scans by rt and mz windows from experiments in the same folder.
    Prints if the window has coelution or not.
    """

    os.chdir(path_in)
    
    coelution_list = []
    quality_list = []
    experiment_list = []

    with open(template_file) as csv_template:
        csv_reader = csv.reader(csv_template, delimiter = ",")
        line_count = 0
        sum_size = 0
        sum_number_of_spectra = 0

        for row in csv_reader:
            if line_count == 0:
                pass
                
            else:
                print(line_count)
                list_of_values_in = row

                name = list_of_values_in[0][:-2]
                name_file = name + ".mzML"
                retention_time_window = list_of_values_in[2]
                retention_time = ip.rt_window_to_delta(retention_time_window)
                quality = list_of_values_in[4]
                mz_precursor = float(list_of_values_in[5])
                delta_mz = 1.3
                mz_in_template = list(filter(lambda x: x != "", list_of_values_in[9:]))

                ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])
                print("Number of MS2 spectra found:", len(ms2_spectra_found))

                precursor_list_ms2 = list()
                for spectrum in ms2_spectra_found:
                    for mz in spectrum.get_precursor_mz():
                        precursor_list_ms2.append(mz)

                print("Precursor list:", precursor_list_ms2)
                precursor_ms2 = statistics.mode(precursor_list_ms2)
                print("Precursor found:", precursor_ms2)

                spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1], ms_level_1 = True)
                print("Number of MS1 spectra found:", len(spectra_found))
                print("sizes:")
                for spectrum in spectra_found:
                    print(spectrum.get_size())
    
                average_spectrum = cp.average_spectra_ordered(spectra_found, 0.03)

                # We sort the spectrum by mz

                coelution = is_coelution(average_spectrum, precursor_ms2)
                
                coelution_list.append(coelution)
                quality_list.append(quality)
                experiment_list.append(name)
                
            line_count += 1
            
        for i in range(0, len(coelution_list)):
            print("Experiment name:", experiment_list[i])
            print("Quality:", quality_list[i])
            print("Coelution:", coelution_list[i])
            print()



def main():
    "Test is_coelution"
    # "Ordered_average_test"
    
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")
    # retention_time = ip.rt_window_to_delta("7.632_7.846")
    # print(retention_time[0], retention_time[1])

    # spectra_found = cp.find_spectra_by_mz_and_rt("MSMS_AFX3.mzML", 782.5682, retention_time[0], 0.03, retention_time[1])
    # num_spectrum = len(spectra_found)
    # print("Number found spectrum:", num_spectrum)

    # print("Start_av")
    # average_spectrum = cp.average_spectra(spectra_found, 0.01)
    # average_spectrum.sort_by_mz()
    # print("Start_or")
    # ordered_average_spectrum = cp.average_spectra_ordered(spectra_found, 0.01)

    # print(len(average_spectrum.get_peaks()))
    # print(len(ordered_average_spectrum.get_peaks()))

    # # "Negative test"
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")
    # retention_time = ip.rt_window_to_delta("7.632_7.846")
    # print(retention_time[0], retention_time[1])

    # spectra_found = cp.find_spectra_by_mz_and_rt("MSMS_AFX3.mzML", 782.5682, retention_time[0], 0.03, retention_time[1])
    # num_spectrum = len(spectra_found)
    # print("Number found spectrum:", num_spectrum)

    # average_spectrum = cp.average_spectra(spectra_found, 0.03)
    # coelution = is_coelution(average_spectrum)
    # if coelution == False:
    #     print("Negative Test passed\n")
    # else:
    #     raise Exception("Negative test not passed")

    # "Positive test"
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")
    # retention_time = ip.rt_window_to_delta("4.592_4.635")
    # print(retention_time[0], retention_time[1])

    # spectra_found = cp.find_spectra_by_mz_and_rt("MSMS_AFX13.mzML", 954.4915, retention_time[0], 0.03, retention_time[1])
    # num_spectrum = len(spectra_found)
    # print("Number found spectrum:", num_spectrum)

    # average_spectrum = cp.average_spectra(spectra_found, 0.03)
    # coelution = is_coelution(average_spectrum)
    # if coelution == True:
    #     print("Positive Test passed\n")
    # else:
    #     raise Exception("Positive test not passed")
    
    # "Analyze all"
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    # open_template("plantilla.csv", path_in)

    # #########################################################################################################
    # # Try find_reference_massses with negative data
    # user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"
    # list_of_values = ip.open_negative_template("plantilla_negativo.csv", path_in)

    # reference_masses_list = []
    # reference_masses_template_list = []
    # quality_list = []
    # experiment_list = []
    # precursor_found_list =[]
    # retention_time_list = []


    # for a in range(len(list_of_values[0])):

    #     name = list_of_values[0][a]
    #     name_file = name + ".mzML"
    #     mz_precursor = float(list_of_values[4][a])
    #     retention_time = list_of_values[1][a]
    #     delta_mz = 0.01
    #     reference_masses_template = list_of_values[8][a]
    #     quality = list_of_values[3][a]

    #     ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])

    #     precursor_list_ms2 = list()
    #     for spectrum in ms2_spectra_found:
    #         for mz in spectrum.get_precursor_mz():
    #             precursor_list_ms2.append(mz)

    #     precursor_ms2 = statistics.mode(precursor_list_ms2)

    #     average_spectrum = cp.average_spectra_ordered(ms2_spectra_found, delta_mz)

    #     grass_intensity_be = gf.be_measure_grass_level(average_spectrum, increase = 10)
    #     grass_intensity_end = gf.end_measure_grass_level(average_spectrum, increase = 10)
    #     average_grass = (grass_intensity_be + grass_intensity_end) / 2

    #     cut_spectrum = gf.grass_cutter(average_spectrum, average_grass)

    #     reference_masses = find_reference_massses(cut_spectrum, user_reference_masses_list, delta_mz)

    #     reference_masses_template_list.append(reference_masses_template)
    #     reference_masses_list.append(reference_masses)
    #     quality_list.append(quality)
    #     experiment_list.append(name)
    #     retention_time_list.append(retention_time)
    #     precursor_found_list.append(precursor_ms2)
    

    # for i in range(len(list_of_values[0])):

    #     print("################################################################################################")
    #     print("Experiment name:", experiment_list[i])
    #     print("Quality:", quality_list[i])
    #     print("Retention time:", (retention_time_list[i][0] - retention_time_list[i][1])/60, (retention_time_list[i][0] + retention_time_list[i][1])/60)
    #     print("Precursor_mz:", precursor_found_list[i])

    #     print("Reference masses found:")
    #     for reference_mass_peak in reference_masses_list[i]:
    #         print("MZ:", reference_mass_peak.get_mz(), end = ";")
    #         print("I:", reference_mass_peak.get_intensity(), end = ";")
    #     print("")

    #     print("Reference_masses_template:")
    #     for reference_mass in reference_masses_template_list[i]:
    #         print("MZ:", reference_mass, end = ";")    
    #     print("")
    #     print("")

    # precision_list = []
    # recall_list = []
    # for i in range(len(list_of_values[0])):
    
    #     reference_mass_spectrum = csm.Spectrum_object(reference_masses_list[i], experiment_list[i], retention_time_list[i][0], [precursor_found_list[i]])

    #     match_peaks = ip.compare_template_with_found(reference_masses_template_list[i], reference_mass_spectrum, delta_mz = 0.01)

    #     print("Found_peaks:", end = "")
    #     for peak in reference_mass_spectrum.get_peaks():
    #         print(peak.get_mz(), end = ",")
    #     print("")

    #     print("Template_peaks:", end = "")
    #     for peak in reference_masses_template_list[i]:
    #         print(peak, end = ",")
    #     print("")

    #     print("Match_peaks:", end = "")
    #     for peak in match_peaks:
    #         print(peak.get_mz(), end = ",")
    #     print("")

    #     if len(reference_masses_template_list[i]) != 0:
            
    #         if len(reference_mass_spectrum.get_peaks()) == 0:
    #             precision = 0
    #         else:
    #             precision = ip.calculate_precision(match_peaks, reference_mass_spectrum)

    #         recall = ip.calculate_recall(match_peaks, reference_masses_template_list[i])
            
    #         precision_list.append(precision)
    #         recall_list.append(recall)
        
    #     else:
    #         precision = "No template peaks"
    #         recall = "No template peaks"

    #     print("Precision:", precision)
    #     print("Recall", recall)
    #     print("")

    # avg_precision = statistics.mean(precision_list)
    # avg_recall = statistics.mean(recall_list)

    # print("Average_precision:", avg_precision)
    # print("Average_recall:", avg_recall)







    # # Try is_coelution with negative data
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"    
    # list_of_values = ip.open_negative_template("plantilla_negativo.csv", path_in)
    # print("")

    # coelution_list = []
    # quality_list = []
    # experiment_list = []
    # retention_time_list = []
    # precursor_found_list = []

    # for a in range(len(list_of_values[0])):
    #     print("NUMBER SPECTRUM:", a)

    #     name = list_of_values[0][a]
    #     name_file = name + ".mzML"
    #     mz_precursor = float(list_of_values[4][a])
    #     retention_time = list_of_values[1][a]
    #     delta_mz = 0.01

    #     print(name_file)
    #     print(mz_precursor)
    #     print(retention_time)

    #     ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])
    #     print("Number of MS2 spectra found:", len(ms2_spectra_found))

    #     precursor_list_ms2 = list()
    #     for spectrum in ms2_spectra_found:
    #         for mz in spectrum.get_precursor_mz():
    #             precursor_list_ms2.append(mz)

    #     print("Precursor list:", precursor_list_ms2)
    #     precursor_ms2 = statistics.mode(precursor_list_ms2)
    #     print("Precursor found:", precursor_ms2)

    #     spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1], ms_level_1 = True)
    #     print("Number of MS1 spectra found:", len(spectra_found))
    #     print("sizes:")
    #     for spectrum in spectra_found:
    #         print(spectrum.get_size())

    #     average_spectrum = cp.average_spectra_ordered(spectra_found, delta_mz, ms1 = True)

    #     coelution = is_coelution(average_spectrum, precursor_ms2, delta_mz = delta_mz)
        
    #     coelution_list.append(coelution)
    #     quality_list.append(list_of_values[3][a])
    #     experiment_list.append(name)
    #     retention_time_list.append(retention_time)
    #     precursor_found_list.append(precursor_ms2)

    #     print("Next spectrum")
    #     print("")
    
    # for i in range(0, len(coelution_list)):
    #         print("################################################################################################")
    #         print("Experiment name:", experiment_list[i])
    #         print("Quality:", quality_list[i])
    #         print("Retention time:", (retention_time_list[i][0] - retention_time_list[i][1])/60, (retention_time_list[i][0] + retention_time_list[i][1])/60)
    #         print("Precursor_mz:", precursor_found_list[i])
    #         print("Proper_coelution_found:")
    #         for coelution_peak in coelution_list[i][0]:
    #             print("MZ:", coelution_peak.get_mz(), end = ";")
    #         print("\nAcceptable_coelution_found:")
    #         for coelution_peak in coelution_list[i][1]:
    #             print("MZ:", coelution_peak.get_mz(), end = ";")
    #         print("")
    #         print("Coelution_template:")
    #         for coelution_peak in list_of_values[7][i]:
    #             print("MZ:", coelution_peak, end = ";")    
    #         print("")
    #         print("")

    # #########################################################################################################
    # # Try get_most_intense_peak
    # user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"
    # list_of_values = ip.open_negative_template("plantilla_negativo.csv", path_in)

    # name = list_of_values[0][4]
    # name_file = name + ".mzML"
    # mz_precursor = float(list_of_values[4][4])
    # retention_time = list_of_values[1][4]
    # delta_mz = 0.01
    # reference_masses_template = list_of_values[8][4]
    # quality = list_of_values[3][4]

    # ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])
    # scan_to_use = ms2_spectra_found[0]

    # greater_peak, reference_masses =  scan_to_use.get_most_intense_peak(user_reference_masses_list)

    # print("Name:", name)
    # print("Scan retention time", scan_to_use.get_retention_time()/60)

    # print("Greater_peak: MZ:", greater_peak.get_mz(), "I:", greater_peak.get_intensity())

    # print("Reference_masses_found:", end = "")
    # for reference_mass in reference_masses:
    #     print ("MZ:", reference_mass.get_mz(), "I:", reference_mass.get_intensity(), end = "")
    # print("")




    
    
    
    # #########################################################################################################
    # # Try get_most_intense_peak with all negative data
    # user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"
    # list_of_values = ip.open_negative_template("plantilla_negativo.csv", path_in)

    # reference_masses_list = []
    # reference_masses_template_list = []
    # quality_list = []
    # experiment_list = []
    # precursor_found_list =[]
    # retention_time_list = []


    # for a in range(len(list_of_values[0])):

    #     name = list_of_values[0][a]
    #     name_file = name + ".mzML"
    #     mz_precursor = float(list_of_values[4][a])
    #     retention_time = list_of_values[1][a]
    #     delta_mz = 0.01
    #     reference_masses_template = list_of_values[8][a]
    #     quality = list_of_values[3][a]

    #     ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])

    #     precursor_list_ms2 = list()
    #     for spectrum in ms2_spectra_found:
    #         for mz in spectrum.get_precursor_mz():
    #             precursor_list_ms2.append(mz)

    #     precursor_ms2 = statistics.mode(precursor_list_ms2)

    #     average_spectrum = cp.average_spectra_ordered(ms2_spectra_found, delta_mz)

    #     be_grass_level = gf.be_measure_grass_level(average_spectrum, increase = 10)
    #     end_grass_level = gf.end_measure_grass_level(average_spectrum, increase = 10)
    #     grass_level = (be_grass_level + end_grass_level) / 2

    #     most_intense_peak, reference_masses_found = average_spectrum.get_most_intense_peak(user_reference_masses_list)

    #     reference_masses = filter_masses_by_intensity(most_intense_peak, reference_masses_found, grass_level)        

    #     reference_masses_template_list.append(reference_masses_template)
    #     reference_masses_list.append(reference_masses[2])
    #     quality_list.append(quality)
    #     experiment_list.append(name)
    #     retention_time_list.append(retention_time)
    #     precursor_found_list.append(precursor_ms2)
    

    # for i in range(len(list_of_values[0])):

    #     print("################################################################################################")
    #     print("Experiment name:", experiment_list[i])
    #     print("Quality:", quality_list[i])
    #     print("Retention time:", (retention_time_list[i][0] - retention_time_list[i][1])/60, (retention_time_list[i][0] + retention_time_list[i][1])/60)
    #     print("Precursor_mz:", precursor_found_list[i])

    #     print("Reference masses found:")
    #     for reference_mass_peak in reference_masses_list[i]:
    #         print("MZ:", reference_mass_peak.get_mz(), end = ";")
    #         print("I:", reference_mass_peak.get_intensity(), end = ";")
    #     print("")

    #     print("Reference_masses_template:")
    #     for reference_mass in reference_masses_template_list[i]:
    #         print("MZ:", reference_mass, end = ";")    
    #     print("")
    #     print("")

    # precision_list = []
    # recall_list = []
    # for i in range(len(list_of_values[0])):
    
    #     reference_mass_spectrum = csm.Spectrum_object(reference_masses_list[i], experiment_list[i], retention_time_list[i][0], [precursor_found_list[i]])

    #     match_peaks = ip.compare_template_with_found(reference_masses_template_list[i], reference_mass_spectrum, delta_mz = 0.01)

    #     print("Found_peaks:", end = "")
    #     for peak in reference_mass_spectrum.get_peaks():
    #         print(peak.get_mz(), end = ",")
    #     print("")

    #     print("Template_peaks:", end = "")
    #     for peak in reference_masses_template_list[i]:
    #         print(peak, end = ",")
    #     print("")

    #     print("Match_peaks:", end = "")
    #     for peak in match_peaks:
    #         print(peak.get_mz(), end = ",")
    #     print("")

    #     if len(reference_masses_template_list[i]) != 0:
            
    #         if len(reference_mass_spectrum.get_peaks()) == 0:
    #             precision = 0
    #         else:
    #             precision = ip.calculate_precision(match_peaks, reference_mass_spectrum)

    #         recall = ip.calculate_recall(match_peaks, reference_masses_template_list[i])
            
    #         precision_list.append(precision)
    #         recall_list.append(recall)
        
    #     else:
    #         precision = "No template peaks"
    #         recall = "No template peaks"

    #     print("Precision:", precision)
    #     print("Recall", recall)
    #     print("")

    # avg_precision = statistics.mean(precision_list)
    # avg_recall = statistics.mean(recall_list)

    # print("Average_precision:", avg_precision)
    # print("Average_recall:", avg_recall)








    # #########################################################################################################
    # # Try find_crosstalk_peaks
    # user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"
    # list_of_values = ip.open_negative_template("plantilla_negativo.csv", path_in)

    # name = list_of_values[0][4]
    # name_file = name + ".mzML"
    # mz_precursor = float(list_of_values[4][4])
    # retention_time = list_of_values[1][4]
    # delta_mz = 0.01
    # reference_masses_template = list_of_values[8][4]
    # quality = list_of_values[3][4]

    # ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])
    # scan_to_use = ms2_spectra_found[0]

    # be_grass_level = gf.be_measure_grass_level(scan_to_use, increase = 10)
    # end_grass_level = gf.end_measure_grass_level(scan_to_use, increase = 10)
    # grass_level = (be_grass_level + end_grass_level) / 2

    # greater_peak, reference_masses =  scan_to_use.get_most_intense_peak(user_reference_masses_list)
    # crosstalk_peaks_found =  find_crosstalk_peaks(scan_to_use)

    # crosstalk_peaks = filter_masses_by_intensity(greater_peak, crosstalk_peaks_found, grass_level, weak_percentage = 40)

    # print("Name:", name)
    # print("Scan retention time:", scan_to_use.get_retention_time()/60)
    # print("Grass level:", grass_level)

    # print("Weak_crosstalk_peaks_found:", end = "")
    # for peak in crosstalk_peaks[1]:
    #     print ("MZ:", peak.get_mz(), "I:", peak.get_intensity(), end = ", ")
    # print("")

    # print("Strong_crosstalk_peaks_found:", end = "")
    # for peak in crosstalk_peaks[2]:
    #     print ("MZ:", peak.get_mz(), "I:", peak.get_intensity(), end = ", ")
    # print("")

    
        







    

if __name__ == "__main__":
    main()