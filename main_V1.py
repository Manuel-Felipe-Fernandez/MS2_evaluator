# main V1
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
import matplotlib.pyplot as plt

def evaluate_spectrum(spectrum_ms2_in, spectrum_ms1_in, user_reference_masses_list, delta_mz = 0.01, delta_coelution = 1.3,
                    strong_percentage_coelution = 10, strong_percentage_crosstalk = 10, weak_percentage_coelution = 40,
                    weak_percentage_reference_masses = 40, weak_percentage_crosstalk = 40):


    ## Grass level in MS2
    be_grass_level = gf.be_measure_grass_level(spectrum_ms2_in, increase = 10)
    end_grass_level = gf.end_measure_grass_level_stdev(spectrum_ms2_in, increase = 10)
    grass_level = (be_grass_level + end_grass_level)/2


    ## Find coelution
    coelution_peaks = ff.is_coelution(spectrum_ms1_in, spectrum_ms2_in.get_precursor_mz()[0], delta_coelution,
                                        percentage_intensity_not_coelution = strong_percentage_coelution,
                                        percentage_accetable_coelution= weak_percentage_coelution)


    ## Find maximum intensity peak and reference masses
    max_peak, refence_masses_found = spectrum_ms2_in.get_most_intense_peak(user_reference_masses_list, delta_mz)
    reference_masses = ff.filter_masses_by_intensity(max_peak, refence_masses_found, max_peak.get_intensity()*0.1, weak_percentage_reference_masses)


    ## Find crosstalk
    crosstalk_found = ff.find_crosstalk_peaks(spectrum_ms2_in)
    crosstalk = ff.filter_masses_by_intensity(max_peak, crosstalk_found, max_peak.get_intensity()*0.1, weak_percentage_crosstalk)


    ## Calculate S/N
    maximum_intensity = max_peak.get_intensity()
    signal_noise_ratio = maximum_intensity / grass_level

    values_out = [coelution_peaks, reference_masses, crosstalk, signal_noise_ratio, max_peak, grass_level]

    return(values_out)

    


def determine_quality_logical_V1(spectrum_evaluation, lower_signal_noise_ratio = 6, medium_signal_noise_ratio = 50):
    strong_coelution_peaks, weak_coelution_peaks, precursor_peak = spectrum_evaluation[0]
    not_reference_masses, weak_reference_masses, strong_reference_masses = spectrum_evaluation[1]
    not_crosstalk, weak_crosstalk, strong_crosstalk = spectrum_evaluation[2]
    signal_noise_ratio = spectrum_evaluation[3]
    max_peak = spectrum_evaluation[4]
    grass_level = spectrum_evaluation[5]

    number_strong_coelution = len(strong_coelution_peaks)
    number_weak_coelution = len(weak_coelution_peaks)

    number_strong_reference_masses = len(strong_reference_masses)
    number_weak_reference_masses = len(weak_reference_masses)

    number_weak_crosstalk = len(weak_crosstalk)
    number_strong_crosstalk = len(strong_crosstalk)


    if number_strong_coelution > 1:
        
        # basura
        quality_out = 1

    elif number_strong_coelution > 0:

        # malo o basura

        if number_weak_coelution > 0 or number_strong_crosstalk > 0 or number_weak_crosstalk > 0 or number_strong_reference_masses > 0 or number_weak_reference_masses > 0 or signal_noise_ratio < lower_signal_noise_ratio:

            # basura
            quality_out = 1

        else:

            # malo
            quality_out = 2
    
    # Weak coelution 
    elif number_weak_coelution > 0:
        
        if number_strong_crosstalk > 1 or number_strong_reference_masses > 1:

            # basura
            quality_out = 1

        elif number_weak_coelution > 1 or number_weak_reference_masses > 0 or number_weak_crosstalk > 0 or signal_noise_ratio < lower_signal_noise_ratio:

            # malo
            quality_out = 2
        
        else:

            # regular
            quality_out = 3

    # No coelution
    else:

        if number_strong_reference_masses + number_weak_reference_masses + number_weak_crosstalk + number_strong_crosstalk > 0 or signal_noise_ratio < lower_signal_noise_ratio:
            
            # regular
            quality_out = 3

        elif signal_noise_ratio < medium_signal_noise_ratio:
            
            # bueno
            quality_out = 4
        
        else:

            # muy
            quality_out = 5
    
    return(quality_out)


############################# Score functions ########################################

def score_generation(coelution_peak, max_peak, lower_threshold_percentage = 10, medium_threshold_percentage = 40, upper_threshold_percentage = 50, medium_gradient = -1/100):
    
    # Preparing functions
    
    # Medium function
    n_medium = 1 - lower_threshold_percentage * medium_gradient

    # Upper function
    medium_threshold_score = medium_gradient * medium_threshold_percentage + n_medium

    upper_gradient = (0 - medium_threshold_score)/(upper_threshold_percentage - medium_threshold_percentage)

    n_upper = - upper_threshold_percentage * upper_gradient

    # Score generation
    coelution_intensity_percentage = (coelution_peak.get_intensity() / max_peak.get_intensity()) * 100

    if coelution_intensity_percentage < 10:
        
        score = 1
    
    elif coelution_intensity_percentage < medium_threshold_percentage:

        score = coelution_intensity_percentage * medium_gradient + n_medium

    elif coelution_intensity_percentage < upper_threshold_percentage:

        score = coelution_intensity_percentage * upper_gradient + n_upper
    
    else:

        score = 0

    return(score)


def score_list_of_peaks(list_of_peaks, max_peak, lower_threshold_percentage = 10, medium_threshold_percentage = 40, upper_threshold_percentage = 50, medium_gradient = -1/100):
    
    list_of_scores = []

    for peak in list_of_peaks:

        score = score_generation(peak, max_peak, lower_threshold_percentage = 10,
                                medium_threshold_percentage = 40, upper_threshold_percentage = 50,
                                medium_gradient = -1/100 )

        list_of_scores.append(score)

    return(list_of_scores)    


def score_signal_noise_ratio(signal_noise_ratio, threshold = 50, gradient = 1/100):
    
    if signal_noise_ratio >= threshold:
        
        score = 1

    else:

        n = 1 - (threshold * gradient)

        score = signal_noise_ratio * gradient + n

    return(score)




def score_evaluation(spectrum_evaluation, quality_evaluation, medium_gradient = -1/100,
                    lower_percentage_coelution = 10, medium_percentage_coelution = 40, upper_percentage_coelution = 50,
                    lower_percentage_crosstalk = 10, medium_percentage_crosstalk = 40, upper_percentage_crosstalk = 50,
                    lower_percentage_reference_masses = 10, medium_percentage_reference_masses = 40, upper_percentage_reference_masses = 50,
                    weight_coelution = 0.8, weight_reference_masses = 0.7):

    final_score = quality_evaluation - 1

    # Unpack evaluation
    strong_coelution_peaks, weak_coelution_peaks, precursor_peak = spectrum_evaluation[0]
    not_reference_masses, weak_reference_masses, strong_reference_masses = spectrum_evaluation[1]
    not_crosstalk, weak_crosstalk, strong_crosstalk = spectrum_evaluation[2]
    signal_noise_ratio = spectrum_evaluation[3]
    max_peak = spectrum_evaluation[4]
    grass_level = spectrum_evaluation[5]

    # Find score for each coelution
    score_strong_coelution_peaks = score_list_of_peaks(strong_coelution_peaks, precursor_peak, lower_percentage_coelution, medium_percentage_coelution, upper_percentage_coelution, medium_gradient)
    score_weak_coelution_peaks = score_list_of_peaks(weak_coelution_peaks, precursor_peak, lower_percentage_coelution, medium_percentage_coelution, upper_percentage_coelution, medium_gradient)

    # Find score for each reference mass
    score_strong_reference_masses = score_list_of_peaks(strong_reference_masses, max_peak, lower_percentage_reference_masses, medium_percentage_reference_masses, upper_percentage_reference_masses, medium_gradient)
    score_weak_reference_masses = score_list_of_peaks(weak_reference_masses, max_peak, lower_percentage_reference_masses, medium_percentage_reference_masses, upper_percentage_reference_masses, medium_gradient)

    # Find score for each cross talk
    score_strong_crosstalk = score_list_of_peaks(strong_crosstalk, max_peak, lower_percentage_crosstalk, medium_percentage_crosstalk, upper_percentage_crosstalk, medium_gradient)
    score_weak_crosstalk = score_list_of_peaks(weak_crosstalk, max_peak, lower_percentage_crosstalk, medium_percentage_crosstalk, upper_percentage_crosstalk, medium_gradient)

    print("Score_strong_coelutions:", score_strong_coelution_peaks)
    print("Score_weak_coelutions:", score_weak_coelution_peaks)

    print("Score_strong_reference_masses:", score_strong_reference_masses)
    print("score_weak_reference_masses:", score_weak_reference_masses)

    print("score_strong_crosstalk:", score_strong_crosstalk)
    print("score_weak_crosstalk:", score_weak_crosstalk)

    # Calculate weights
    number_strong_coelutions = len(strong_coelution_peaks)
    number_strong_crosstalk = len(strong_crosstalk)
    number_strong_reference_masses = len(strong_reference_masses)   
    
    
    # Weight scores
    crosstalk_coelution_scores = score_strong_coelution_peaks + score_strong_crosstalk + score_weak_coelution_peaks + score_weak_crosstalk

    if len(crosstalk_coelution_scores) > 0:

        minimum_crosstalk_coelution_scores = min(crosstalk_coelution_scores)
        weighted_coelution_score = weight_coelution * minimum_crosstalk_coelution_scores

    else:

        weighted_coelution_score = weight_coelution * 1


    reference_masses_scores = score_strong_reference_masses + score_weak_reference_masses

    if len(reference_masses_scores) > 0:

        minimum_reference_masses_score = min(reference_masses_scores)
        weighted_reference_masses_score = weight_reference_masses * minimum_reference_masses_score

    else:

        weighted_reference_masses_score = weight_reference_masses * 1

    
    
    # Calculate final score

    signal_noise_ratio_score = score_signal_noise_ratio(signal_noise_ratio)

    final_score_coelution = weighted_coelution_score + signal_noise_ratio_score * (1 - weight_coelution)

    final_score_reference_mass = weighted_reference_masses_score + signal_noise_ratio_score * (1 - weight_reference_masses)

    final_score += min(final_score_coelution, final_score_reference_mass)
    final_score = final_score/5
    
    print("")

    try:
        print("minimum_crosstalk_coelution_scores", minimum_crosstalk_coelution_scores)
    except:
        pass

    try:
        print("minimum_reference_masses_score", minimum_reference_masses_score)
    except:
        pass

    print("weighted_coelution_score", weighted_coelution_score)    
    print("weighted_reference_masses_score", weighted_reference_masses_score)

    print("")

    print("signal_noise_ratio_score", signal_noise_ratio_score)

    print("final_score_coelution", final_score_coelution)
    print("final_score_reference_mass", final_score_reference_mass)
    print("final_score", final_score)

    print("")

    return(final_score)




    


def score_evaluation2(spectrum_evaluation, medium_gradient = -1/100,
                    lower_percentage_coelution = 10, medium_percentage_coelution = 40, upper_percentage_coelution = 50,
                    lower_percentage_crosstalk = 10, medium_percentage_crosstalk = 40, upper_percentage_crosstalk = 50,
                    lower_percentage_reference_masses = 10, medium_percentage_reference_masses = 40, upper_percentage_reference_masses = 50):


    # Unpack evaluation
    strong_coelution_peaks, weak_coelution_peaks, precursor_peak = spectrum_evaluation[0]
    not_reference_masses, weak_reference_masses, strong_reference_masses = spectrum_evaluation[1]
    not_crosstalk, weak_crosstalk, strong_crosstalk = spectrum_evaluation[2]
    signal_noise_ratio = spectrum_evaluation[3]
    max_peak = spectrum_evaluation[4]
    grass_level = spectrum_evaluation[5]

    # Find score for each coelution
    score_strong_coelution_peaks = score_list_of_peaks(strong_coelution_peaks, precursor_peak, lower_percentage_coelution, medium_percentage_coelution, upper_percentage_coelution, medium_gradient)
    score_weak_coelution_peaks = score_list_of_peaks(weak_coelution_peaks, precursor_peak, lower_percentage_coelution, medium_percentage_coelution, upper_percentage_coelution, medium_gradient)

    # Find score for each reference mass
    score_strong_reference_masses = score_list_of_peaks(strong_reference_masses, max_peak, lower_percentage_reference_masses, medium_percentage_reference_masses, upper_percentage_reference_masses, medium_gradient)
    score_weak_reference_masses = score_list_of_peaks(weak_reference_masses, max_peak, lower_percentage_reference_masses, medium_percentage_reference_masses, upper_percentage_reference_masses, medium_gradient)

    # Find score for each cross talk
    score_strong_crosstalk = score_list_of_peaks(strong_crosstalk, max_peak, lower_percentage_crosstalk, medium_percentage_crosstalk, upper_percentage_crosstalk, medium_gradient)
    score_weak_crosstalk = score_list_of_peaks(weak_crosstalk, max_peak, lower_percentage_crosstalk, medium_percentage_crosstalk, upper_percentage_crosstalk, medium_gradient)

    print("Score_strong_coelutions:", score_strong_coelution_peaks)
    print("Score_weak_coelutions:", score_weak_coelution_peaks)

    print("Score_strong_reference_masses:", score_strong_reference_masses)
    print("score_weak_reference_masses:", score_weak_reference_masses)

    print("score_strong_crosstalk:", score_strong_crosstalk)
    print("score_weak_crosstalk:", score_weak_crosstalk)

    # Calculate weights
    number_strong_coelutions = len(strong_coelution_peaks)
    number_strong_crosstalk = len(strong_crosstalk)
    number_strong_reference_masses = len(strong_reference_masses)

    weight_coelution = 0.8

    if (number_strong_coelutions + number_strong_crosstalk) > 1:
        weight_coelution += 0.1   

    weight_reference_masses = 0.7
    
    
    # Weight scores
    crosstalk_coelution_scores = score_strong_coelution_peaks + score_strong_crosstalk + score_weak_coelution_peaks + score_weak_crosstalk

    if len(crosstalk_coelution_scores) > 0:

        minimum_crosstalk_coelution_scores = min(crosstalk_coelution_scores)
        weighted_coelution_score = weight_coelution * minimum_crosstalk_coelution_scores

    else:

        weighted_coelution_score = weight_coelution * 1


    reference_masses_scores = score_strong_reference_masses + score_weak_reference_masses

    if len(reference_masses_scores) > 0:

        minimum_reference_masses_score = min(reference_masses_scores)
        weighted_reference_masses_score = weight_reference_masses * minimum_reference_masses_score

    else:

        weighted_reference_masses_score = weight_reference_masses * 1

    
    
    # Calculate final score

    signal_noise_ratio_score = score_signal_noise_ratio(signal_noise_ratio)

    final_score_coelution = weighted_coelution_score + signal_noise_ratio_score * (1 - weight_coelution)

    final_score_reference_mass = weighted_reference_masses_score + signal_noise_ratio_score * (1 - weight_reference_masses)

    final_score = min(final_score_coelution, final_score_reference_mass)
    
    print("")

    try:
        print("minimum_crosstalk_coelution_scores", minimum_crosstalk_coelution_scores)
    except:
        pass

    try:
        print("minimum_reference_masses_score", minimum_reference_masses_score)
    except:
        pass

    print("weighted_coelution_score", weighted_coelution_score)    
    print("weighted_reference_masses_score", weighted_reference_masses_score)

    print("")

    print("signal_noise_ratio_score", signal_noise_ratio_score)

    print("final_score_coelution", final_score_coelution)
    print("final_score_reference_mass", final_score_reference_mass)
    print("final_score", final_score)

    print("")

    return(final_score)




    




            





        

    



def main():

    # Test score evaluation function
    path_in = "C:\\Users\\Manuel Fern??ndez\\Desktop\\PAE\\Datos_anotados"
    list_of_values = ip.open_negative_template("pos_neg_template.csv", path_in, ";")
    user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    number_of_windows = len(list_of_values[0])

    
    evaluation_list = []
    quality_list = []
    score_evalutation_list = []
    name_list = []
    template_quality_list = []


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

        # Evaluate the spectrum
        evaluation_out = evaluate_spectrum(average_ms2, average_ms1, user_reference_masses_list)

        # Determine quality
        quality_out = determine_quality_logical_V1(evaluation_out)

        # Get score from evaluation
        score_evalutation_out = score_evaluation(evaluation_out, quality_out)
        print("score_evalutation_out", score_evalutation_out)
        print("")


        strong_coelution_peaks, weak_coelution_peaks, precursor_peak = evaluation_out[0]
        not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation_out[1]
        not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation_out[2]
        signal_noise_ratio = evaluation_out[3]
        max_peak = evaluation_out[4]
        grass_level = evaluation_out[5]

        evaluation_list.append(evaluation_out)
        quality_list.append(quality_out)
        score_evalutation_list.append(score_evalutation_out)
        name_list.append(name)
        template_quality_list.append(quality)

        print("NAME:", name)
        print("Retention time:", retention_time[0])

        print("Template quality:", quality)
        print("Assessed quality:", quality_out)

        print("Assessed score:", quality_out)

        print("Template coelution:", end="")
        for mz in coelution_template:
            print("MZ:", mz, end=",")
        print("")

        print("Strong coelution:", end="")
        for peak in strong_coelution_peaks:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Weak coelution:", end="")
        for peak in weak_coelution_peaks:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("")


        # Reference masses
        print("Weak reference masses", end = "")
        for peak in weak_reference_masses:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        for peak in weak_reference_masses:
            print("I:", peak.get_intensity(), end = ",")
        print("")

        print("Strong reference masses", end = "")
        for peak in strong_reference_masses:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Reference massses template:", end = "")
        for mz in reference_masses_template:
            print("MZ:", mz, end=",")
        print("")


        print("")


        # Crosstalk
        print("Weak cross talk peaks found:", len(weak_crosstalk))
        print("Strong cross talk peaks found:", len(strong_crosstalk))


        print("")


        # Signal to noise ratio
        print("Signal to noise ratio:", signal_noise_ratio)
        print("Max peak:", "MZ:", max_peak.get_mz(), "I:", max_peak.get_intensity())

        

        print("")
        print("Spectrum", window, "done")
        print("______________________________")



    path_in = "C:\\Users\\Manuel Fern??ndez\\Desktop\\PAE\\Datos_anotados\\main_results"
    os.chdir(path_in)
    
    with open("ordered.txt", "w") as f:
        f.write("Name;Template_quality;Assessed_quality;Score;S/N;Strong_Coelution;Weak_Coelution;Strong_Reference_masses;Weak_Reference_masses;Strong_Crosstalk;Weak_Crosstalk\n")

        for spectrum_index in range(len(evaluation_list)):

            evaluation = evaluation_list[spectrum_index]

            name = name_list[spectrum_index]
            template_quality = template_quality_list[spectrum_index]

            quality = quality_list[spectrum_index]
            strong_coelution_peaks, weak_coelution_peaks, precursor_peak = evaluation[0]
            not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation[1]
            not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation[2]
            signal_noise_ratio = evaluation[3]
            max_peak = evaluation[4]
            grass_level = evaluation[5]

            score = score_evalutation_list[spectrum_index]

            f.write(name + ";")

            f.write(template_quality + ";")

            f.write(str(quality) + ";")

            f.write(str(score) + ";")

            f.write(str(signal_noise_ratio) + ";")

            f.write(str(len(strong_coelution_peaks)) + ";")
            f.write(str(len(weak_coelution_peaks)) + ";")

            f.write(str(len(strong_reference_masses)) + ";")
            f.write(str(len(weak_reference_masses)) + ";")

            f.write(str(len(strong_crosstalk)) + ";")
            f.write(str(len(weak_crosstalk)) + ";\n")


    # Test score generating function
    """
    path_in = "C:\\Users\\Manuel Fern??ndez\\Desktop\\PAE\\Datos_anotados\\main_results"
    os.chdir(path_in)
    
    with open("Score_function.txt", "w") as f:

        max_peak_test = csm.Peak_object(421, 100)

        score_list = []
        score_index = []
        score_signal_noise_ratio_list = []

        for intensity in range(1, 101):

            coelution_peak_test = csm.Peak_object(68, intensity)

            score = score_generation(coelution_peak_test, max_peak_test)
            signal_noise_ratio_score = score_signal_noise_ratio(intensity)

            f.write(str(score) + ";")
            f.write(str(intensity) + ";")
            f.write(str(signal_noise_ratio_score) + ";\n")


            score_list.append(score)
            score_index.append(intensity)
            score_signal_noise_ratio_list.append(signal_noise_ratio_score)
    """

    
    
    
    # Test evaluation and assessment
    """
    path_in = "C:\\Users\\Manuel Fern??ndez\\Desktop\\PAE\\Datos_anotados"
    list_of_values = ip.open_negative_template("pos_neg_template.csv", path_in, ";")
    user_reference_masses_list =  [92.9283, 94.9253, 102.9569, 104.9543, 112.9854, 146.9835, 148.982, 150.8866, 224.9792, 266.8034, 116.9267]
    number_of_windows = len(list_of_values[0])

    
    evaluation_list = []
    quality_list = []
    name_list = []
    template_quality_list = []


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

        # Evaluate the spectrum
        evaluation_out = evaluate_spectrum(average_ms2, average_ms1, user_reference_masses_list)

        # Determine quality
        quality_out = determine_quality_logical_V1(evaluation_out)


        strong_coelution_peaks, weak_coelution_peaks = evaluation_out[0]
        not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation_out[1]
        not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation_out[2]
        signal_noise_ratio = evaluation_out[3]
        max_peak = evaluation_out[4]
        grass_level = evaluation_out[5]

        evaluation_list.append(evaluation_out)
        quality_list.append(quality_out)
        name_list.append(name)
        template_quality_list.append(quality)

        print("NAME:", name)
        print("Retention time:", retention_time[0])

        print("Template quality:", quality)
        print("Assessed quality:", quality_out)

        print("Template coelution:", end="")
        for mz in coelution_template:
            print("MZ:", mz, end=",")
        print("")

        print("Strong coelution:", end="")
        for peak in strong_coelution_peaks:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Weak coelution:", end="")
        for peak in weak_coelution_peaks:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("")


        # Reference masses
        print("Weak reference masses", end = "")
        for peak in weak_reference_masses:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Strong reference masses", end = "")
        for peak in strong_reference_masses:
            print("MZ:", peak.get_mz(), end = ",")
        print("")

        print("Reference massses template:", end = "")
        for mz in reference_masses_template:
            print("MZ:", mz, end=",")
        print("")


        print("")


        # Crosstalk
        print("Weak cross talk peaks found:", len(weak_crosstalk))
        print("Strong cross talk peaks found:", len(strong_crosstalk))


        print("")


        # Signal to noise ratio
        print("Signal to noise ratio:", signal_noise_ratio)
        print("Max peak:", "MZ:", max_peak.get_mz(), "I:", max_peak.get_intensity())

        

        print("")
        print("Spectrum", window, "done")
        print("______________________________")



    path_in = "C:\\Users\\Manuel Fern??ndez\\Desktop\\PAE\\Datos_anotados\\main_results"
    os.chdir(path_in)
    
    with open("Main_V1.txt", "w") as f:
        f.write("Name;Template_quality;Assessed_quality;S/N;Strong_Coelution;Weak_Coelution;Strong_Reference_masses;Weak_Reference_masses;Strong_Crosstalk;Weak_Crosstalk\n")

        for spectrum_index in range(len(evaluation_list)):

            evaluation = evaluation_list[spectrum_index]

            name = name_list[spectrum_index]
            template_quality = template_quality_list[spectrum_index]

            quality = quality_list[spectrum_index]
            strong_coelution_peaks, weak_coelution_peaks = evaluation[0]
            not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation[1]
            not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation[2]
            signal_noise_ratio = evaluation[3]
            max_peak = evaluation[4]
            grass_level = evaluation[5]

            f.write(name + ";")

            f.write(template_quality + ";")

            f.write(str(quality) + ";")

            f.write(str(signal_noise_ratio) + ";")

            f.write(str(len(strong_coelution_peaks)) + ";")
            f.write(str(len(weak_coelution_peaks)) + ";")

            f.write(str(len(strong_reference_masses)) + ";")
            f.write(str(len(weak_reference_masses)) + ";")

            f.write(str(len(strong_crosstalk)) + ";")
            f.write(str(len(weak_crosstalk)) + ";\n")
    """




        

        






if __name__ == "__main__":
    main()