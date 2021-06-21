import statistics
import pyopenms as pyo
import numpy as np
import Class_Spectrum_Model as csm
import os
import copy

def average_spectra_ordered(spectrum_list_in, delta_mz = 0.1, delta_in_ppm = False, ms1 = False):
    """
    Function that averages the peaks from the spectra given.
    :param spectrum_list_in: list of spectrum to average
    :type spectum_list_in: list of Spectrum_object
    :param delta_mz: delta mz to accept as the same peak
    :type delta_mz: float
    """
    count_spec = 1
    peaks_to_average = list()
    

    # Parameters for Spectrum_object creation
    spectrum_id = ""
    retention_time_list = []
    precursor_mz_list = []
    precursor_intensity_list = []

    for spectrum in spectrum_list_in:
        spectrum_id = spectrum_id + spectrum.get_spectrum_id()
        retention_time_list.append(spectrum.get_retention_time())

        if ms1 == False:
            precursor_mz_list.append(spectrum.get_precursor_mz()[0])
            precursor_intensity_list.append(spectrum.get_precursor_intensity()[0])

    retention_time_avg = statistics.mean(retention_time_list)
    
    if ms1 == False:

        precursor_mz_avg = [statistics.mode(precursor_mz_list)]
        precursor_intensity_avg = [statistics.mean(precursor_intensity_list)]

    else:

        precursor_mz_avg = []
        precursor_intensity_avg = []

    # Average_peaks
    for spectrum in spectrum_list_in:

        if count_spec == 1:

            peaks_to_average = spectrum.get_peaks()

        else:

            peaks = spectrum.get_peaks()

            pos_avg = 0
            pos_tmp = 0
            pos_peak = 0
            peaks_to_average_copy = copy.deepcopy(peaks_to_average)

            while pos_tmp < len(peaks_to_average_copy) and pos_peak < len(peaks):
                
                mz_tmp = peaks_to_average_copy[pos_tmp].get_mz()
                
                if delta_in_ppm == True:
                        delta_mz = mz_to_ppm(mz_tmp, delta_mz)

                mz_tmp_lower = mz_tmp - delta_mz
                mz_tmp_upper = mz_tmp + delta_mz

                peak = peaks[pos_peak]
                mz_peak = peak.get_mz()

                if mz_tmp_lower <= mz_peak and mz_tmp_upper >= mz_peak:
                    
                    i_peak = peak.get_intensity()
                    i_avg = peaks_to_average[pos_avg].get_intensity()
                    peaks_to_average[pos_avg].set_itensity(i_peak + i_avg)

                    pos_avg += 1
                    pos_tmp += 1
                    pos_peak += 1 
                
                if mz_tmp_lower > mz_peak:

                    peaks_to_average.insert(pos_avg, peak)
                    pos_avg += 1
                    pos_peak += 1

                if mz_tmp_upper < mz_peak:

                    pos_avg += 1
                    pos_tmp += 1

            if pos_peak < len(peaks):
                for peak in peaks[pos_peak:]:
                    peaks_to_average.append(peak)

        count_spec += 1

    intensity_list_parsed = []
    count_peaks = 0

    for peak in peaks_to_average:
        i = peak.get_intensity()
        i = i / count_spec
        peak.set_itensity(i)
        intensity_list_parsed.append(i)
        count_peaks += 1
    
    average_spectrum_out = csm.Spectrum_object(peaks_to_average, spectrum_id, retention_time_avg,
                                                precursor_mz_avg, precursor_intensity_avg, count_peaks,
                                                intensity_list_parsed)
    
    return(average_spectrum_out)


def find_intensity_distributions_by_mz_and_rt(file_in, mz_in, rt_in, delta_mz = 5, delta_rt = 10):
    """
    Finds intensity_distributions within spectfied m/z and retention time windows.
    :param file_in: input mzML experiment file that has the spectrum to parse
    :param mz_in: mass/charge value of the spectrum to find
    :type mz_in: float
    :param rt_in: retention time of the spectrum to find
    :type rt_in: float
    :param delta_mz: tolerance to find the mz_in in absolute value
    :type delta_mz: float
    :param delta_rt: tolerance to finde the rt_in in seconds
    :type delta_rt: float
    :return :list of parsed intensity_distributions
    :rtype :list of lists
    """
    exp = pyo.MSExperiment()
    
    if is_mzML(file_in):
        pyo.MzMLFile().load(file_in, exp)

    elif is_mzXML(file_in):
        pyo.MzXMLFile().load(file_in, exp)

    else:
        raise TypeError("The file inserted is not an mzML or mzXML file")

    mz_upper = mz_in + delta_mz
    mz_lower = mz_in - delta_mz

    rt_upper = rt_in + delta_rt
    rt_lower = rt_in - delta_rt

    spectrum_list = []

    for spectrum in exp:
        # AQUI BUSCO EN CADA ESPECTRO SI EL PRECURSOR ESTA DENTRO DE MZ +- delta_mz y RT_IN +- DELTA_RT
        ms_level = spectrum.getMSLevel()

        if ms_level > 1:
            precursor = spectrum.getPrecursors()
            precursor_mz = precursor[0].getMZ()
            spectrum_rt = spectrum.getRT()
            
            
            if precursor_mz > mz_lower and precursor_mz < mz_upper and spectrum_rt > rt_lower and spectrum_rt < rt_upper:
                parsed_spectrum = parser_spectrum(spectrum)
                spectrum_list.append(parsed_spectrum)
    
    return spectrum_list




def find_spectrum_by_spectrum_id(file_in, spectrum_to_parse):
    """
    Function that parses a spectrum from a given file onto a Spectrum_object
    
    """
    exp = pyo.MSExperiment()
    
    if is_mzML(file_in):
        pyo.MzMLFile().load(file_in, exp)

    elif is_mzXML(file_in):
        pyo.MzXMLFile().load(file_in, exp)

    else:
        raise TypeError("The file inserted is not an mzML or mzXML file")


    for spectrum in exp:
        scan_id = spectrum.getNativeID()[7:]
        
        if (scan_id == str(spectrum_to_parse)):
            
            return parser_spectrum(spectrum)


def find_spectrum_by_mz_and_rt(file_in, mz_in, rt_in, delta_mz = 5, delta_rt = 10):
    """
    Function that parses a single spectrum from a given file onto a Spectrum_object
    Finds the first spectrum within spectfied m/z and retention time windows.
    :param file_in: input mzML experiment file that has the spectrum to parse
    :param mz_in: mass/charge value of the spectrum to find
    :type float
    :param rt_in: retention time of the spectrum to find
    :type float
    :param delta_mz: tolerance to find the mz_in in absolute value
    :type float
    :param delta_rt: tolerance to finde the rt_in in seconds
    :type float
    """
    
    exp = pyo.MSExperiment()

    if is_mzML(file_in):
        pyo.MzMLFile().load(file_in, exp)

    elif is_mzXML(file_in):
        pyo.MzXMLFile().load(file_in, exp)

    else:
        raise TypeError("The file inserted is not an mzML or mzXML file")

    mz_upper = mz_in + delta_mz
    mz_lower = mz_in - delta_mz

    rt_upper = rt_in + delta_rt
    rt_lower = rt_in - delta_rt

    for spectrum in exp:
        # AQUI BUSCO EN CADA ESPECTRO SI EL PRECURSOR ESTA DENTRO DE MZ +- delta_mz y RT_IN +- DELTA_RT
        ms_level = spectrum.getMSLevel()

        if ms_level > 1:
            precursor = spectrum.getPrecursors()
            
            precursor_mz = precursor[0].getMZ()
            spectrum_rt = spectrum.getRT()
            
            
            if precursor_mz > mz_lower and precursor_mz < mz_upper and spectrum_rt > rt_lower and spectrum_rt < rt_upper:
                return parser_spectrum(spectrum)


def find_spectra_by_mz_and_rt(file_in, mz_in, rt_in, delta_mz = 5, delta_rt = 10, delta_in_ppm = False, ms_level_1 = False):
    """
    Function that parses spectra from a given file onto multiple Spectrum_object.
    Finds spectra within spectfied m/z and retention time windows.
    :param file_in: input mzML experiment file that has the spectrum to parse
    :param mz_in: mass/charge value of the spectrum to find
    :type mz_in: float
    :param rt_in: retention time of the spectrum to find
    :type rt_in: float
    :param delta_mz: tolerance to find the mz_in in absolute value
    :type delta_mz: float
    :param delta_rt: tolerance to finde the rt_in in seconds
    :type delta_rt: float
    :param delta_in_ppm: if true, delta_mz input in ppm
    :type delta_in_pp: boolean
    :param ms_level_1: if true, parses MS1. By default MS2 spectra are parsed
    :return :list of parsed spectrums
    :rtype :list of Spectrum_object
    """
    exp = pyo.MSExperiment()
    
    if is_mzML(file_in):
        pyo.MzMLFile().load(file_in, exp)

    elif is_mzXML(file_in):
        pyo.MzXMLFile().load(file_in, exp)

    else:
        raise TypeError("The file inserted is not an mzML or mzXML file")


    if delta_in_ppm == True:
        
        delta_mz_ppm = mz_to_ppm(mz_in, delta_mz)

        mz_upper = mz_in + delta_mz_ppm
        mz_lower = mz_in - delta_mz_ppm

    else:

        mz_upper = mz_in + delta_mz
        mz_lower = mz_in - delta_mz

    rt_upper = rt_in + delta_rt
    rt_lower = rt_in - delta_rt

    spectrum_list = []

    for spectrum in exp:
        # AQUI BUSCO EN CADA ESPECTRO SI EL PRECURSOR ESTA DENTRO DE MZ +- delta_mz y RT_IN +- DELTA_RT
        ms_level = spectrum.getMSLevel()

        if ms_level_1 == False:

            if ms_level == 2: 
                precursor = spectrum.getPrecursors()
                precursor_mz = precursor[0].getMZ()
                spectrum_rt = spectrum.getRT()
                
                
                if precursor_mz > mz_lower and precursor_mz < mz_upper and spectrum_rt > rt_lower and spectrum_rt < rt_upper:
                    parsed_spectrum = parser_spectrum(spectrum)
                    spectrum_list.append(parsed_spectrum)

        else:
            if ms_level == 1: 
                spectrum_rt = spectrum.getRT()
                
                
                if spectrum_rt > rt_lower and spectrum_rt < rt_upper:
                    parsed_spectrum = parser_spectrum(spectrum)
                    spectrum_list.append(parsed_spectrum)
            

    return spectrum_list

def average_spectra(spectrum_list_in, delta_mz = 0.1, delta_in_ppm = False):
    """
    Function that averages the peaks from the spectra given.
    :param spectrum_list_in: list of spectrum to average
    :type spectum_list_in: list of Spectrum_object
    :param delta_mz: delta mz to accept as the same peak
    :type delta_mz: float
    """
    count_spec = 1
    peaks_to_average = list()

    for spectrum in spectrum_list_in:

        if count_spec == 1:
            peaks_to_average = spectrum.get_peaks()

            # Parameters for Spectrum_object creation
            spectrum_id = spectrum.get_spectrum_id()
            retention_time = spectrum.get_retention_time()
            precursor_mz = spectrum.get_precursor_mz()
            precursor_intensity = spectrum.get_precursor_intensity()
            spectrum_size = spectrum.get_size()

        else:

            peaks = spectrum.get_peaks()
            
            for peak in peaks:
                mz = peak.get_mz()
                i = peak.get_intensity()
                found = False

                for peak_to_average in peaks_to_average:
                    mz_av = peak_to_average.get_mz()
                    i_av = peak_to_average.get_intensity()

                    if delta_in_ppm == True:
                        delta_mz = mz_to_ppm(mz_av, delta_mz)

                    mz_upper = mz_av + delta_mz
                    mz_lower = mz_av - delta_mz
                    # print(mz_upper, mz_lower)
                    if mz >= mz_lower and mz <= mz_upper:
                        i_av = i_av + i
                        peak_to_average.set_itensity(i_av)
                        found = True
                        break
                    
                if not found:
                    peak_to_add = csm.Peak_object(mz, i)

                    peaks_to_average.append(peak_to_add)

        count_spec += 1

    intensity_list_parsed = []
    count_peaks = 0

    for peak in peaks_to_average:
        i = peak.get_intensity()
        i = i / count_spec
        peak.set_itensity(i)
        intensity_list_parsed.append(i)
        count_peaks += 1
    
    average_spectrum_out = csm.Spectrum_object(peaks_to_average, spectrum_id, retention_time,
                                                precursor_mz, precursor_intensity, count_peaks,
                                                intensity_list_parsed)
    
    return(average_spectrum_out)


def parse_all_MS2(file_in):
    """
    Function that parses spectra from a given file onto multiple Spectrum_object.
    :return :list of parsed spectrums
    :rtype :list of Spectrum_object
    """
    exp = pyo.MSExperiment()
    
    if is_mzML(file_in):
        pyo.MzMLFile().load(file_in, exp)

    elif is_mzXML(file_in):
        pyo.MzXMLFile().load(file_in, exp)

    else:
        raise TypeError("The file inserted is not an mzML or mzXML file")

    spectrum_list = []

    for spectrum in exp:
        # AQUI BUSCO EN CADA ESPECTRO SI EL PRECURSOR ESTA DENTRO DE MZ +- delta_mz y RT_IN +- DELTA_RT
        ms_level = spectrum.getMSLevel()

        if ms_level > 1:
            
            parsed_spectrum = parser_spectrum(spectrum)
            spectrum_list.append(parsed_spectrum)
    
    return spectrum_list

def parser_spectrum(spectrum):
    """
    Function that parses a given spectrum onto a Spectrum_object.
    Returns parsed spectrum.
    :rtype Spectrum_object
    """
    spectrum_id = spectrum.getNativeID()
    spectrum_rt = spectrum.getRT()
    precursor = spectrum.getPrecursors()
    precursor_mz_list = []
    precursor_intensity_list = []

    for peak in precursor:
        peak_mz = peak.getMZ()
        peak_i = peak.getIntensity()

        precursor_mz_list.append(peak_mz)
        precursor_intensity_list.append(peak_i)
    
    peak_list = []
    intensity_list_parsed = []
    number_of_peaks = 0

    for peak in spectrum:
        mz = peak.getMZ()
        i = peak.getIntensity()

        peak_to_add = csm.Peak_object(mz, i)
        peak_list.append(peak_to_add)
        intensity_list_parsed.append(i)

        number_of_peaks += 1

    parsed_spectrum = csm.Spectrum_object(peak_list, spectrum_id, spectrum_rt, precursor_mz_list, precursor_intensity_list, number_of_peaks, intensity_list_parsed)

    return parsed_spectrum



def is_mzML(file_name):
    """
    Function that detects if file_name is mzML.
    Returns True if it is, False if not.
    """
    if file_name.endswith(".mzML"):
        return True
    else:
        return False


def is_mzXML(file_name):
    """
    Function that detects if file_name is mzML.
    Returns True if it is, False if not.
    """
    if file_name.endswith(".mzXML"):
        return True
    else:
        return False


def mz_to_ppm(mz_in, delta_in):
    """
    Function that transfers from mz to ppm.
    :param mz_in: mass/charge ratio to find the delta.
    :type mz_in: float
    :param delta_in: delta in mass/charge ratio to convert into ppm.
    :type mz_in: float
    :retuns: delta in ppm
    :rtype: float
    """

    ppm_out = (delta_in/mz_in)*(10**6)
    return(ppm_out)


def average_intensity(spectra):
    """
    Function that calculates the average intensity of the spectra given.
    Returns a single spectrum with the average intensity of the peaks.
    :param spectra: list of spectrum to do average
    :type spectra: list of Spectrum_object
    """
    
    peak_list_average = []

    for spectrum in spectra:
        peaks_spectrum = spectrum.get_peaks()
        for peak in peaks_spectrum:
            mz = peak.get_mz()
            i = peak.get_intensity()

            for peak_av in peak_list_average:
                mz_average = peak_av.get_mz()
                i_average = peak_av.get_intensity()
                # if 
    

    
##### Instrucciones:

# os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Spectra_examples\\20171013_FISmsms")
# file_to_parse = "MixPatronAV1.mzML"

###### Para parser por filtrado por id
# spect = find_spectrum_by_spectrum_id(file_to_parse, 796146)
# peaks_spectrum = spect.get_peaks()

# for peak in peaks_spectrum:
#     mz = peak.get_mz()
#     i = peak.get_intensity()
#     print (mz, i)

# print("Precursor_mz", "Precursor_i", sep="\t")
# num_precursor = len(spect.get_precursor_mz())

# for i in range(num_precursor):
#     precursor_mz = spect.get_precursor_mz()[i]
#     precursor_intensity = spect.get_precursor_intensity()[i]

#     print(precursor_mz, precursor_intensity, sep="\t")

###### Para parser por filtrado por ventana mz rt

# spect = find_spectrum_by_mz_and_rt(file_to_parse, 382.27, 793.2, delta_rt = 2)
# peaks_spectrum = spect.get_peaks()

# for peak in peaks_spectrum:
#     mz = peak.get_mz()
#     i = peak.get_intensity()
#     print (mz, i)

# print("Precursor_mz", "Precursor_i", sep="\t")
# num_precursor = len(spect.get_precursor_mz())

# for i in range(num_precursor):
#     precursor_mz = spect.get_precursor_mz()[i]
#     precursor_intensity = spect.get_precursor_intensity()[i]

#     print(precursor_mz, precursor_intensity, sep="\t")


# os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
# file_to_parse = "Mild-1-PL-ms.mzML"

# spect = find_spectrum_by_mz_and_rt(file_to_parse, 436, 20.96*60 , delta_rt = 2)
# peaks_spectrum = spect.get_peaks()

# print("Peak_mz", "Peak_i", sep="\t")

# for peak in peaks_spectrum:
#     mz = peak.get_mz()
#     i = peak.get_intensity()
#     print (mz, i)

# print("Precursor_mz-p", "Precursor_i", sep="\t")
# num_precursor = len(spect.get_precursor_mz())

# for i in range(num_precursor):
#     precursor_mz = spect.get_precursor_mz()[i]
#     precursor_intensity = spect.get_precursor_intensity()[i]

#     print(precursor_mz, precursor_intensity, sep="\t")
