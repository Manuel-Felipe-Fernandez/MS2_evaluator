# main_17_06
import Evaluation_functions as ev
import Class_parser as cp
import sys
import os

def arguments_input():
    """
    Input arguments for main
    """
    path_in = sys.argv[1]

    if not isinstance(path_in, str):
        raise TypeError("Argument 1 is not a string")

    try:
        os.chdir(path_in)
    except FileNotFoundError:
        raise FileNotFoundError("The specified directory in argument 1 does not exist, please insert a valid directory")



    try:
        rt_mz_name_file = sys.argv[2]
    except IndexError:
        rt_mz_name_file = False

    if rt_mz_name_file == False:

        rt_mz_name_file = "input.txt"

        if not os.path.isfile(rt_mz_name_file):

            raise FileNotFoundError("The default file input.txt does not exist, please insert a valid file")

    elif not isinstance(rt_mz_name_file, str):

        raise TypeError("Argument 2 is not a string")

    else:

        if not os.path.isfile(rt_mz_name_file):
            
            raise FileNotFoundError("The specified file in argument 2 does not exist, please insert a valid file")



    try:
        user_reference_masses_file_name = sys.argv[3]
    except IndexError:
        user_reference_masses_file_name = False
    
    if user_reference_masses_file_name == False:

        user_reference_masses_file_name = "reference_mass_list.txt"

        if not os.path.isfile(user_reference_masses_file_name):
            
            raise FileNotFoundError("The default file reference_mass_list.txt does not exist, please insert a valid file")

    elif not isinstance(user_reference_masses_file_name, str):

        raise TypeError("Argument 3 is not a string")

    else:

        if not os.path.isfile(user_reference_masses_file_name):

            raise FileNotFoundError("The specified file in argument 3 does not exist, please insert a valid file")



    try:
        output_file_name = sys.argv[4]
    except IndexError:
        output_file_name = False
    

    if output_file_name == False:

        output_file_name = "output.txt"

        if not os.path.isfile(output_file_name):

            raise FileNotFoundError("The default file output.txt does not exist, please insert a valid file")

    elif not isinstance(output_file_name, str):

        raise TypeError("Argument 4 is not a string")

    else:

        if not os.path.isfile(output_file_name):
            
            raise FileNotFoundError("The specified file in argument 4 does not exist, please insert a valid file")
    


    try:
        delta_mz = sys.argv[5]
    except IndexError:
        delta_mz = False

    if delta_mz == False:

        delta_mz = 0.01

    else:

        try:
            delta_mz = float(delta_mz)
        
        except:

            raise TypeError("The specified delta mz in argument 5 is not a number")
        
        if delta_mz <= 0:

            raise TypeError("The specified delta mz in argument 5 is equal or smaller than 0. Delta mz should be a positive number")

    
    out_list = [path_in, rt_mz_name_file, user_reference_masses_file_name, output_file_name, delta_mz]
    return(out_list)


def main():
    
    input_arguments_list = arguments_input()

    # Test score evaluation function

    # User defined variables
    path_in = input_arguments_list[0]
    rt_mz_name_file = input_arguments_list[1]
    user_reference_masses_file_name =  input_arguments_list[2]
    output_file_name = input_arguments_list[3]
    delta_mz = input_arguments_list[4]


    # We read name, rt and mz
    rt_mz_name_data = ev.read_rt_mz_csv(path_in, rt_mz_name_file)

    for spectrum_rt_mz_name_data in rt_mz_name_data:
        print("_________________________________________________")
        print("RT MZ NAME DATA:")
        print("File name:", spectrum_rt_mz_name_data[0])
        print("RT:", spectrum_rt_mz_name_data[1], "Delta RT:", spectrum_rt_mz_name_data[2])
        print("MZ:", spectrum_rt_mz_name_data[3], "Delta MZ:", spectrum_rt_mz_name_data[4])
        

    # We read user reference masses input
    user_reference_masses_list =  ev.read_user_mass_references_csv(path_in, user_reference_masses_file_name)

    print("_________________________________________________")
    print("User reference masses:")
    for reference_mass in user_reference_masses_list:
        print(reference_mass, end = ",")
    print("")


    # We evaluate all the spectra

    evaluation_list = []
    quality_list = []
    score_evalutation_list = []
    name_list = []
    spectrum_data_list = []

    for window in rt_mz_name_data:

        ## Window parameters
        name_file = window[0]

        w_retention_time = window[1]
        w_delta_rt = window[2]

        w_precursor_mz = window[3]
        w_delta_mz = window[4]
        

        ## Find spectra within RT and MZ window
        ms1_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, w_precursor_mz, w_retention_time, w_delta_mz, w_delta_rt, ms_level_1 = True)
        ms2_spectra_found = cp.find_spectra_by_mz_and_rt(name_file, w_precursor_mz, w_retention_time, w_delta_mz, w_delta_rt)

        print("NUMBER SCAN FOUND:", len(ms2_spectra_found))

        ## Average spectra found
        average_ms1 = cp.average_spectra_ordered(ms1_spectra_found, delta_mz + 0.02, ms1 = True) #
        average_ms2 = cp.average_spectra_ordered(ms2_spectra_found, delta_mz) #


        # Evaluate the spectrum
        evaluation_out = ev.evaluate_spectrum(average_ms2, average_ms1, user_reference_masses_list, delta_mz) #


        # Determine quality
        quality_out = ev.determine_quality_logical(evaluation_out) #
        traffic_quality = ev.quality_to_traffic_light(quality_out)


        # Get score from evaluation
        score_evalutation_out = ev.score_evaluation(evaluation_out, quality_out) #


        strong_coelution_peaks, weak_coelution_peaks, precursor_peak = evaluation_out[0]
        not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation_out[1]
        not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation_out[2]
        signal_noise_ratio = evaluation_out[3]
        max_peak = evaluation_out[4]
        grass_level = evaluation_out[5]

        evaluation_list.append(evaluation_out)
        quality_list.append(traffic_quality)
        score_evalutation_list.append(score_evalutation_out)
        name_list.append(name_file)

        spectrum_data = [name_file, evaluation_out, traffic_quality, score_evalutation_out, w_retention_time, w_delta_rt, w_precursor_mz, w_delta_mz]
        spectrum_data_list.append(spectrum_data)

        print("_________________________________________________")

        print("NAME:", name_file)
        print("Retention time:", w_retention_time/60)

        print("Assessed quality:", quality_out)

        print("Assessed traffic quality:", traffic_quality)

        print("Assessed score:", score_evalutation_out)

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

    
    ev.order_evaluation(spectrum_data_list)

    print("ORDERED SCORES:")
    for spectrum_data in spectrum_data_list:
        print("NAME", spectrum_data[0], "RT:", spectrum_data[4]/60, "Score:", spectrum_data[3])


    ev.write_results_onto_csv(path_in, output_file_name, spectrum_data_list)



if __name__ == "__main__":
    main()