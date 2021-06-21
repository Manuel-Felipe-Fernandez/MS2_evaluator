import Class_Spectrum_Model as csm
import pyopenms as pyo
import Class_parser as cp
import matplotlib.pyplot as plt
import numpy as np
import os




def sorter(lists_in):
    """
    Function that sorts in reverse multiple lists
    """
    for l in lists_in:
        l.sort(reverse = True)
    
    return lists_in

def prueba(file_in, mz_in, rt_in):

    os.chdir("C:\\Users\\Manuel Fernández\\Desktop\\PAE\\Espectros_segunda_parte")
    file_to_parse = file_in

    intensity_lists = cp.find_intensity_distributions_by_mz_and_rt(file_to_parse, mz_in, rt_in, delta_mz = 10, delta_rt = 2)

    sorted_lists = sorter(intensity_lists)
    
    number_of_lists = len(sorted_lists)
    number_of_peaks = len(sorted_lists[0])

    print("Number of lists:", number_of_lists)
    print("Number of peaks:", number_of_peaks)
    
    return sorted_lists[0]
    


def main():

    mild = prueba("Mild-1-PL-ms.mzML", 436, 20.939*60)
    x1 = np.linspace(0, 1, len(mild))

    severe_1 = prueba("Severe-1-PL-ms.mzML", 540, 19.43*60)
    x2 = np.linspace(0, 1, len(severe_1))

    active = prueba("Active-1msms.mzML", 298.63, 17.84*60)
    x3 = np.linspace(0, 1, len(active))

    placebo = prueba("Placebo-1msms.mzML", 468.36, 19.04*60)
    x4 = np.linspace(0, 1, len(placebo))

    severe_3 = prueba("Severe-3-ms.mzML", 556.3247, 16.1276*60)
    x5 = np.linspace(0, 1, len(severe_3))

    control = ("Control-1ms.mzML", 507.216, 12.7437*60)
    x6 = np.linspace(0, 1, len(control))
    
    # plt.plot(x1, mild, label = "mild bueno")
    # plt.plot(x2, severe_1, label = "severe1 bueno")

    plt.plot(x3, active, label = "active malo")
    plt.plot(x4, placebo, label = "placebo malo")
    plt.plot(x5, severe_3, label = "severe3 regular")
    # plt.plot(x6, control, label = "control regular")

    

    plt.legend()
    plt.show()
main()
