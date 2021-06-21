import Class_Spectrum_Model as csm
import pyopenms as pyo
import Class_parser as cp
import matplotlib.pyplot as plt
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

    print(sorted_lists[0])
    print("Number of lists:", number_of_lists)
    
    plt.plot(sorted_lists[0])
    
    plt.show()

def main():

    # prueba("Mild-1-PL-ms.mzML", 436, 20.939*60)
    # prueba("Severe-1-PL-ms.mzML", 540, 19.43*60)
    # prueba("Active-1msms.mzML", 298.63, 17.84*60)
    # prueba("Placebo-1msms.mzML", 468.36, 19.04*60)
    # prueba("Severe-3-ms.mzML", 556.3247, 16.1276*60)
    prueba("Control-1ms.mzML", 507.216, 12.7437*60)
    
main()
