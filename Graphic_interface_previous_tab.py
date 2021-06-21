import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import Evaluation_functions as ev
import Class_parser as cp
import sys
import os

# Run function
def run(spectra_folder, rt_mz_name_path, user_reference_masses_path, output_file_path, delta_mz):
    
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

    ###################################################################################################################################

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


    ev.write_results_onto_csv(output_dir, output_file_name, spectrum_data_list)

    return(spectrum_data_list)



# Results functions
def results_window(spectrum_data_list):

    # results_window settings
    results_window = tk.Tk()
    results_window.geometry("800x700")
    results_window.title("Results_MS2_evaluator")

    # Upper labels
    score_lbl = tk.Label(results_window, text = "Score")
    score_lbl.grid(column = 0, row = 0)

    quality_lbl = tk.Label(results_window, text = "Quality")
    quality_lbl.grid(column = 1, row = 0)

    file_name_lbl = tk.Label(results_window, text = "File name")
    file_name_lbl.grid(column = 2, row = 0)

    rt_lbl = tk.Label(results_window, text = "Retention time")
    rt_lbl.grid(column = 3, row = 0)

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
        
        column_label = column_start_results
        for label in spectrum_labels:

            label.grid(column = column_label, row = row_label)
            column_label += 1
        
        row_label += 1

    
    

        



    
    

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
    
    ### Spectra_folder
    column_spectra_folder = 0
    row_spectra_folder = 0

    ## Label 
    spectra_folder_lbl = tk.Label(main_window, text = "Spectra folder:")
    spectra_folder_lbl.grid(column = column_spectra_folder, row = row_spectra_folder)

    ## Entry
    spectra_folder_entry = tk.Entry(main_window, width = 20)
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
    spectra_folder_button = tk.Button(main_window, text = "Save", command = click_spectra_folder)
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
    spectra_folder_button = tk.Button(main_window, text = "Browse", command = click_spectra_folder_browse)
    spectra_folder_button.grid(column = column_spectra_folder + 3, row = row_spectra_folder)


    ### Input_file
    column_input_file = 0
    row_input_file = 1

    ## Label 
    input_file_lbl = tk.Label(main_window, text = "Input file:")
    input_file_lbl.grid(column = column_input_file, row = row_input_file)

    ## Entry
    input_file_entry = tk.Entry(main_window, width = 20)
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
    input_file_button = tk.Button(main_window, text = "Save", command = click_input_file)
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
    input_browse_button = tk.Button(main_window, text = "Browse", command = click_input_browse)
    input_browse_button.grid(column = column_input_file + 3, row = row_input_file)


    ### Output_file
    column_output_file = 0
    row_output_file = 2    

    ## Label 
    output_file_lbl = tk.Label(main_window, text = "Output file:")
    output_file_lbl.grid(column = column_output_file, row = row_output_file)

    ## Entry
    output_file_entry = tk.Entry(main_window, width = 20)
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
    output_file_button = tk.Button(main_window, text = "Save", command = click_output_file)
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
    output_browse_button = tk.Button(main_window, text = "Browse", command = click_output_browse)
    output_browse_button.grid(column = column_output_file + 3, row = row_output_file)

    
    ### Reference_masses
    column_reference_masses = 0
    row_reference_masses = 3    

    ## Label 
    reference_masses_lbl = tk.Label(main_window, text = "Reference masses file:")
    reference_masses_lbl.grid(column = column_reference_masses, row = row_reference_masses)

    ## Entry
    reference_masses_entry = tk.Entry(main_window, width = 20)
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
    reference_masses_file_button = tk.Button(main_window, text = "Save", command = click_reference_masses_file)
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
    reference_masses_browse_button = tk.Button(main_window, text = "Browse", command = click_reference_masses_browse)
    reference_masses_browse_button.grid(column = column_reference_masses + 3, row = row_reference_masses)







    ### Run
    column_run = 4
    row_run = 4

    # Click function
    def click_run():
        print("Spectra_folder_was:", spectra_folder.get())
        print("Input file was:", input_file.get())
        print("Output file was:", output_file.get())
        print("Reference mass file was:", reference_masses_file.get())
        
        delta_mz = 0.01

        # Execute evaluation
        spectrum_data_list = run(spectra_folder.get(), input_file.get(), reference_masses_file.get(), output_file.get(), delta_mz)

        # Open new window
        results_window(spectrum_data_list)


    
    # Button
    run_button = tk.Button(main_window, text = "Run", command = click_run)
    run_button.grid(column = column_run, row = row_run)
    
    
    main_window.mainloop()

    








if __name__ == "__main__":
    main()