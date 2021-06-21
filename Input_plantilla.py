# Función para leer la plantilla
import csv
import os
import numpy as np
import pandas as pd
import Class_parser as cp
import Grass_Functions as gf
import matplotlib.pyplot as plt
import PyQt5




def read_mz_rt_template(dataframe_in):
    name_of_exp = dataframe_in["nombre_de_archivo"].values.tolist()
    rt_times = dataframe_in["tiempo_de_retencion"].values.tolist()
    mz_wind = dataframe_in["mz_precursor"].values.tolist()
    qualitative_value = dataframe_in["etiqueta_de_validez"].values.tolist()

    return(name_of_exp, rt_times, mz_wind, qualitative_value)

def open_template_instensity_distribution(template_file, path_in):
    """
    Reads template file, reads scans by rt and mz windows from experiments in the same folder.
    Then saves a plot for each scan in a folder with the name of the experiment and scan window.
    """

    os.chdir(path_in)

    with open(template_file) as csv_template:
        csv_reader = csv.reader(csv_template, delimiter = ",")
        line_count = 0
        sum_size = 0
        sum_number_of_spectra = 0

        for row in csv_reader:
            if line_count == 0:
                pass
                
            else:
                list_of_values = row
                size, number_of_spectra = intensity_list_file(list_of_values, path_in)
                sum_size += size 
                sum_number_of_spectra += number_of_spectra
            
            line_count += 1
            
            print(line_count)
        
        average_peaks = sum_size/sum_number_of_spectra
        print(average_peaks)


def intensity_list_file(list_of_values_in, path_in):
    
    name = list_of_values_in[0][:-2]
    name_file = name + ".mzML"
    retention_time_window = list_of_values_in[2]
    retention_time = rt_window_to_delta(retention_time_window)
    mz_precursor = float(list_of_values_in[5])
    delta_mz = 1.3
    quality = list_of_values_in[4]

    spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])
    path = path_in + "\\plot\\" + name + "_" + str(round(retention_time[0]/60, 3))

    if not os.path.exists(path):    
        os.makedirs(path)

    sum_size = 0

    for spectrum in spectra_found:

        intensity_list = spectrum.get_intensity_list()
        rt = round(spectrum.get_retention_time()/60, 3)
        size = spectrum.get_size()
        sum_size += size
        plot_intensity_list(intensity_list, name, quality, rt, size, path)
        plot_intensity_list_inverse(intensity_list, name, quality, rt, size, path)

    for spectrum in spectra_found:

        intensity_list = spectrum.get_intensity_list()
        rt = round(spectrum.get_retention_time()/60, 3)
        size = spectrum.get_size()

        path_dir = path + "\\norm"
        if not os.path.exists(path_dir):    
            os.makedirs(path_dir)
        path_plot = path_dir + "\\" + str(rt)

        plot_intensity_list_norm(intensity_list, name, quality, rt, size, path)

    plt.savefig(path_plot + "norm.jpeg" )
    plt.close()
    
    number_of_spectra = len(spectra_found)

    return(sum_size, number_of_spectra)


def plot_intensity_list(intensity_list_in, name_in, quality_in, retention_time_in, size_in,  path_in):
    
    path_dir = path_in + "\\intensity_list"
    if not os.path.exists(path_dir):    
        os.makedirs(path_dir)

    path_plot = path_dir + "\\" + str(retention_time_in)

    x = np.linspace(0, 1, len(intensity_list_in))
    label_in = name_in + " q: " + quality_in + " rt: " + str(retention_time_in) + " s: " + str(size_in)
    plt.plot(x, intensity_list_in, label = label_in)
    plt.legend()
    plt.suptitle("Intensity")
    plt.savefig(path_plot + ".jpeg" )
    plt.close()

def plot_intensity_list_norm(intensity_list_in, name_in, quality_in, retention_time_in, size_in,  path_in):

    # normalize the intensity
    max_intensity = intensity_list_in[0]
    normalized_intensity = [0] * len(intensity_list_in)

    for i in range(len(intensity_list_in)):
        normalized_intensity[i] = intensity_list_in[i] / max_intensity    

    x = np.linspace(0, 1, len(intensity_list_in))
    label_in = name_in + " q: " + quality_in + " rt: " + str(retention_time_in) + " s: " + str(size_in)
    plt.plot(x, normalized_intensity, label = label_in)
    plt.legend()
    plt.suptitle("Intensity_normalized")

def plot_intensity_list_inverse(intensity_list_in, name_in, quality_in, retention_time_in, size_in,  path_in):
    
    inverse_intensity = [0] * len(intensity_list_in)

    for i in range(len(intensity_list_in)):
        inverse_intensity[i] = 1 / intensity_list_in[i]
    
    path_dir = path_in + "\\inverse"
    if not os.path.exists(path_dir):    
        os.makedirs(path_dir)

    path_plot = path_dir + "\\" + str(retention_time_in)

    x = np.linspace(0, 1, len(intensity_list_in))
    label_in = name_in + " q: " + quality_in + " rt: " + str(retention_time_in) + " s: " + str(size_in)
    plt.plot(x, inverse_intensity, label = label_in)
    plt.legend()
    plt.suptitle("Inverse_intensity")
    plt.savefig(path_plot + "inverse.jpeg" )
    plt.close()





def rt_window_to_delta(window_in):
    """
    Converts window data to delta format
    Data format 5.6-6.1 to 5.85 +/- 0.25
    """
    split_window = window_in.split("_")
    rt_lower = float(split_window[0]) * 60
    rt_upper = float(split_window[1]) * 60

    diference = rt_upper - rt_lower
    delta = diference / 2
    rt_out = rt_lower + delta
    delta += 0.001 * 60 

    return(rt_out, delta)

def maximize_precision(template_file, path_in, lower_limit, upper_limit, step_in):

    precision_list = []
    recall_list = []
    increase_list = []

    for i in range(lower_limit, upper_limit, step_in):
        print("################################################")
        print("############Increase:", i, "################")
        print("################################################")
        precision, recall = open_template(template_file, path_in, i)
        precision_list.append(precision)
        recall_list.append(recall)
        increase_list.append(i)

    return(precision_list, recall_list, increase_list)


def open_template(template_file, path_in, increase):
    """
    Reads template file, reads scans by rt and mz windows from experiments in the same folder.
    Compares cut spectra with grass functions with peaks from template.
    """

    os.chdir(path_in)
    
    average_precision = 0
    average_recall = 0

    with open(template_file) as csv_template:
        csv_reader = csv.reader(csv_template, delimiter = ";")
        line_count = 0
        sum_size = 0
        sum_number_of_spectra = 0

        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                pass
            elif row[4] == "regular" or row[4] == "malo" or row[4] == "basura":
                pass
            else:
                list_of_values = row
                precision, recall = check_grass(list_of_values, increase)
                print("Precision:", precision)
                print("Recall:", recall)

                average_precision += precision
                average_recall += recall
            
                line_count += 1
            
            print(line_count)
        
        average_precision = average_precision / line_count
        average_recall = average_recall / line_count
    
    return(average_precision, average_recall)


def check_grass_scans(list_of_values_in, increase_stdev):
    """
    Function that returns the precision and recall of cut spectra
    """
    name = list_of_values_in[0][:-2]
    name_file = name + ".mzML"
    retention_time_window = list_of_values_in[2]
    retention_time = rt_window_to_delta(retention_time_window)
    quality = list_of_values_in[4]
    mz_precursor = float(list_of_values_in[5])
    delta_mz = 1.3
    mz_in_template = list(filter(lambda x: x != "", list_of_values_in[9:]))

    spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])

    print("Number of scans:", len(spectra_found))
    print("Label", quality)
    print("Peaks in template", mz_in_template)

    sum_size = 0

    cut_spectra = list()

    for spectrum in spectra_found:
        grass_intensity_be = gf.be_measure_grass_level(spectrum, increase = increase_stdev)
        grass_intensity_end = gf.end_measure_grass_level(spectrum, increase = increase_stdev)
        average_grass = (grass_intensity_be + grass_intensity_end) / 2
        # average_grass = gf.lowest_measure_grass_level_stdev(spectrum, increase = increase_stdev)
        # average_grass = gf.lowest_measure_grass_level(spectrum, increase = increase_stdev)
        # average_grass = gf.highest_measure_grass_level(spectrum, increase = increase_stdev)

        print("\nAverage_grass: ", average_grass)
        cut_spectrum = gf.grass_cutter(spectrum, average_grass)
        
        print("Scan_peaks  ", end = "")

        for peak in cut_spectrum.get_peaks():
            print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ", ")

        print("")

        cut_spectra.append(cut_spectrum)
    
    
    average_cut_spectra = cp.average_spectra(cut_spectra, delta_mz = 0.03)
        
    match_peaks = compare_template_with_found(mz_in_template, average_cut_spectra, delta_mz = 0.03)

    print("\nOur_peaks  ", end = "")

    for peak in average_cut_spectra.get_peaks():
        print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ",")

    print("")


    print("\nCoincident_peaks  ", end = "")

    for peak in match_peaks:
        print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ",")

    print("")


    precision = calculate_precision(match_peaks, average_cut_spectra)
    recall = calculate_recall(match_peaks, mz_in_template)

    return(precision, recall)


def check_grass(list_of_values_in, increase_stdev):
    """
    Function that returns the precision and recall of cut spectra
    """
    name = list_of_values_in[0][:-2]
    name_file = name + ".mzML"
    retention_time_window = list_of_values_in[2]
    retention_time = rt_window_to_delta(retention_time_window)
    quality = list_of_values_in[4]
    mz_precursor = float(list_of_values_in[5])
    delta_mz = 1.3

    length_row = len(list_of_values_in)
    mz_in_template = []
    start = False
    for i in range(length_row):

        if start == True:
            if list_of_values_in[i] == "coelucion" or list_of_values_in[i] == "massref":
                break
            elif list_of_values_in[i] != "":
                mz_in_template.append(float(list_of_values_in[i]))
        
        if list_of_values_in[i] == "picos_detectados":
            start = True

    spectra_found = cp.find_spectra_by_mz_and_rt(name_file, mz_precursor, retention_time[0], delta_mz, retention_time[1])

    print("Number of scans:", len(spectra_found))
    print("Label", quality)
    print("Peaks in template", mz_in_template)

    sum_size = 0

    average_spectrum = cp.average_spectra_ordered(spectra_found, 0.03)

    grass_intensity_be = gf.be_measure_grass_level(average_spectrum, increase = increase_stdev)
    grass_intensity_end = gf.end_measure_grass_level(average_spectrum, increase = increase_stdev)
    average_grass = (grass_intensity_be + grass_intensity_end) / 2
    # average_grass = gf.lowest_measure_grass_level_stdev(average_spectrum, increase = increase_stdev)
    # average_grass = gf.lowest_measure_grass_level(average_spectrum, increase = increase_stdev)
    # average_grass = gf.highest_measure_grass_level(average_spectrum, increase = increase_stdev)

    print("\nAverage_grass: ", average_grass)
    cut_spectrum = gf.grass_cutter(average_spectrum, average_grass)
    
    print("Scan_peaks  ", end = "")

    for peak in cut_spectrum.get_peaks():
        print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ", ")

    print("")
        
    match_peaks = compare_template_with_found(mz_in_template, cut_spectrum, delta_mz = 0.03)

    print("\nOur_peaks  ", end = "")

    for peak in cut_spectrum.get_peaks():
        print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ",")

    print("")


    print("\nCoincident_peaks  ", end = "")

    for peak in match_peaks:
        print("Mz:",peak.get_mz(), "Intensity", peak.get_intensity(), end = ",")

    print("")


    precision = calculate_precision(match_peaks, cut_spectrum)
    recall = calculate_recall(match_peaks, mz_in_template)

    return(precision, recall)


def compare_template_with_found(template_peaks, cut_spectrum, delta_mz = 0.5):
    """
    Function that compares the template peaks fith the cut spectrum
    Returns the list of peaks from that coincides with the mz of the cut_spectrum
    """
    list_of_coincident_peaks = list()

    for peak in template_peaks:
        
        position_last_peak_found = 0
        found_peaks = cut_spectrum.get_peaks()

        upper_mz = float(peak) + delta_mz
        lower_mz = float(peak) - delta_mz

        for cut_peak in found_peaks[position_last_peak_found:]:
            
            cut_peak_mz = cut_peak.get_mz() 

            if cut_peak_mz >= lower_mz and cut_peak_mz <= upper_mz:
                
                list_of_coincident_peaks.append(cut_peak)
    
    return(list_of_coincident_peaks)


def calculate_precision(match_peaks, cut_spectrum):
    """
    Function that calculates the precision, given the list of coincident peaks and the cut spectrum
    """
    number_match_peaks = len(match_peaks)
    number_cut_peaks = len(cut_spectrum.get_peaks())

    precision = number_match_peaks/number_cut_peaks

    return(precision)


def calculate_recall(match_peaks, template_peaks):
    """
    Function that calculates the recall, given the list of coincident peaks and the template peaks
    """
    number_match_peaks = len(match_peaks)
    number_template_peaks = len(template_peaks)

    recall = number_match_peaks/number_template_peaks

    return(recall)
            
def open_negative_template(template_file, path_in, delimiter = ","):
    """
    Function that reads negative template file
    returns: list_of_values = [names, retention_times, list_number_of_scans,
                quality_list, list_mz_precursor, list_precursor_intensities,
                noise_level_list, list_coelution_peaks, list_ref
                erence_masses,
                list_detected_peaks]
    """

    os.chdir(path_in)
    names = []
    retention_times = []
    time_windows = []
    list_number_of_scans = []
    quality_list = []
    list_mz_precursor = []
    list_precursor_intensities = []
    noise_level_list = []
    list_coelution_peaks = []
    list_reference_masses = []
    list_detected_peaks = []

    with open(template_file) as csv_template:
        csv_reader = csv.reader(csv_template, delimiter = delimiter)
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                pass
                
            else:
                name = row[0][:-2]

                retention_time_window = row[2]
                retention_time = rt_window_to_delta(retention_time_window)

                number_of_scans = row[3]

                quality = row[4]

                precursor_mz = row[5]

                precursor_i = row[6]

                noise_level = row[7]

                length_row = len(row)

                coelution_peaks = []
                start = False
                for i in range(length_row):

                    if start == True:
                        if row[i] == "massref" or row[i] == "picos_detectados":
                            break
                        elif row[i] != "":
                            coelution_peaks.append(float(row[i]))

                    if row[i] == "coelucion":
                        start = True

                reference_masses = []
                start = False
                for i in range(length_row):
                    
                    if start == True:
                        if row[i] == "coelucion" or row[i] == "picos_detectados":
                            break
                        elif row[i] != "":
                            reference_masses.append(float(row[i]))

                    if row[i] == "massref":
                        start = True

                detected_peaks = []
                start = False
                for i in range(length_row):

                    if start == True:
                        if row[i] == "coelucion" or row[i] == "massref":
                            break
                        elif row[i] != "":
                            detected_peaks.append(float(row[i]))
                    
                    if row[i] == "picos_detectados":
                        start = True

                print(line_count)
                print("NAME:", name)
                print("RETENTION_TIME:", retention_time[0]/60, "DELTA_RT:", retention_time[1]/60)
                print("NUMBER_OF_SCANS:", number_of_scans)
                print("QUALITY:", quality)
                print("MZ_PRECURSOR:", precursor_mz)
                print("MZ_INTENSITY:", precursor_i)
                print("NOISE LEVEL:", noise_level)
                print("COELUTION PEAKS", coelution_peaks)
                print("REFERENCE MASSES", reference_masses)
                print("DETECTED PEAKS", detected_peaks)
                print("")

                names.append(name)
                retention_times.append(retention_time)
                list_number_of_scans.append(number_of_scans)
                quality_list.append(quality)
                list_mz_precursor.append(precursor_mz)
                list_precursor_intensities.append(precursor_i)
                noise_level_list.append(noise_level)
                list_coelution_peaks.append(coelution_peaks)
                list_reference_masses.append(reference_masses)
                list_detected_peaks.append(detected_peaks)

            
            line_count += 1
            
    values_out = [names, retention_times, list_number_of_scans,
                quality_list, list_mz_precursor, list_precursor_intensities,
                noise_level_list, list_coelution_peaks, list_reference_masses,
                list_detected_peaks]
    
    return(values_out)



def main():

    # # Prueba de lectura del csv con el módulo csv
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")


    # with open("plantilla.csv") as csv_template:
    #     csv_reader = csv.reader(csv_template, delimiter = ",")
    #     line_count = 0
        
    #     for row in csv_reader:
    #         if line_count == 0:
    #             titles = row[:8]
                
    #         else:
    #             for title in titles:
    #                 print(title, end = " ")
    #             print()
    #             for column in row:
    #                 print(column, end = " ")
    #             print()

    #         line_count += 1

    
    # # Prueba de lectura del csv con el módulo pandas
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")

    # df_template = pd.read_csv("plantilla.csv")
    # print(df_template)

    # # Prueba de función read rt con pandas
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")
    # df_template = pd.read_csv("plantilla.csv")
    # read_mz_rt_template(df_template)

    # Prueba de función read rt con pandas
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    # open_template_instensity_distribution("plantilla.csv", path_in)


    # # Prueba open_template
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    # open_template("plantilla.csv", path_in)


    # # Prueba maximize
    path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    precision_list, recall_list, increase_list = maximize_precision("pos_neg_template.csv", path_in, 1, 50, 1)

    with open("precision.txt", "w") as f:
        f.write("Precision,Recall,Increase\n")
        for item in range(len(precision_list)):
            f.write(str(precision_list[item]) + "," + str(recall_list[item]) + "," + str(increase_list[item]) + "\n")

    # plt.plot(increase_list, precision_list)
    # plt.plot(increase_list, recall_list)
    # plt.legend(["Precision", "Recall"])
    # plt.show()
    
    # Prueba_1 Espectro MSMS_AFX7
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados"
    # open_template("plantilla.csv", path_in, increase = 5)

    # Prueba open template negative
    # path_in = "C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados_negativo"
    # list_of_values = open_negative_template("plantilla_negativo.csv", path_in)
    # for value in list_of_values:
    #     print(value)
    #     print("")


if __name__ == "__main__":
    main()