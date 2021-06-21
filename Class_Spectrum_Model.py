#Class_Spectrum_Model

class Peak_object:
    """
    Object that represents a single peak in a spectrum.
    :param mz_in: mz of the peak to create
    :type: float
    :param intensity_in: intensity of the peak to create
    :type: float
    """
    def __init__(self, mz_in, intensity_in):

        if not isinstance(mz_in, (int,float)):
            raise TypeError("A value of mz in the peaks of the file is not a number")
        else:
            self._mz = mz_in

        if not isinstance(intensity_in, (int,float)):
            raise TypeError("A value of intensity in the peaks of the file is not a number")
        else:
            self._intensity = intensity_in

    
    def get_intensity(self):
        return self._intensity

    def get_mz(self):
        return self._mz
    
    def set_itensity(self, intensity_in):
        if not isinstance(intensity_in, (int,float)):
            raise TypeError("The value of intensity introduced is not a number")
        else:
            self._intensity = intensity_in

    def set_mz(self, mz_in):
        if not isinstance(mz_in, (int,float)):
            raise TypeError("The value of intensity introduced is not a number")
        else:
            self._mz = mz_in


class Spectrum_object:
    """
    Object that represents a single spectrum in an experiment.
    :param spectrum_in: list of peaks that represent a spectrum
    :type: list [Peak_object]
    :param spectrum_id: ID of the spectrum
    :type: str
    :param retention_time_in: Retention time of the spectrum in seconds
    :type: float 
    :param precursor_mz_in: list of mz of the precursor
    :type: list [float]
    :param precursor_intensity_MS1_in: list of intensities of the precursors
    :type: list [float]
    :param size: Number of peaks in the spectrum
    :type: positive int
    :param intensity_list: Intensities of the peaks
    :type: boolean
    """
    def __init__(self, spectrum_in, spectrum_id,  retention_time_in, precursor_mz_in, precursor_intensity_MS1_in = [1000],
                size = 0, intensity_list = False):

        self._spectrum = spectrum_in

        if not isinstance(spectrum_id, str):
            raise TypeError("The value of spectrum_id introudced is not an integer")
        else:
            self._spectrum_id = spectrum_id
        
        if not isinstance(retention_time_in, (int,float)):
            raise TypeError("The value of retention time introduced is not a number")
        else:
            self._retention_time = retention_time_in
        
        if not isinstance(precursor_mz_in, list):
            raise TypeError("The value of precursor mz introduced is not a list")
        else:
            for precursor_mz in precursor_mz_in:
                if not isinstance(precursor_mz, (int,float)):
                    raise TypeError("The value of precursor mz introduced is not a list of numbers")
            self._precursor_mz = precursor_mz_in

        if not isinstance(precursor_intensity_MS1_in, list):
            raise TypeError("The value of precursor intensity introduced is not a list")
        else:
            for precursor_intensity in precursor_intensity_MS1_in:
                if not isinstance(precursor_intensity, (int,float)):
                    raise TypeError("The value of precursor intensity introduced is not a list of numbers")
            self._precursor_intensity_MS1 = precursor_intensity_MS1_in

        if size == 0:
            self._size = len(spectrum_in)
        else:
            if not isinstance(size, (int,float)):
                raise TypeError("The value of size is not a number")
            else:
                self._size = size

        if intensity_list == False:
            self._intensity_list = 0
        elif not isinstance(intensity_list, list):
            raise TypeError("intensity_list introduced is not a list")
        else:
            intensity_list.sort(reverse = True)
            self._intensity_list = intensity_list


    def get_peaks(self):
        """
        Returns all the peaks in a list format
        """
        return self._spectrum

    def get_precursor_mz(self):
        """
        Returns the mz from all the precursors
        """
        return self._precursor_mz

    def get_precursor_intensity(self):
        """
        Returns the intensities from all the precursors
        """
        return self._precursor_intensity_MS1

    def get_retention_time(self):
        """
        Retruns the retention time from the spectrum
        """
        return self._retention_time

    def get_spectrum_id(self):
        """
        Retruns the spectrum_id from the spectrum
        """
        return self._spectrum_id

    def get_size(self):
        """
        Returns the number of peaks in the spectrum
        """
        return self._size

    def get_intensity_list(self):
        """
        Returns the ordered intensity of the peaks
        """
        return self._intensity_list
    
    def get_most_intense_peak(self, reference_mass_list = [], delta_mz = 0.01):
        """
        Gets the peak with greater intensity from the spectrum.
        Ignores all peaks with mz greater than precursor.
        Ignores peaks with mz equal to a mz of reference masses.
        :param reference_mass_list: list of mz of reference masses.
        :type: list [float]
        """

        precursor_mz = self.get_precursor_mz()[0]
        precursor_mz_upper = precursor_mz + delta_mz
        peaks = self.get_peaks()
        
        found_ref_mass = []
        max_peak = Peak_object(0,0)

        for peak in peaks:
            
            mz_peak = peak.get_mz()
            if mz_peak <= precursor_mz_upper:

                is_reference_mass = False

                for reference_mz in reference_mass_list:

                    mz_reference_lower = reference_mz - delta_mz
                    mz_reference_upper = reference_mz + delta_mz
                
                    if mz_reference_lower <= mz_peak and mz_reference_upper >= mz_peak:
                        
                        found_ref_mass.append(peak)
                        
                        is_reference_mass = True
                
                if is_reference_mass == False:

                    i_peak = peak.get_intensity()

                    if max_peak.get_intensity() < i_peak:

                        max_peak.set_mz(mz_peak)
                        max_peak.set_itensity(i_peak)

            else:
                break
            
        
        r_list = [max_peak, found_ref_mass]
        
        return(r_list)



    def set_peaks(self, spectrum_in):
        """
        Sets the peaks in the spectrum
        """
        self._spectrum = spectrum_in

    def sort_by_mz(self):
        """
        Sorts peak_objects in spectrum by mz
        """
        def key_for_sort(peak):
            mz = peak.get_mz()
            return (mz)

        peaks = self.get_peaks()
        peaks.sort(key = key_for_sort)

        self.set_peaks(peaks)

class Peak_object_trust(Peak_object):
    
    def __init__(self, mz_in, intensity_in, trust = 0):
        Peak_object.__init__(self, mz_in, intensity_in)

        if not isinstance(trust, (int, float)):
            raise TypeError("The value of trust is not a number")
        else:
            self._trust = trust
    
    def get_trust(self):
        """
        Retruns the trust of the peak
        """
        return self._trust

    def set_trust(self, trust):
        """
        Sets the trust of the peak
        """
        if not isinstance(trust, (int, float)):
            raise TypeError("The value of trust is not a number")
        else:
            self._trust = trust



def main():
    # Diagnostics of Class Peak
    peak = Peak_object_trust(129, 1111, 5)
    
    if peak.get_intensity() == 1111:
        print("Test intensity of peak is correct!")
    else:
        raise Exception("Test intensity of peak failed")

    if peak.get_mz() == 129:
        print("Test mz of peak is correct!")
    else:
        raise Exception("Test mz of peak failed")

    if peak.get_trust() == 5:
        peak.set_trust(6)
        if peak.get_trust() == 6:
            print("Test trust of peak is correct!")
        else:
            raise Exception("Test trust of peak failed")
    else:
        raise Exception("Test trust of peak failed")


if __name__ == "__main__":
    main()




    