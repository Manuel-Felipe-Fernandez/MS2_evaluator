import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
import Evaluation_functions as ev
import Class_parser as cp
import sys
import os

# Retention time function
def rt_to_window(w_retention_time, w_delta_rt, decimal_places = 2):
    
    lower_rt = round(w_retention_time - w_delta_rt, 2)
    upper_rt = round(w_retention_time + w_delta_rt, 2)

    return (lower_rt, upper_rt)
    
# Run function
def run(spectra_folder, rt_mz_name_path, user_reference_masses_path, output_file_path,
        delta_mz = 0.01, delta_coelution = 1.3,
        lower_percentage_coelution = 10, lower_percentage_reference_masses = 10, lower_percentage_crosstalk = 10,
        medium_percentage_coelution = 40, medium_percentage_reference_masses = 40, medium_percentage_crosstalk = 40,
        upper_percentage_coelution = 50, upper_percentage_reference_masses = 50, upper_percentage_crosstalk = 50,
        weight_coelution = 0.8, weight_reference_masses = 0.7,
        lower_signal_noise_ratio = 6, medium_signal_noise_ratio = 50):
    
    # File names and path
    print("Input into run")

    print("spectra_folder", spectra_folder)

    rt_mz_name_dir, rt_mz_name_file_name  = os.path.split(rt_mz_name_path)
    print("rt_mz_name_file_name:", rt_mz_name_file_name, "rt_mz_name_dir:", rt_mz_name_dir)

    user_reference_masses_dir, user_reference_masses_file_name = os.path.split(user_reference_masses_path)
    print("user_reference_masses_file_name:", user_reference_masses_file_name, "user_reference_masses_dir:", user_reference_masses_dir)

    output_dir, output_file_name = os.path.split(output_file_path)
    print("output_file_name:", output_file_name, "output_dir:", output_dir)

    print("")

    
    # Run evaluation

    rt_mz_name_data = ev.read_rt_mz_csv(rt_mz_name_dir, rt_mz_name_file_name)

    for spectrum_rt_mz_name_data in rt_mz_name_data:
        print("_________________________________________________")
        print("RT MZ NAME DATA:")
        print("File name:", spectrum_rt_mz_name_data[0])
        print("RT:", spectrum_rt_mz_name_data[1], "Delta RT:", spectrum_rt_mz_name_data[2])
        print("MZ:", spectrum_rt_mz_name_data[3], "Delta MZ:", spectrum_rt_mz_name_data[4])
        

    # We read user reference masses input
    user_reference_masses_list =  ev.read_user_mass_references_csv(user_reference_masses_dir, user_reference_masses_file_name)

    print("_________________________________________________")
    print("User reference masses:")
    for reference_mass in user_reference_masses_list:
        print(reference_mass, end = ",")
    print("")


    # We evaluate all the spectra
    os.chdir(spectra_folder)

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

        ## Average spectra found
        average_ms1 = cp.average_spectra_ordered(ms1_spectra_found, delta_mz + 0.02, ms1 = True)
        average_ms2 = cp.average_spectra_ordered(ms2_spectra_found, delta_mz)


        # Evaluate the spectrum
        evaluation_out = ev.evaluate_spectrum(average_ms2, average_ms1, user_reference_masses_list,
                                            delta_mz, delta_coelution,
                                            lower_percentage_coelution, lower_percentage_reference_masses, lower_percentage_crosstalk, 
                                            medium_percentage_coelution, medium_percentage_reference_masses, medium_percentage_crosstalk)


        # Determine quality
        quality_out = ev.determine_quality_logical(evaluation_out, lower_signal_noise_ratio, medium_signal_noise_ratio)
        traffic_quality = ev.quality_to_traffic_light(quality_out)


        # Get score from evaluation
        score_evalutation_out = ev.score_evaluation(evaluation_out, quality_out,
                                lower_percentage_coelution = lower_percentage_coelution,
                                medium_percentage_coelution = medium_percentage_coelution,
                                upper_percentage_coelution = upper_percentage_coelution,

                                lower_percentage_reference_masses = lower_percentage_reference_masses,
                                medium_percentage_reference_masses = medium_percentage_reference_masses,
                                upper_percentage_reference_masses = upper_percentage_reference_masses,

                                lower_percentage_crosstalk = lower_percentage_crosstalk,
                                medium_percentage_crosstalk = medium_percentage_crosstalk,
                                upper_percentage_crosstalk = upper_percentage_crosstalk,
                                
                                weight_coelution = weight_coelution,
                                weight_reference_masses = weight_reference_masses)


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

        print("Number scan found:", len(ms2_spectra_found))

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


    ev.write_results_onto_csv(output_dir, output_file_name, spectrum_data_list)

    return(spectrum_data_list)

# Options tab functions
def is_pos_float(number):
    """
    Function that returns true if number and if positive,
    returns false if not
    """
    bool_out = False

    try:
        number = float(number)
        number_float = True
    except:
        number_float = False
    
    if number_float and number > 0:
        bool_out = True

    return bool_out

def label_entry_button(tab, variable, label_text, default_value, start_row = 0, start_column = 0):
    ## Default value
    variable.set(default_value)

    ## Label 
    variable_lbl = tk.Label(tab, text = label_text)
    variable_lbl.grid(column = start_column, row = start_row)

    ## Entry
    variable_entry = tk.Entry(tab, width = 5)
    variable_entry.insert(0, default_value)
    variable_entry.grid(column = start_column + 1, row = start_row)

    # Click function
    def click_save():
        initial_variable = variable_entry.get()
        initial_variable = initial_variable.replace('"', '')

        if not is_pos_float(initial_variable):

            tk.messagebox.showinfo('Type Error', "The variable inserted is not a positive number")
            raise TypeError("The variable inserted is not a positive number, please insert a valid variable")
            
        
        else:

            variable.set(initial_variable)
            print("The variable", variable.get(), "is valid")
    
    # Button
    variable_button = tk.Button(tab, text = "Save", command = click_save)
    variable_button.grid(column = start_column + 2, row = start_row)

    return(variable_entry)

def options_tab(main_tab_control):
    """
    delta_mz = 0.01, delta_coelution = 1.3,
    lower_percentage_coelution = 10, lower_percentage_reference_masses = 10, lower_percentage_crosstalk = 10,
    medium_percentage_coelution = 40, medium_percentage_reference_masses = 40, medium_percentage_crosstalk = 40,
    upper_percentage_coelution = 50, upper_percentage_reference_masses = 50, upper_percentage_crosstalk = 50,
    weight_coelution = 0.8, weight_reference_masses = 0.7,
    lower_signal_noise_ratio = 6, medium_signal_noise_ratio = 50
    """
    # Initiate tab
    options_tab = ttk.Frame(main_tab_control)
    main_tab_control.add(options_tab, text = "Options")

    # Default values
    d_delta_mz = 0.01
    d_delta_coelution = 1.3
    d_lower_percentage_coelution = 10
    d_lower_percentage_reference_masses = 10
    d_lower_percentage_crosstalk = 10
    d_medium_percentage_coelution = 40
    d_medium_percentage_reference_masses = 40
    d_medium_percentage_crosstalk = 40
    d_upper_percentage_coelution = 50
    d_upper_percentage_reference_masses = 50
    d_upper_percentage_crosstalk = 50
    d_weight_coelution = 0.8
    d_weight_reference_masses = 0.7
    d_lower_signal_noise_ratio = 6
    d_medium_signal_noise_ratio = 50

    # List of default values
    labels_list = ["delta_mz", "delta_coelution",
    "lower_percentage_coelution", "lower_percentage_reference_masses", "lower_percentage_crosstalk",
    "medium_percentage_coelution", "medium_percentage_reference_masses", "medium_percentage_crosstalk",
    "upper_percentage_coelution", "upper_percentage_reference_masses", "upper_percentage_crosstalk",
    "weight_coelution", "weight_reference_masses",
    "lower_signal_noise_ratio", "medium_signal_noise_ratio"]

    default_values_list = [d_delta_mz, d_delta_coelution,
                            d_lower_percentage_coelution, d_lower_percentage_reference_masses, d_lower_percentage_crosstalk,
                            d_medium_percentage_coelution, d_medium_percentage_reference_masses, d_medium_percentage_crosstalk,
                            d_upper_percentage_coelution, d_upper_percentage_reference_masses, d_upper_percentage_crosstalk,
                            d_weight_coelution, d_weight_reference_masses,
                            d_lower_signal_noise_ratio, d_medium_signal_noise_ratio]

    start_row = 0
    start_column = 0

    variables_list = []
    variable_entry_list = []
    for var in range(len(default_values_list)):
        variable = tk.StringVar()
        variables_list.append(variable)
        varaible_entry = label_entry_button(options_tab, variables_list[var], labels_list[var], default_values_list[var], start_row, start_column)
        variable_entry_list.append(varaible_entry)
        start_row += 1

    ## Save all
    # Clicked function
    def clicked_save_all():
        entry_index = 0
        for variable_entry in variable_entry_list:
            initial_variable = variable_entry.get()
            initial_variable = initial_variable.replace('"', '')

            if not is_pos_float(initial_variable):

                tk.messagebox.showinfo('Type Error', "The variable inserted in", labels_list[entry_index] , "is not a positive number")
                raise TypeError("The variable inserted in", labels_list[entry_index], "is not a positive number, please insert a valid variable")
                
            
            else:

                variables_list[entry_index].set(initial_variable)
                print("The variable", variables_list[entry_index].get(), "is valid")
            
            entry_index += 1
    
    # Button
    spectra_folder_button = tk.Button(options_tab, text = "Save All", command = clicked_save_all)
    spectra_folder_button.grid(column = 4, row = len(labels_list))

    
    return(variables_list)



# Results functions
def results_window(spectrum_data_list):

    # results_window settings
    results_window = tk.Tk()
    results_window.geometry("800x700")
    results_window.title("Results_MS2_evaluator")

    # Upper labels
    column_start = 0
    row_start = 0

    number_lbl = tk.Label(results_window, text = "Number")
    number_lbl.grid(column = column_start, row = 0)

    score_lbl = tk.Label(results_window, text = "Score")
    score_lbl.grid(column = column_start + 1, row = 0)

    quality_lbl = tk.Label(results_window, text = "Quality")
    quality_lbl.grid(column = column_start + 2, row = 0)

    file_name_lbl = tk.Label(results_window, text = "File name")
    file_name_lbl.grid(column = column_start + 3, row = 0)

    rt_lbl = tk.Label(results_window, text = "Retention time")
    rt_lbl.grid(column = column_start + 4, row = 0)

    # Results Label function
    def row_results_lbl(spectrum_results):

        # Unpack information in spectrum data
        name = spectrum_results[0]

        evaluation = spectrum_results[1]
        strong_coelution_peaks, weak_coelution_peaks, precursor_peak = evaluation[0]
        not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation[1]
        not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation[2]
        signal_noise_ratio = evaluation[3]
        max_peak = evaluation[4]
        grass_level = evaluation[5] 

        quality = spectrum_results[2]

        score = spectrum_results[3]

        w_retention_time = spectrum_results[4]
        w_delta_rt = spectrum_results[5]

        w_mz = spectrum_results[6]
        w_delta_mz = spectrum_results[7]

        if quality == 1:
            quality_str = "Bad"
        if quality == 2:
            quality_str = "Regular"
        if quality == 3:
            quality_str = "Good"

        # Generate labels
        result_score_lbl = tk.Label(results_window, text = str(round(score, 2)))

        result_quality_lbl = tk.Label(results_window, text = quality_str)

        result_file_name_lbl = tk.Label(results_window, text = name)

        result_rt_lbl = tk.Label(results_window, text = str(round(w_retention_time/60, 2)))

        spectrum_labels = [result_score_lbl, result_quality_lbl, result_file_name_lbl, result_rt_lbl]
        return(spectrum_labels)
    
    # Spectrum labels list
    spectrum_labels_list = []

    for spectrum_data in spectrum_data_list:
        spectrum_labels = row_results_lbl(spectrum_data)
        spectrum_labels_list.append(spectrum_labels)
    
    # Results grid
    row_start_results = 1
    column_start_results = 0

    row_label = row_start_results
    for spectrum_labels in spectrum_labels_list:
        
        column_label = column_start_results + 1
        for label in spectrum_labels:

            label.grid(column = column_label, row = row_label)
            column_label += 1
        
        row_label += 1

    ## Number button

    # Button
    number_button_list = []
    spectrum_index_var_list = []

    column_button = column_start_results
    row_button = row_start_results
    
    for spectrum_index in range(len(spectrum_labels_list)):
        spectrum_index_var = tk.StringVar()
        spectrum_index_var_list.append(spectrum_index_var)
        spectrum_index_button(results_window, spectrum_data_list, spectrum_index_var_list[spectrum_index], spectrum_index, spectrum_index + 1)        

def spectrum_index_button(tab, spectrum_data_list, variable, spectrum_index, row, column = 0):
    ## Default value
    variable.set(spectrum_index)

    # Click function
    def click_save():
        initial_variable = variable.get()
        single_result_window(spectrum_data_list, int(initial_variable))
    
    # Button
    variable_button = tk.Button(tab, text = str(variable.get()), command = click_save)
    variable_button.grid(column = column, row = row)
    
def single_result_window(spectrum_data_list, number_button):

    ## Unpack information in spectrum data list 
    spectrum_data = spectrum_data_list[int(number_button)]

    
    name = spectrum_data[0]
    experiment_name, experiment_extension = os.path.splitext(name)

    evaluation = spectrum_data[1]
    strong_coelution_peaks, weak_coelution_peaks, precursor_peak = evaluation[0]
    not_reference_masses, weak_reference_masses, strong_reference_masses = evaluation[1]
    not_crosstalk, weak_crosstalk, strong_crosstalk = evaluation[2]
    signal_noise_ratio = evaluation[3]
    max_peak = evaluation[4]
    grass_level = evaluation[5] 

    quality = spectrum_data[2]

    score = spectrum_data[3]

    w_retention_time = spectrum_data[4]
    w_delta_rt = spectrum_data[5]
    w_lower_rt, w_upper_rt = rt_to_window(w_retention_time, w_delta_rt)

    w_mz = spectrum_data[6]
    w_delta_mz = spectrum_data[7]

    if quality == 1:
        quality_str = "Bad"
    if quality == 2:
        quality_str = "Regular"
    if quality == 3:
        quality_str = "Good"

    ## single_result_window settings
    single_result_window = tk.Tk()
    single_result_window.geometry("800x700")
    single_result_window.title(experiment_name)
    
    ## Name label
    name_title = "Name:"
    name_title_lbl = tk.Label(single_result_window, text = name_title)
    name_title_lbl.grid(row = 0, column = 0)

    name_txt = experiment_name
    name_lbl = tk.Label(single_result_window, text = name_txt)
    name_lbl.grid(row = 0, column = 1)

    ## Retention time label
    rt_title = "Retention time:"
    rt_title_lbl = tk.Label(single_result_window, text = rt_title)
    rt_title_lbl.grid(row = 1, column = 0)

    rt_mean_txt = str(round(w_retention_time/60, 2))
    rt_w_txt = "(" + str(round(w_lower_rt/60, 2)) + "-" + str(round(w_upper_rt/60, 2)) + ")"
    rt_txt = rt_mean_txt + " " + rt_w_txt
    rt_lbl = tk.Label(single_result_window, text = rt_txt)
    rt_lbl.grid(row = 1, column = 1)

    ## Quality label
    quality_title = "Quality:"
    quality_title_lbl = tk.Label(single_result_window, text = quality_title)
    quality_title_lbl.grid(row = 2, column = 0)

    quality_txt = quality_str
    quality_lbl = tk.Label(single_result_window, text = quality_txt)
    quality_lbl.grid(row = 2, column = 1)

    ## Score label
    score_title = "Score:"
    score_title_lbl = tk.Label(single_result_window, text = score_title)
    score_title_lbl.grid(row = 3, column = 0)

    score_txt = str(round(score, 2))
    score_lbl = tk.Label(single_result_window, text = score_txt)
    score_lbl.grid(row = 3, column = 1)

    ## Maximum peak label
    max_peak_title = "Maximum intensity peak:"
    max_peak_title_lbl = tk.Label(single_result_window, text = max_peak_title)
    max_peak_title_lbl.grid(row = 4, column = 0)

    max_peak_mz = max_peak.get_mz()
    max_peak_i = max_peak.get_intensity()
    max_peak_txt = "MZ: " + str(round(max_peak_mz, 3)) + "  I: " + str(round(max_peak_i, 2))
    max_peak_lbl = tk.Label(single_result_window, text = max_peak_txt)
    max_peak_lbl.grid(row = 4, column = 1)

    ## Noise label
    grass_level_title = "Noise/grass intensity:"
    grass_level_title_lbl = tk.Label(single_result_window, text = grass_level_title)
    grass_level_title_lbl.grid(row = 5, column = 0)

    grass_level_txt = str(round(grass_level, 2))
    grass_level_lbl = tk.Label(single_result_window, text = grass_level_txt)
    grass_level_lbl.grid(row = 5, column = 1)

    ## Signal to noise ratio label
    signal_noise_ratio_title = "Signal to noise ratio:"
    signal_noise_ratio_title_lbl = tk.Label(single_result_window, text = signal_noise_ratio_title)
    signal_noise_ratio_title_lbl.grid(row = 6, column = 0)

    signal_noise_ratio_txt = str(round(signal_noise_ratio, 2))
    signal_noise_ratio_lbl = tk.Label(single_result_window, text = signal_noise_ratio_txt)
    signal_noise_ratio_lbl.grid(row = 6, column = 1)

    ## Peaks labels
    def label_multiple_peaks(title_label_txt, peaks, row_start, column_start = 0, digits_mz = 3, digits_intensity = 0):
        
        title_label = tk.Label(single_result_window, text = title_label_txt)
        title_label.grid(row = row_start, column = column_start)

        peak_label_list = []
        number_peak = column_start + 1
        for peak in peaks:

            mz = peak.get_mz()
            intensity = peak.get_intensity()

            peaks_label_txt = "MZ: " + str(round(mz, digits_mz)) + "  I: " + str(round(intensity, digits_intensity)) 

            peak_lbl = tk.Label(single_result_window, text = peaks_label_txt)
            peak_lbl.grid(row = row_start, column = number_peak)

            number_peak += 1

    row_peaks_start = 7

    # Strong coelution label
    if len(strong_coelution_peaks) > 0:
        
        strong_coelution_txt = "Strong coelution found: "
        label_multiple_peaks(strong_coelution_txt, strong_coelution_peaks, row_peaks_start)
        
        row_peaks_start += 1

    # Strong reference masses label
    if len(strong_reference_masses) > 0:
        
        strong_reference_masses_txt = "Strong reference masses found: "
        label_multiple_peaks(strong_reference_masses_txt, strong_reference_masses, row_peaks_start)
        
        row_peaks_start += 1

    # Strong crosstalk label
    if len(strong_crosstalk) > 0:
        
        strong_crosstalk_txt = "Strong crosstalk found: "
        label_multiple_peaks(strong_crosstalk_txt, strong_crosstalk, row_peaks_start)
        
        row_peaks_start += 1

    # Weak coelution label
    if len(weak_coelution_peaks) > 0:
        
        weak_coelution_txt = "Weak coelution found: "
        label_multiple_peaks(weak_coelution_txt, weak_coelution_peaks, row_peaks_start)
        
        row_peaks_start += 1

    # Weak reference masses label
    if len(weak_reference_masses) > 0:
        
        weak_reference_masses_txt = "Strong reference masses found: "
        label_multiple_peaks(weak_reference_masses_txt, weak_reference_masses, row_peaks_start)
        
        row_peaks_start += 1

    # Weak crosstalk label
    if len(weak_crosstalk) > 0:
        
        weak_crosstalk_txt = "Strong crosstalk found: "
        label_multiple_peaks(weak_crosstalk_txt, weak_crosstalk, row_peaks_start)
        
        row_peaks_start += 1
    


    

def main():

    # main_window settings
    main_window = tk.Tk()
    main_window.geometry("800x700")
    main_window.title("Main_MS2_evaluator")

    # variable definition
    spectra_folder = tk.StringVar()
    input_file = tk.StringVar()
    output_file = tk.StringVar()
    reference_masses_file = tk.StringVar()

    # default values
    input_file_default = "Folder_of_tool/input.txt"
    output_file_default = "Folder_of_tool/output.txt"
    reference_masses_file_default = "Folder_of_tool/reference_masses.txt"

    # set default values
    input_file.set(input_file_default)
    output_file.set(output_file_default)
    reference_masses_file.set(reference_masses_file_default)
    
    # Tab control
    main_tab_control = ttk.Notebook(main_window)

    #### Main Tab
    main_tab = ttk.Frame(main_tab_control)
    main_tab_control.add(main_tab, text = "Run")
    
    ### Spectra_folder
    column_spectra_folder = 0
    row_spectra_folder = 0

    ## Label 
    spectra_folder_lbl = tk.Label(main_tab, text = "Spectra folder:")
    spectra_folder_lbl.grid(column = column_spectra_folder, row = row_spectra_folder)

    ## Entry
    spectra_folder_entry = tk.Entry(main_tab, width = 20)
    spectra_folder_entry.grid(column = column_spectra_folder + 1, row = row_spectra_folder)

    # Click function
    def click_spectra_folder():
        initial_spectra_folder = spectra_folder_entry.get()
        initial_spectra_folder = initial_spectra_folder.replace('"', '')

        if not os.path.isdir(initial_spectra_folder):

            tk.messagebox.showinfo('Path Error', "The path inserted does not exist, insert a valid path")
            raise FileNotFoundError("The path inserted does not exist, insert a valid path")
            
        
        else:

            spectra_folder.set(initial_spectra_folder)
            print("The path", spectra_folder.get(), "is valid")
    
    # Button
    spectra_folder_button = tk.Button(main_tab, text = "Save", command = click_spectra_folder)
    spectra_folder_button.grid(column = column_spectra_folder + 2, row = row_spectra_folder)

    ## Browse
    # Click function
    def click_spectra_folder_browse():
        result = tk.filedialog.askdirectory()
        spectra_folder.set(result)
        spectra_folder_entry.delete(0,"end")
        spectra_folder_entry.insert(0, result)
        print("Path browsed:", spectra_folder.get())
    
    # Button
    spectra_folder_button = tk.Button(main_tab, text = "Browse", command = click_spectra_folder_browse)
    spectra_folder_button.grid(column = column_spectra_folder + 3, row = row_spectra_folder)


    ### Input_file
    column_input_file = 0
    row_input_file = 1

    ## Label 
    input_file_lbl = tk.Label(main_tab, text = "Input file:")
    input_file_lbl.grid(column = column_input_file, row = row_input_file)

    ## Entry
    input_file_entry = tk.Entry(main_tab, width = 20)
    input_file_entry.insert(0, input_file_default)
    input_file_entry.grid(column = column_input_file + 1, row = row_input_file)

    # Click function
    def click_input_file():
        initial_input = input_file_entry.get()
        initial_input = initial_input.replace('"', '')

        if not os.path.isfile(initial_input):

            tk.messagebox.showinfo('Path Error', "The path inserted does not exist, insert a valid path")
            raise FileNotFoundError("The path inserted does not exist, insert a valid path")
            
        
        else:

            input_file.set(initial_input)
            print("The path", input_file.get(), "is valid")
    
    # Button
    input_file_button = tk.Button(main_tab, text = "Save", command = click_input_file)
    input_file_button.grid(column = column_input_file + 2, row = row_input_file)

    ## Browse
    # Click function
    def click_input_browse():
        result = tk.filedialog.askopenfilename()
        input_file.set(result)
        input_file_entry.delete(0,"end")
        input_file_entry.insert(0, result)
        print("Path browsed:", input_file.get())
    
    # Button
    input_browse_button = tk.Button(main_tab, text = "Browse", command = click_input_browse)
    input_browse_button.grid(column = column_input_file + 3, row = row_input_file)


    ### Output_file
    column_output_file = 0
    row_output_file = 2    

    ## Label 
    output_file_lbl = tk.Label(main_tab, text = "Output file:")
    output_file_lbl.grid(column = column_output_file, row = row_output_file)

    ## Entry
    output_file_entry = tk.Entry(main_tab, width = 20)
    output_file_entry.insert(0, output_file_default)
    output_file_entry.grid(column = column_output_file + 1, row = row_output_file)

    # Click function
    def click_output_file():
        initial_output = output_file_entry.get()
        initial_output = initial_output.replace('"', '')

        if not os.path.isfile(initial_output):

            tk.messagebox.showinfo('Path Error', "The path inserted does not exist, insert a valid path")
            raise FileNotFoundError("The path inserted does not exist, insert a valid path")
            
        
        else:

            output_file.set(initial_output)
            print("The path", output_file.get(), "is valid")
    
    # Button
    output_file_button = tk.Button(main_tab, text = "Save", command = click_output_file)
    output_file_button.grid(column = column_output_file + 2, row = row_output_file)

    ## Browse
    # Click function
    def click_output_browse():
        result = tk.filedialog.askopenfilename()
        output_file.set(result)
        output_file_entry.delete(0,"end")
        output_file_entry.insert(0, result)
        print("Path browsed:", output_file.get())
    
    # Button
    output_browse_button = tk.Button(main_tab, text = "Browse", command = click_output_browse)
    output_browse_button.grid(column = column_output_file + 3, row = row_output_file)

    
    ### Reference_masses
    column_reference_masses = 0
    row_reference_masses = 3    

    ## Label 
    reference_masses_lbl = tk.Label(main_tab, text = "Reference masses file:")
    reference_masses_lbl.grid(column = column_reference_masses, row = row_reference_masses)

    ## Entry
    reference_masses_entry = tk.Entry(main_tab, width = 20)
    reference_masses_entry.insert(0, reference_masses_file_default)
    reference_masses_entry.grid(column = column_reference_masses + 1, row = row_reference_masses)

    # Click function
    def click_reference_masses_file():
        initial_reference_masses = reference_masses_entry.get()
        initial_reference_masses = initial_reference_masses.replace('"', '')

        if not os.path.isfile(initial_reference_masses):

            tk.messagebox.showinfo('Path Error', "The path inserted does not exist, insert a valid path")
            raise FileNotFoundError("The path inserted does not exist, insert a valid path")
            
        
        else:

            reference_masses_file.set(initial_reference_masses)
            print("The path", reference_masses_file.get(), "is valid")
    
    # Button
    reference_masses_file_button = tk.Button(main_tab, text = "Save", command = click_reference_masses_file)
    reference_masses_file_button.grid(column = column_reference_masses + 2, row = row_reference_masses)

    ## Browse
    # Click function
    def click_reference_masses_browse():
        result = tk.filedialog.askopenfilename()
        reference_masses_file.set(result)
        reference_masses_entry.delete(0,"end")
        reference_masses_entry.insert(0, result)
        print("Path browsed:", reference_masses_file.get())
    
    # Button
    reference_masses_browse_button = tk.Button(main_tab, text = "Browse", command = click_reference_masses_browse)
    reference_masses_browse_button.grid(column = column_reference_masses + 3, row = row_reference_masses)

    # Scrolled text
    reference_masses_browse_scrolled = tk.scrolledtext.ScrolledText(main_tab, width=40, height=2)
    reference_masses_browse_scrolled.grid(columnspan = 4, row = row_reference_masses + 1, sticky = 'nsew')
    


    ### Options tab
    option_variables_list = options_tab(main_tab_control)
    (delta_mz, delta_coelution,
    lower_percentage_coelution, lower_percentage_reference_masses, lower_percentage_crosstalk,
    medium_percentage_coelution, medium_percentage_reference_masses, medium_percentage_crosstalk,
    upper_percentage_coelution, upper_percentage_reference_masses, upper_percentage_crosstalk,
    weight_coelution, weight_reference_masses,
    lower_signal_noise_ratio, medium_signal_noise_ratio) = option_variables_list


    ### Run
    column_run = 4
    row_run = 5

    # Click function
    def click_run():
        print("Run variables")
        print("Spectra_folder_was:", spectra_folder.get())
        print("Input file was:", input_file.get())
        print("Output file was:", output_file.get())
        print("Reference mass file was:", reference_masses_file.get())

        print("\nOption variables")
        print("Delta_mz was:", delta_mz.get())
        print("Delta_coelution was:", option_variables_list[1].get())
        print("Lower_pecentage_coelution was:", option_variables_list[2].get())
        print("Lower_pecentage_reference_masses was:", option_variables_list[3].get())
        print("Lower_pecentage_crosstalk was:", option_variables_list[4].get())
        print("Medium_pecentage_coelution was:", option_variables_list[5].get())
        print("Medium_pecentage_reference_masses was:", option_variables_list[6].get())
        print("Medium_pecentage_criosstalk was:", option_variables_list[7].get())
        print("Upper_pecentage_coelution was:", option_variables_list[8].get())
        print("Upper_pecentage_reference_masses was:", option_variables_list[9].get())
        print("Upper_pecentage_crosstalk was:", option_variables_list[10].get())
        print("weight_coelution was:", option_variables_list[11].get())
        print("weight_reference_masses was:", option_variables_list[12].get())
        print("Lower_signal_noise_ratio was:", option_variables_list[13].get())
        print("Medium_signal_noise_ratio was:", medium_signal_noise_ratio.get())

        print("")

        # Execute evaluation
        spectrum_data_list = run(spectra_folder.get(), input_file.get(), reference_masses_file.get(), output_file.get(), float(delta_mz.get()), float(delta_coelution.get()),
                                float(lower_percentage_coelution.get()), float(lower_percentage_reference_masses.get()), float(lower_percentage_crosstalk.get()),
                                float(medium_percentage_coelution.get()), float(medium_percentage_reference_masses.get()), float(medium_percentage_crosstalk.get()),
                                float(upper_percentage_coelution.get()), float(upper_percentage_reference_masses.get()), float(upper_percentage_crosstalk.get()),
                                float(weight_coelution.get()), float(weight_reference_masses.get()),
                                float(lower_signal_noise_ratio.get()), float(medium_signal_noise_ratio.get()))

        # Open new window
        results_window(spectrum_data_list)


    
    # Button
    run_button = tk.Button(main_tab, text = "Run", command = click_run)
    run_button.grid(column = column_run, row = row_run)
    


    main_tab_control.pack(expand=1, fill='both')
    main_window.mainloop()

    


if __name__ == "__main__":
    main()