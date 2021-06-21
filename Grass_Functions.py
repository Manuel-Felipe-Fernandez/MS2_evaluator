import pyopenms as pyo
import numpy as np
import Class_Spectrum_Model as csm
import os
import Class_parser as cp
import statistics

def lowest_measure_grass_level_stdev(spectrum, percentage = 20, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by measuring the median of the lowest peaks.
    """

    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    intensity_list = spectrum.get_intensity_list()[-number_of_peaks_to_choose:]
    
    median_peak = statistics.median(intensity_list)
    stdev = statistics.stdev(intensity_list)

    increased_stdev = stdev * increase
    increased_median = median_peak * increased_stdev

    return increased_median

def be_measure_grass_level_stdev(spectrum, percentage = 10, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by assuming the beginning as "noise".
    Calculates average intensity of the first peaks and sums it by the standard deviation (incremented)
    return: grass intensity
    rtype: float
    """
    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    peaks = spectrum.get_peaks()[:number_of_peaks_to_choose]

    peak_intensity_list = []
    for peak in peaks:
        peak_intensity_list.append(peak.get_intensity())
    
    i_average = statistics.mean(peak_intensity_list)
    stdev = statistics.stdev(peak_intensity_list)
    increased_stdev = stdev * increase

    i_increased = i_average + increased_stdev

    return i_increased


def end_measure_grass_level_stdev(spectrum, percentage = 10, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by assuming the end peaks as "noise".
    Calculates average intensity of the first peaks and sums it by the standard deviation (incremented)
    return: grass intensity
    rtype: float
    """
    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    peaks = spectrum.get_peaks()[-number_of_peaks_to_choose:]

    peak_intensity_list = []
    for peak in peaks:
        peak_intensity_list.append(peak.get_intensity())
    
    i_average = statistics.mean(peak_intensity_list)
    stdev = statistics.stdev(peak_intensity_list)
    increased_stdev = stdev * increase

    i_increased = i_average + increased_stdev

    return i_increased



def be_measure_grass_level(spectrum, percentage = 10, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by assuming the beginning as "noise".
    Calculates average intensity of the first peaks and multiplies it by increase.
    return: grass intensity
    rtype: float
    """
    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    peaks = spectrum.get_peaks()[:number_of_peaks_to_choose]
    i_sum = 0

    for peak in peaks:
        i_sum += peak.get_intensity()
    
    i_average = i_sum / number_of_peaks_to_choose
    i_increased = i_average * increase

    return i_increased


def be_measure_grass_level_max(spectrum, percentage = 10, increase = 1):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by assuming the beginning as "noise" .
    Calculates the maximum intensity of the first peaks and multiplies it by increase.
    return: grass intensity
    rtype: float
    """
    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    peaks = spectrum.get_peaks()[:number_of_peaks_to_choose]
    i_max = 0

    for peak in peaks:

        peak_intensity = peak.get_intensity()

        if peak_intensity > i_max:
            i_max = peak_intensity
    
    i_increased = i_max * increase
    
    return i_increased



def end_measure_grass_level(spectrum, percentage = 10, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by assuming the end peaks as "noise".
    Calculates average intensity of the first peaks and multiplies it by increase.
    return: grass intensity
    rtype: float
    """
    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    peaks = spectrum.get_peaks()[-number_of_peaks_to_choose:]
    i_sum = 0

    for peak in peaks:
        i_sum += peak.get_intensity()
    
    i_average = i_sum / number_of_peaks_to_choose
    i_increased = i_average * increase

    return i_increased


def lowest_measure_grass_level(spectrum, percentage = 20, increase = 5):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by measuring the median of the lowest peaks.
    """

    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    intensity_list = spectrum.get_intensity_list()

    if number_of_peaks_to_choose % 2 == 0:
        peak_1 = number_of_peaks_to_choose // 2
        peak_2 = peak_1 + 1
        median_peak = (intensity_list[-peak_1] + intensity_list[-peak_2]) / 2
    else:
        peak_1 = number_of_peaks_to_choose // 2
        median_peak = intensity_list[-peak_1]
    
    median_peak = statistics.median(intensity_list)

    increased_median = median_peak * increase

    return increased_median


def highest_measure_grass_level(spectrum, percentage = 5, increase = 1):
    """
    Function that measures grass level from a Spectrum_object.
    It measures grass by measuring the median of the highest peaks.
    """

    spectrum_size = spectrum.get_size()
    number_of_peaks_to_choose = round(spectrum_size * percentage / 100)

    intensity_list = spectrum.get_intensity_list()

    if number_of_peaks_to_choose % 2 == 0:
        peak_1 = number_of_peaks_to_choose // 2
        peak_2 = peak_1 + 1
        median_peak = (intensity_list[peak_1] + intensity_list[peak_2]) / 2
    else:
        peak_1 = number_of_peaks_to_choose // 2
        median_peak = intensity_list[peak_1]
    
    increased_median = median_peak / increase

    return increased_median
    

def grass_cutter(spectrum, grass_level):

    spectrum_id = spectrum.get_spectrum_id()
    precursor_mz_list = spectrum.get_precursor_mz()
    precursor_intensity_list = spectrum.get_precursor_intensity()
    spectrum_rt = spectrum.get_retention_time()
    intensity_list = spectrum.get_intensity_list()
    peaks = spectrum.get_peaks()
    peak_list = []
    number_of_peaks = 0

    for peak in peaks:

        intensity = peak.get_intensity()

        if intensity > grass_level:

            mz = peak.get_mz()
            peak_to_add = csm.Peak_object(mz, intensity)
            peak_list.append(peak_to_add)
            number_of_peaks += 1

    clean_spectrum = csm.Spectrum_object(peak_list, spectrum_id, spectrum_rt, precursor_mz_list, precursor_intensity_list, number_of_peaks, intensity_list)

    return clean_spectrum


def spectrum_object_to_MSSpectrum(spectrum):
    """
    Function that parses a Spectrum_object into a MSSpectrum object.
    return: parsed spectrum
    rtype: MSSpectrum
    """
    pyo_spectrum = pyo.MSSpectrum()

    retention_time_so = spectrum.get_retention_time()
    peaks_so = spectrum.get_peaks()
    spectrum_id = str(spectrum.get_spectrum_id())

    pyo_spectrum.setRT(retention_time_so)
    pyo_spectrum.setMSLevel(2)
    pyo_spectrum.setNativeID(spectrum_id)

    for peak in peaks_so:
        
        mz_so = peak.get_mz()
        intensity_so = peak.get_intensity()

        pyo_peak = pyo.Peak1D()
        pyo_peak.setMZ(mz_so)
        pyo_peak.setIntensity(intensity_so)
        pyo_spectrum.push_back(pyo_peak)

    return pyo_spectrum


def list_of_Spectrum_object_to_MSExperiment(spectra):
    """
    Function that parses a list of Spectrum_object into a MSExperiment.
    return: experiment
    rtype: MSExperiment
    """

    exp = pyo.MSExperiment()

    for spectrum in spectra:
        
        pyo_spectrum = spectrum_object_to_MSSpectrum(spectrum)
        exp.addSpectrum(pyo_spectrum)

    return exp
    
########################### Funciones de prueba ###############################################

def prueba_grass_cutter(file_to_parse, type_grass, mz_in, rt_in, type_file = "mzML"):
    """
    Prueba grass_cutter con be
    """

    spectra = cp.find_spectra_by_mz_and_rt(file_to_parse + "." + type_file, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    cut_spectra = []

    print("Grass cutter con", type_grass, "del espectro:", file_to_parse)

    for spectrum in spectra:

        print("Spectrum_id:", spectrum.get_spectrum_id())
        print("Spectrum_size:", spectrum.get_size())

        if type_grass == "be":
            grass_level = be_measure_grass_level(spectrum, 20, 5)
        elif type_grass == "be_max":
            grass_level = be_measure_grass_level_max(spectrum, 5)
        elif type_grass == "end":
            grass_level = end_measure_grass_level(spectrum, 20, 5)
        elif type_grass == "lowest":
            grass_level = lowest_measure_grass_level(spectrum, 20, 10)
        elif type_grass == "highest":
            grass_level = highest_measure_grass_level(spectrum, 1, 1)

        print("Grass_level_found:", grass_level)

        cut_spectrum = grass_cutter(spectrum, grass_level)
        print("Cut_Spectrum_size:", cut_spectrum.get_size())

        cut_spectra.append(cut_spectrum)


    experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    file_name_out = file_to_parse + "_cut_" + type_grass + "." + type_file

    pyo.MzMLFile().store(file_name_out, experiment)



def prueba_grass_cutter_all(file_to_parse, type_grass, type_file = "mzML"):
    """
    Prueba grass_cutter con be
    """

    spectra = cp.parse_all_MS2(file_to_parse + "." + type_file)

    cut_spectra = []

    print("Grass cutter con", type_grass, "del espectro:", file_to_parse)

    for spectrum in spectra:

        print("Spectrum_id:", spectrum.get_spectrum_id())
        print("Spectrum_size:", spectrum.get_size())

        if type_grass == "be":
            grass_level = be_measure_grass_level(spectrum, 20, 5)
        elif type_grass == "be_max":
            grass_level = be_measure_grass_level_max(spectrum, 5)
        elif type_grass == "end":
            grass_level = end_measure_grass_level(spectrum, 20, 5)
        elif type_grass == "lowest":
            grass_level = lowest_measure_grass_level(spectrum, 10, 10)
        elif type_grass == "highest":
            grass_level = highest_measure_grass_level(spectrum, 1, 1)

        print("Grass_level_found:", grass_level)

        cut_spectrum = grass_cutter(spectrum, grass_level)
        print("Cut_Spectrum_size:", cut_spectrum.get_size())

        cut_spectra.append(cut_spectrum)


    experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    file_name_out = file_to_parse + "_cut_" + type_grass + "." + type_file

    pyo.MzMLFile().store(file_name_out, experiment)


    







def main():
    # """
    # Prueba be_measure_grass_level
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    # file_to_parse = "Mild-1-PL-ms.mzML"
    # mz_in = 436
    # rt_in = 20.96*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse, mz_in, rt_in, delta_mz = 10, delta_rt = 12)
    
    # spectra_found = 0
        
    # for spectrum in spectra:

    #     size = spectrum.get_size()
    #     print(size)
        
    #     grass_intensity = be_measure_grass_level(spectrum)
    #     print(grass_intensity)

    # """
    # Prueba end_measure_grass_level
    # """
    
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    # file_to_parse = "Mild-1-PL-ms.mzML"
    # mz_in = 436
    # rt_in = 20.984*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse, mz_in, rt_in, delta_mz = 10, delta_rt = 2)
    
    # spectra_found = 0
        
    # for spectrum in spectra:

    #     size = spectrum.get_size()
    #     print(size)
        
    #     grass_intensity = end_measure_grass_level(spectrum)
    #     print(grass_intensity)

    # """
    # Pruebas de grass_cuter con diferentes funciones
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    # file_to_parse = "Mild-1-PL-ms"
    # mz_in = 436
    # rt_in = 20.984*60

    # lista_de_type_grass = ["be", "end", "be_max", "lowest", "highest"]

    # for funcion in lista_de_type_grass:
    #     prueba_grass_cutter(file_to_parse, funcion, mz_in, rt_in)


    """
    Pruebas de grass_cuter con diferentes funciones
    """
    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    file_to_parse = "Mild-1-PL-ms"

    list_filenames = ["Mild-1-PL-ms", "Severe-1-PL-ms", "Active-1msms", "Placebo-1msms", "Severe-3-ms", "Control-1ms"]
    list_type_grass = ["be", "end", "be_max", "lowest", "highest"]

    for file_to_parse in list_filenames:
        for function in list_type_grass:
            prueba_grass_cutter_all(file_to_parse, function) 


    # """
    # Prueba grass_cutter con end
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")


    # file_to_parse = "Mild-1-PL-ms"
    # type_file = ".mzML"
    # mz_in = 436
    # rt_in = 20.984*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse + type_file, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    # cut_spectra = []

    # print("Grass cutter con end promedio")

    # for spectrum in spectra:
    #     print("Spectrum_size:", spectrum.get_size())

    #     grass_level = end_measure_grass_level(spectrum, 20, 5)
    #     print("Grass_level_found:", grass_level)

    #     cut_spectrum = grass_cutter(spectrum, grass_level)
    #     print("Cut_Spectrum_size:", cut_spectrum.get_size())

    #     cut_spectra.append(cut_spectrum)

    # experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    # file_name_out = file_to_parse + "_cut_end" + type_file

    # pyo.MzMLFile().store(file_name_out, experiment)

    # """
    # Prueba grass_cutter con lowest_measure_grass_level median
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    # file_to_parse = "Mild-1-PL-ms"
    # type_file = ".mzML"
    # mz_in = 436
    # rt_in = 20.984*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse + type_file, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    # cut_spectra = []

    # print("Grass cutter con lowest median")

    # for spectrum in spectra:

    #     print("Spectrum_size:", spectrum.get_size())

    #     grass_level = lowest_measure_grass_level(spectrum, 20, 1)
    #     print("Grass_level_found:", grass_level)

    #     cut_spectrum = grass_cutter(spectrum, grass_level)
    #     print("Cut_Spectrum_size:", cut_spectrum.get_size())

    #     cut_spectra.append(cut_spectrum)

    # experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    # file_name_out = file_to_parse + "_cut_lowest" + type_file

    # pyo.MzMLFile().store(file_name_out, experiment)

    # """
    # Prueba grass_cutter con be max
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    # file_to_parse = "Mild-1-PL-ms"
    # type_file = ".mzML"
    # mz_in = 436
    # rt_in = 20.984*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse + type_file, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    # cut_spectra = []

    # print("Grass cutter con be max")

    # for spectrum in spectra:

    #     print("Spectrum_size:", spectrum.get_size())

    #     grass_level = be_measure_grass_level_max(spectrum, 5)
    #     print("Grass_level_found:", grass_level)

    #     cut_spectrum = grass_cutter(spectrum, grass_level)
    #     print("Cut_Spectrum_size:", cut_spectrum.get_size())

    #     cut_spectra.append(cut_spectrum)


    # experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    # file_name_out = file_to_parse + "_cut_be_max" + type_file

    # pyo.MzMLFile().store(file_name_out, experiment)


    # """
    # Prueba grass_cutter con highest_measure_grass_level median
    # """
    # os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    # file_to_parse = "Mild-1-PL-ms"
    # type_file = ".mzML"
    # mz_in = 436
    # rt_in = 20.984*60

    # spectra = cp.find_spectra_by_mz_and_rt(file_to_parse + type_file, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    # cut_spectra = []

    # print("Grass cutter con highest measure median")

    # for spectrum in spectra:

    #     print("Spectrum_size:", spectrum.get_size())

    #     grass_level = highest_measure_grass_level(spectrum, 1, 1)
    #     print("Grass_level_found:", grass_level)

    #     cut_spectrum = grass_cutter(spectrum, grass_level)
    #     print("Cut_Spectrum_size:", cut_spectrum.get_size())

    #     cut_spectra.append(cut_spectrum)

    # experiment = list_of_Spectrum_object_to_MSExperiment(cut_spectra)
    # file_name_out = file_to_parse + "_cut_highest" + type_file

    # pyo.MzMLFile().store(file_name_out, experiment)


if __name__ == "__main__":
    main()