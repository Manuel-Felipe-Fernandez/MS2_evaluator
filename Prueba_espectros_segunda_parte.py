import Class_Spectrum_Model as csm
import os
import Class_parser as cp
import Grass_Functions as gf
import pyopenms as pyo

### Prueba de PLMild1ms, Bueno
def prueba(file_in, mz_in, rt_in):

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    file_to_parse = file_in

    spectra = cp.find_spectra_by_mz_and_rt(file_to_parse, mz_in, rt_in, delta_mz = 10, delta_rt = 12)
    
    spectra_found = 0
        
    for spectrum in spectra:

        spectra_found += 1
        peaks_spectrum = spectrum.get_peaks()
        count_peaks = 0

        print("Peak_mz", "Peak_i", sep="\t")

        for peak in peaks_spectrum:
            mz = peak.get_mz()
            i = peak.get_intensity()
            print (mz, i)
            count_peaks += 1
        

        print("Precursor_mz", "Precursor_i", sep="\t")
        num_precursor = len(spectrum.get_precursor_mz())

        for i in range(num_precursor):
            precursor_mz = spectrum.get_precursor_mz()[i]
            precursor_intensity = spectrum.get_precursor_intensity()[i]

            print(precursor_mz, precursor_intensity, sep="\t")


        print("Number of peaks:", count_peaks)
        print("Retention_time:", spectrum.get_retention_time(), " In minutes:", spectrum.get_retention_time()/60 )
    
    print("Number of spectra found:", spectra_found)
        




### Prueba de Active1msms, Malo, contaminado
def prueba_3():

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    file_to_parse = ""

    spect = cp.find_spectrum_by_mz_and_rt(file_to_parse, 540, 19.43*60, delta_rt = 2)
    

    try:
        peaks_spectrum = spect.get_peaks()

        print("Peak_mz", "Peak_i", sep="\t")

        for peak in peaks_spectrum:
            mz = peak.get_mz()
            i = peak.get_intensity()
            print (mz, i)
        

        print("Precursor_mz", "Precursor_i", sep="\t")
        num_precursor = len(spect.get_precursor_mz())

        for i in range(num_precursor):
            precursor_mz = spect.get_precursor_mz()[i]
            precursor_intensity = spect.get_precursor_intensity()[i]

            print(precursor_mz, precursor_intensity, sep="\t")
    
    except:
        print("No se encontraron espectros")

def prueba_size(file_in, mz_in, rt_in):

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Datos_anotados")
    file_to_parse = file_in

    spectra = cp.find_spectra_by_mz_and_rt(file_to_parse, mz_in, rt_in, delta_mz = 10, delta_rt = 12)
    
    spectra_found = 0
        
    for spectrum in spectra:

        size = spectrum.get_size()
        print(size)


def prueba_average_peaks(file_in, mz_in, rt_in):

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")

    spectra = cp.find_spectra_by_mz_and_rt(file_in, mz_in, rt_in, delta_mz = 0.0005, delta_rt = 6, delta_in_ppm = True)

    average_spectrum = cp.average_spectra(spectra, 0.01)
    list_into_experiment = list()
    list_into_experiment.append(average_spectrum)

    experiment = gf.list_of_Spectrum_object_to_MSExperiment(list_into_experiment)

    file_name_out = "average_" + "mz" + str(mz_in) + "rt_in" + str(rt_in) + file_in

    pyo.MzMLFile().store(file_name_out, experiment)



def prueba_average_peaks_con_filtro(file_in, mz_in, rt_in):

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    
    # para la prueba, rt era antes 6
    spectra = cp.find_spectra_by_mz_and_rt(file_in, mz_in, rt_in, delta_mz = 0.0005, delta_rt = 6, delta_in_ppm = True)

    cut_spectra = list()

    for spectrum in spectra:
        # Measure grass level
        begin = gf.be_measure_grass_level(spectrum, 20, 5)
        end = gf.end_measure_grass_level(spectrum, 20, 5)
        
        grass_level = (begin + end)/2

        # Cut spectrum
        cut_spectrum = gf.grass_cutter(spectrum, grass_level)
        cut_spectra.append(cut_spectrum)
        


    average_spectrum = cp.average_spectra(cut_spectra, 0.01)
    list_into_experiment = list()
    list_into_experiment.append(average_spectrum)

    experiment = gf.list_of_Spectrum_object_to_MSExperiment(list_into_experiment)

    file_name_out = "cut_average_" + "mz" + str(mz_in) + "rt_in" + str(rt_in)[:5] + file_in

    pyo.MzMLFile().store(file_name_out, experiment)
    


def main():
    # # prueba_1
    # prueba_size("Mild-1-PL-ms.mzML", 436, 20.96*60)
    # # prueba_2
    #     prueba("Severe-1-PL-ms.mzML", 540, 19.43*60)
    # ## prueba_3
    # #    prueba("Active-1msms.mzML", 298.63, 17.84*60)
    # # prueba_average_peaks
    # prueba_average_peaks("Mild-1-PL-ms.mzML", 436, 20.894*60)
    # # prueba_average_peaks_con_filtro
    # prueba_average_peaks_con_filtro("Mild-1-PL-ms.mzML", 436, 20.894*60)
    # prueba_nuevos
    prueba_size("MSMS_AFX3.mzML", 782.5682, 464.34)


main()

"""
Mild-1-PL-ms.mzML 436 20.96*60
Active-1msms.mzML
Control-1ms.mzML
Placebo-1msms.mzML
Severe-1-PL-ms.mzML
Severe-3-ms.mzML
"""