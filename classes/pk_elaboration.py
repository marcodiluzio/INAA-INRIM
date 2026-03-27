import os, pickle, datetime
import asyncio
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy.special import erfc
from scipy.integrate import quad

FWHMSIG = 1.665


class PeakFit:
    def __init__(self, Region):
        self.name = ''
        self.P0 = []
        self.BOUNDS = (None,None)
        self._PEAK = [1]
        self._BACKGROUND = 1

        self.coeff = [0]
        self.var_matrix = [0]
        self.infodict = {}
        self.mesg = ''
        self.intmsg = -1
        self._parameter_descriptor = ()

    def __repr__(self):
        return f'{self.name}'

    def _fit(self, x, *p):
        """placeholder"""
        return None
    
    def _draw_total(self, x):
        self._PEAK = [1] * len(self._PEAK)
        self._BACKGROUND = 1
        return self._fit(x, *self.coeff)
    
    def _draw_partials(self, x):
        if len(self._PEAK) > 1:
            self._BACKGROUND = 1

            fits = []
            for _idx in range(len(self._PEAK)):
                self._PEAK = [0] * len(self._PEAK)
                self._PEAK[_idx] = 1
                fits.append(self._fit(x, *self.coeff))
            return fits
        return []

    def _draw_background(self, x):
        self._PEAK = [0] * len(self._PEAK)
        self._BACKGROUND = 1
        return self._fit(x, *self.coeff)

    async def coro_evaluate(self, X, Y, Region):
        self.evaluate(X, Y, Region)
        return self

    def evaluate(self, X, Y, Region):
        try:
            self.coeff, self.var_matrix, self.infodict, self.mesg, self.intmsg = curve_fit(self._fit, X, Y, p0=self.P0, sigma=np.sqrt(Y),
                            bounds=self.BOUNDS, full_output=True,
                            absolute_sigma=True)
        except (ValueError, RuntimeError, RuntimeWarning):
            self.coeff, self.var_matrix, self.infodict, self.mesg, self.intmsg = [0.0], [0.0], {}, '', -1

        self.std_uncs, self.fvec, self.ssum, self.sqsum, self.chisq = self.metrics(X, Y)

        if self.intmsg != -1:
            self.centroids = self._get_centroids()#np.array(self.coeff[1:2]) #BIG POINT HERE self._get_centroids()
            self.ucentroids = self._get_ucentroids()#np.array(self.std_uncs[1:2]) #BIG POINT HERE self._get_ucentroids()
            self.pks, self.ur_pks = self._calulate_peak_area(Region) #IT'S GOOD

            print(self.centroids)
            print(self.pks)

        else:
            self.centroids, self.pks, self.ur_pks = np.array([0.0]), np.array([0.0]), np.array([0.0])

        self.output = self._get_output(Region.checks)

    def metrics(self, X, Y):
        std_uncs = np.sqrt(np.diag(self.var_matrix))
        fvec = self.infodict.get('fvec', None)

        if fvec is None:
            ssum = 9999
            sqsum = 9999
            stchis = 9999
        else:
            ssum = np.abs(np.sum(fvec))
            sqsum = np.sum(np.power(fvec, 2))
            res = Y - self._fit(X, *self.coeff)
            stchis = np.sum(np.power(res, 2)/Y) / (len(Y) - len(self.coeff))

        return std_uncs, fvec, ssum, sqsum, stchis

    def _get_output(self, Rdicts):
        output = True

        if np.all(self.pks < Rdicts['min_netarea']):
            self.intmsg = 9
            return None

        if np.all(self.ur_pks > Rdicts['max_allowed_unc']/100):
            self.intmsg = 10
            return None

        if np.any(np.isnan(self.ur_pks)):
            self.intmsg = 11
            return None

        if np.all(self.ucentroids > Rdicts['max_allowed_centroid_unc']):
            self.intmsg = 12
            return None
        
        if self.chisq > Rdicts['max_allowed_chisq']:
            self.intmsg = 13
            return None

        if self.intmsg in (-1, 9, 10, 11, 12, 13):
            output = None

        return output

    def _calulate_peak_area(self, Region):
        self._PEAK = [0] * len(self._PEAK)
        self._BACKGROUND = 0
        peakareas = []
        uncertainties = []
        
        for idx, npeak in enumerate(self.centroids):
            self._PEAK[idx] = 1
            area_calculation_results = quad(self._fit, Region.low_limit, Region.high_limit, args=tuple(self.coeff))
            peakareas.append(area_calculation_results[0])
            cs = []
            copycoeff = np.copy(self.coeff)
            for nn, value in enumerate(self.std_uncs):
                copycoeff[nn] = self.coeff[nn] + value
                Psl = quad(self._fit, Region.low_limit, Region.high_limit, args=tuple(copycoeff))
                copycoeff[nn] = self.coeff[nn] - value
                Msl = quad(self._fit, Region.low_limit, Region.high_limit, args=tuple(copycoeff))
                copycoeff[nn] = self.coeff[nn]
                cs.append((Psl[0] - Msl[0])/(2 * value + 1E-24))
            cs = np.array(cs)
            uncertainties.append(np.sqrt((cs.T@self.var_matrix)@cs))
            self._PEAK[idx] = 0
        peakareas = np.array(peakareas)
        rel_uncertainties = np.array(uncertainties) / peakareas
        return peakareas, rel_uncertainties

    def _get_peaklist_equivalent(self, en_cal, fwhm_cal):
        return [[cents, ucents, cents * en_cal[0] + en_cal[1], 0, area, urarea*area, np.sqrt(cents * fwhm_cal[0] + fwhm_cal[1]), np.nan] for cents, ucents, area, urarea in zip(self.centroids, self.ucentroids, self.pks, self.ur_pks)]
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        return True
    

class GaussianFit(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 1]        
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'background level')

    def _fit(self, x, *p):
        A, mu, sigma, BKG = p
        return (A*np.exp(-(x-mu)**2/(2.*sigma**2))) * self._PEAK[0] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])


class GaussianFitLS(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (LS), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'left skew amplitude', 'left skew slope', 'background level')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, LSAmp, LSSlop, BKG = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * LSAmp * np.exp((sigma/(2*LSSlop))**2+(x-mu)/LSSlop) * erfc(sigma/(2*LSSlop)+(x-mu)/sigma))) * self._PEAK[0] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if left_skew==False:
            return False
        return True


class GaussianFitRS(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (RS), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'right skew amplitude', 'right skew slope', 'background level')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, RSAmp, RSSlop, BKG = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * RSAmp * np.exp((sigma/(2*RSSlop))**2-(x-mu)/RSSlop) * erfc(sigma/(2*RSSlop)-(x-mu)/sigma))) * self._PEAK[0] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if right_skew==False:
            return False
        return True


class GaussianFitBS(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (RS LS), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 0, 0.15, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0, 0.1, 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, 0.75, 3, np.inf))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'left skew amplitude', 'left skew slope', 'right skew amplitude', 'right skew slope', 'background level')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, LSAmp, LSSlop, RSAmp, RSSlop, BKG = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * LSAmp * np.exp((sigma/(2*LSSlop))**2+(x-mu)/LSSlop) * erfc(sigma/(2*LSSlop)+(x-mu)/sigma) + spi * sigma * RSAmp * np.exp((sigma/(2*RSSlop))**2-(x-mu)/RSSlop) * erfc(sigma/(2*RSSlop)-(x-mu)/sigma))) * self._PEAK[0] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if left_skew==False or right_skew==False:
            return False
        return True


class GaussianFit_Slope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (), BKG (SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 1, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'background level', 'background slope')

    def _fit(self, x, *p):
        A, mu, sigma, BKG, slop = p
        return (A*np.exp(-(x-mu)**2/(2.*sigma**2))) * self._PEAK[0] + (BKG * (1 + slop*(x-mu))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if slope==False:
            return False
        return True


class GaussianFitLS_Slope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (LS), BKG (SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'left skew amplitude', 'left skew slope', 'background level', 'background slope')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, LSAmp, LSSlop, BKG, slop = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * LSAmp * np.exp((sigma/(2*LSSlop))**2+(x-mu)/LSSlop) * erfc(sigma/(2*LSSlop)+(x-mu)/sigma))) * self._PEAK[0] + (BKG * (1 + slop*(x-mu))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if left_skew==False or slope==False:
            return False
        return True


class GaussianFitRS_Slope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (RS), BKG (SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'right skew amplitude', 'right skew slope', 'background level', 'background slope')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, RSAmp, RSSlop, BKG, slop = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * RSAmp * np.exp((sigma/(2*RSSlop))**2-(x-mu)/RSSlop) * erfc(sigma/(2*RSSlop)-(x-mu)/sigma))) * self._PEAK[0] + (BKG * (1 + slop*(x-mu))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if right_skew==False or slope==False:
            return False
        return True


class GaussianFitBS_Slope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (RS LS), BKG (SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 0, 0.15, 1, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0, 0.1, 0.01, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, 0.75, 3, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'left skew amplitude', 'left skew slope', 'right skew amplitude', 'right skew slope', 'background level', 'background slope')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, LSAmp, LSSlop, RSAmp, RSSlop, BKG, slop = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * LSAmp * np.exp((sigma/(2*LSSlop))**2+(x-mu)/LSSlop) * erfc(sigma/(2*LSSlop)+(x-mu)/sigma) + spi * sigma * RSAmp * np.exp((sigma/(2*RSSlop))**2-(x-mu)/RSSlop) * erfc(sigma/(2*RSSlop)-(x-mu)/sigma))) * self._PEAK[0] + (BKG * (1 + slop*(x-mu))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if left_skew==False or right_skew==False or slope==False:
            return False
        return True


class GaussianFit_Step(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (), BKG (ST)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 1, 0.05]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01, 0), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'background level', 'background step')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, BKG, step = p
        return (A*np.exp(-(x-mu)**2/(2.*sigma**2))) * self._PEAK[0] + (BKG + A*spi*sigma*step*erfc((x-mu)/sigma)) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if step==False:
            return False
        return True


class GaussianFitLS_Step(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (LS), BKG (ST)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1, 0.05]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01, 0), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'left skew amplitude', 'left skew slope', 'background level', 'background step')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, LSAmp, LSSlop, BKG, step = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * LSAmp * np.exp((sigma/(2*LSSlop))**2+(x-mu)/LSSlop) * erfc(sigma/(2*LSSlop)+(x-mu)/sigma))) * self._PEAK[0] + (BKG + A*spi*sigma*step*erfc((x-mu)/sigma)) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if left_skew==False or step==False:
            return False
        return True


class GaussianFitRS_Step(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (RS), BKG (ST)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 0, 0.15, 1, 0.05]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0, 0.1, 0.01, 0), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, 0.75, 3, np.inf, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'right skew amplitude', 'right skew slope', 'background level', 'background step')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, RSAmp, RSSlop, BKG, step = p
        return (A*(np.exp(-(x-mu)**2/(2.*sigma**2)) + spi * sigma * RSAmp * np.exp((sigma/(2*RSSlop))**2-(x-mu)/RSSlop) * erfc(sigma/(2*RSSlop)-(x-mu)/sigma))) * self._PEAK[0] + (BKG + A*spi*sigma*step*erfc((x-mu)/sigma)) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if right_skew==False or step==False:
            return False
        return True


class GaussianFit_StepSlope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self.name = '1PEAK (), BKG (ST SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 1, 0.05, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01, 0, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, 1, 1))

        self._parameter_descriptor = ('peak height', 'centroid', 'sigma', 'background level', 'background step', 'background slope')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A, mu, sigma, BKG, step, slop = p
        return (A*np.exp(-(x-mu)**2/(2.*sigma**2))) * self._PEAK[0] + (BKG * (1 + slop*(x-mu)) + A*spi*sigma*step*erfc((x-mu)/sigma)) * self._BACKGROUND

    def _get_centroids(self):
        return np.array(self.coeff[1:2])

    def _get_ucentroids(self):
        return np.array(self.std_uncs[1:2])
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if slope==False or step==False:
            return False
        return True
    

class DoubleGaussianFit(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self._PEAK = [1, 1]

        self.name = '2PEAK (), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 100, Region.centroids[1], FWHM1/FWHMSIG, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[1] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[1] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf))

        self._parameter_descriptor = ('peak height (1)', 'centroid (1)', 'sigma (1)', 'peak height (2)', 'centroid (2)', 'sigma (2)', 'background level')

    def _fit(self, x, *p):
        A1, mu1, sigma1, A2, mu2, sigma2, BKG = p
        return (A1*np.exp(-(x-mu1)**2/(2.*sigma1**2))) * self._PEAK[0] + (A2*np.exp(-(x-mu2)**2/(2.*sigma2**2))) * self._PEAK[1] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array((self.coeff[1], self.coeff[4]), dtype=float)

    def _get_ucentroids(self):
        return np.array((self.std_uncs[1], self.std_uncs[4]), dtype=float)
    

class DoubleGaussianFit_Slope(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self._PEAK = [1, 1]

        self.name = '2PEAK (), BKG (SL)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 100, Region.centroids[1], FWHM1/FWHMSIG, 1, 0]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[1] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01, -1), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[1] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, 1))

        self._parameter_descriptor = ('peak height (1)', 'centroid (1)', 'sigma (1)', 'peak height (2)', 'centroid (2)', 'sigma (2)', 'background level', 'background slope')

    def _fit(self, x, *p):
        A1, mu1, sigma1, A2, mu2, sigma2, BKG, slop = p
        return (A1*np.exp(-(x-mu1)**2/(2.*sigma1**2))) * self._PEAK[0] + (A2*np.exp(-(x-mu2)**2/(2.*sigma2**2))) * self._PEAK[1] + (BKG * (1 + slop*(x-mu1))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array((self.coeff[1], self.coeff[4]), dtype=float)

    def _get_ucentroids(self):
        return np.array((self.std_uncs[1], self.std_uncs[4]), dtype=float)
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if slope==False:
            return False
        return True
    

class DoubleGaussianFit_Step(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self._PEAK = [1, 1]

        self.name = '2PEAK (), BKG (ST)'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 100, Region.centroids[1], FWHM1/FWHMSIG, 1, 0.05, 0.05]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[1] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01, 0, 0), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[1] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, 1, 1))

        self._parameter_descriptor = ('peak height (1)', 'centroid (1)', 'sigma (1)', 'peak height (2)', 'centroid (2)', 'sigma (2)', 'background level', 'background step (1)', 'background step (2)')

    def _fit(self, x, *p):
        spi = np.sqrt(np.pi)/2
        A1, mu1, sigma1, A2, mu2, sigma2, BKG, step1, step2 = p
        return (A1*np.exp(-(x-mu1)**2/(2.*sigma1**2))) * self._PEAK[0] + (A2*np.exp(-(x-mu2)**2/(2.*sigma2**2))) * self._PEAK[1] + (BKG * (1 + A1*spi*sigma1*step1*erfc((x-mu1)/sigma1) + A2*spi*sigma2*step2*erfc((x-mu2)/sigma2))) * self._BACKGROUND

    def _get_centroids(self):
        return np.array((self.coeff[1], self.coeff[4]), dtype=float)

    def _get_ucentroids(self):
        return np.array((self.std_uncs[1], self.std_uncs[4]), dtype=float)
    
    def _useit(self, left_skew=True, right_skew=True, slope=True, step=True):
        if step==False:
            return False
        return True


class TripleGaussianFit(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self._PEAK = [1, 1, 1]

        self.name = '3PEAK (), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 100, Region.centroids[1], FWHM1/FWHMSIG, 100, Region.centroids[2], FWHM1/FWHMSIG, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[1] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[2] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[1] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[2] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf))

        self._parameter_descriptor = ('peak height (1)', 'centroid (1)', 'sigma (1)', 'peak height (2)', 'centroid (2)', 'sigma (2)', 'peak height (3)', 'centroid (3)', 'sigma (3)', 'background level')

    def _fit(self, x, *p):
        A1, mu1, sigma1, A2, mu2, sigma2, A3, mu3, sigma3, BKG = p
        return (A1*np.exp(-(x-mu1)**2/(2.*sigma1**2))) * self._PEAK[0] + (A2*np.exp(-(x-mu2)**2/(2.*sigma2**2))) * self._PEAK[1] + (A3*np.exp(-(x-mu3)**2/(2.*sigma3**2))) * self._PEAK[2] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array((self.coeff[1], self.coeff[4], self.coeff[7]), dtype=float)

    def _get_ucentroids(self):
        return np.array((self.std_uncs[1], self.std_uncs[4], self.std_uncs[7]), dtype=float)
    

class QuadrupleGaussianFit(PeakFit):
    def __init__(self, Region, cal_fwhm, **kwargs):
        PeakFit.__init__(self, Region)

        self._PEAK = [1, 1, 1, 1]

        self.name = '4PEAK (), BKG ()'

        _cd = kwargs.get('bound_peak', 2)
        _fd = kwargs.get('bound_fwhm', 2)

        FWHM1 = np.sqrt(Region.centroids[0] * cal_fwhm[0] + cal_fwhm[1])
        self.P0 = [100, Region.centroids[0], FWHM1/FWHMSIG, 100, Region.centroids[1], FWHM1/FWHMSIG, 100, Region.centroids[2], FWHM1/FWHMSIG, 100, Region.centroids[3], FWHM1/FWHMSIG, 1]
        self.BOUNDS = ((5, Region.centroids[0] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[1] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[2] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 5, Region.centroids[3] - FWHM1/_cd, FWHM1/(_fd*FWHMSIG), 0.01), (np.inf, Region.centroids[0] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[1] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[2] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf, Region.centroids[3] + FWHM1/_cd, FWHM1*_fd/FWHMSIG, np.inf))

        self._parameter_descriptor = ('peak height (1)', 'centroid (1)', 'sigma (1)', 'peak height (2)', 'centroid (2)', 'sigma (2)', 'peak height (3)', 'centroid (3)', 'sigma (3)', 'peak height (4)', 'centroid (4)', 'sigma (4)', 'background level')

    def _fit(self, x, *p):
        A1, mu1, sigma1, A2, mu2, sigma2, A3, mu3, sigma3, A4, mu4, sigma4, BKG = p
        return (A1*np.exp(-(x-mu1)**2/(2.*sigma1**2))) * self._PEAK[0] + (A2*np.exp(-(x-mu2)**2/(2.*sigma2**2))) * self._PEAK[1] + (A3*np.exp(-(x-mu3)**2/(2.*sigma3**2))) * self._PEAK[2] + (A4*np.exp(-(x-mu4)**2/(2.*sigma4**2))) * self._PEAK[3] + (BKG) * self._BACKGROUND

    def _get_centroids(self):
        return np.array((self.coeff[1], self.coeff[4], self.coeff[7], self.coeff[10]), dtype=float)

    def _get_ucentroids(self):
        return np.array((self.std_uncs[1], self.std_uncs[4], self.std_uncs[7], self.std_uncs[10]), dtype=float)


class PreRegions:
    def __init__(self, spectrum_name, calname, regions):
        self.calname = calname
        self.data_reg = self._get_data_reg(regions)
        self._save(spectrum_name)

    def _get_data_reg(self, regions):
        return [(region.low_limit, region.high_limit, region.centroids) for region in regions]

    def _save(self, spectrum_name):
        path, filename = os.path.split(spectrum_name)
        fname, extension = os.path.splitext(filename)
        self.name = fname
        with open(os.path.join('data/presets', f'{fname}.reg'),'wb') as filesave:
            pickle.dump(self, filesave)


class Region:
    def __init__(self, low_limit, high_limit, centrs, min_netarea=100, max_allowed_unc=40, max_allowed_centroid_unc=2, max_allowed_chisq=5, left_skew=True, right_skew=True, slope=True, step=True):
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.centroids = centrs
        self._fits = []
        self.checks = {'min_netarea':min_netarea, 'max_allowed_unc':max_allowed_unc, 'max_allowed_centroid_unc':max_allowed_centroid_unc, 'max_allowed_chisq':max_allowed_chisq}
        self.peak_kwargs = {'left_skew':left_skew, 'right_skew':right_skew, 'slope':slope, 'step':step}
        self.fit = self._select_fit()

    def _update_peak_parameters(self, left_skew=None, right_skew=None, slope=None, step=None):
        _dict = {}
        ids = (('left_skew', left_skew), ('right_skew', right_skew), ('slope', slope), ('step', step))
        for (key, item) in ids:
            if item is not None:
                _dict[key] = item
        return _dict

    async def peak_elaboration(self, X, Y, fit_list):
        async with asyncio.TaskGroup() as taskgroup:
            collect = [taskgroup.create_task(_fit.coro_evaluate(X, Y, self)) for _fit in fit_list]
        return [task.result() for task in collect]

    def elaboration_fit(self, spectrum_profile, cal_fwhm, peak_opts={}, left_skew=None, right_skew=None, slope=None, step=None):
        self._delete_fits()
        X = np.arange(self.low_limit, self.high_limit+1)
        Y = spectrum_profile[X]

        kargs = self._update_peak_parameters(left_skew=left_skew, right_skew=right_skew, slope=slope, step=step)
        self.peak_kwargs = {**self.peak_kwargs, **kargs}

        singlepeak_fits = (GaussianFit, GaussianFit_Slope, GaussianFit_Step, GaussianFitLS, GaussianFitRS, GaussianFitBS, GaussianFitLS_Slope, GaussianFitRS_Slope, GaussianFitBS_Slope, GaussianFitLS_Step, GaussianFitRS_Step, GaussianFit_StepSlope)

        doublepeak_fits = (DoubleGaussianFit, DoubleGaussianFit_Slope, DoubleGaussianFit_Step)

        triplepeak_fits = (TripleGaussianFit, )

        quadruplepeak_fits = (QuadrupleGaussianFit, )

        if len(self.centroids) == 1:
            fit_list = [fit(self, cal_fwhm, **peak_opts) for fit in singlepeak_fits if fit._useit(fit, **self.peak_kwargs)==True]
            #(StudentFit(self, cal_fwhm), StudentFit_Step(self, cal_fwhm), StudentFitRS_Step(self, cal_fwhm), StudentFitLS_Step(self, cal_fwhm), StudentFitBS_Step(self, cal_fwhm))

        elif len(self.centroids) == 2:
            fit_list = [fit(self, cal_fwhm, **peak_opts) for fit in doublepeak_fits if fit._useit(fit, **self.peak_kwargs)==True]

        elif len(self.centroids) == 3:
            fit_list = [fit(self, cal_fwhm, **peak_opts) for fit in triplepeak_fits if fit._useit(fit, **self.peak_kwargs)==True]

        elif len(self.centroids) == 4:
            fit_list = [fit(self, cal_fwhm, **peak_opts) for fit in quadruplepeak_fits if fit._useit(fit, **self.peak_kwargs)==True]

        else:
            fit_list = []

        collect = asyncio.run(self.peak_elaboration(X, Y, fit_list))

        self._fits = sorted([item for item in collect if item.output == True], key=lambda x : np.abs(x.chisq - 1))
        self.fit = self._select_fit()

    def _delete_fits(self):
        flen = len(self._fits)
        for _nn in range(flen):
            self._fits.pop()

    def _select_fit(self, idx=0):
        try:
            return self._fits[idx]
        except IndexError:
            return None
        
    def _info(self):
        return {'low_limit':self.low_limit, 'high_limit':self.high_limit, 'centrs':self.centroids, 'min_netarea':self.checks['min_netarea'], 'max_allowed_unc':self.checks['max_allowed_unc'], 'max_allowed_centroid_unc':self.checks['max_allowed_centroid_unc'], 'max_allowed_chisq':self.checks['max_allowed_chisq'], 'left_skew':self.peak_kwargs['left_skew'], 'right_skew':self.peak_kwargs['right_skew'], 'slope':self.peak_kwargs['slope'], 'step':self.peak_kwargs['step']}


class Elaboration:
    def __init__(self, spectrum, calibration, K=3.5):
        self.spectrum_name, self.spectrum_profile = self._get_spectrum_information(spectrum)
        self.calname, self.cal_energy, self.cal_fwhm = self._get_calibration_information(calibration)
        self.K = K
        self.regions = []

        if self.spectrum_profile is None:
            raise ValueError

    def _limits(self, centroid):
        FWHM = np.sqrt(centroid * self.cal_fwhm[0] + self.cal_fwhm[1])
        low, high = int(np.floor(centroid - self.K * FWHM)), int(np.ceil(centroid + self.K * FWHM))
        if low < 0:
            low = 0
        if high > len(self.spectrum_profile) - 1:
            high = len(self.spectrum_profile) - 1
        return (low, high)

    def _get_energy(self, channel):
        return channel * self.cal_energy[0] + self.cal_energy[1]

    def _get_channel(self, energy):
        return (energy - self.cal_energy[1]) / self.cal_energy[0]

    def _delete_regions(self):
        for item in self.regions:
            self.regions.pop()

    def _order_regions(self):
        self.regions.sort(key=lambda x : x.low_limit)

    def _autoregion_search(self, energies=None, pregions=None, **kwargs):
        self._delete_regions()

        search_kwargs = {'height':kwargs['height'], 'threshold':kwargs['threshold'], 'distance':kwargs['distance'], 'min_prominence':kwargs['min_prominence'], 'wlen':kwargs['wlen'], 'rel_height':kwargs['rel_height'], 'plateau_size':kwargs['plateau_size'], 'E_min':kwargs['E_min'], 'E_max':kwargs['E_max']}

        reg_kwargs = {'min_netarea':kwargs['min_netarea'], 'max_allowed_unc':kwargs['max_allowed_unc'], 'max_allowed_centroid_unc':kwargs['max_allowed_centroid_unc'], 'max_allowed_chisq':kwargs['max_allowed_chisq'], 'left_skew':kwargs['left_skew'], 'right_skew':kwargs['right_skew'], 'slope':kwargs['slope'], 'step':kwargs['step']}

        if pregions is not None:
            for (_lowlim, _highlim, _centroids) in pregions.data_reg:
                if _highlim <= len(self.spectrum_profile):
                    self.regions.append(Region(_lowlim, _highlim, _centroids, **reg_kwargs))
            
        else:
            if energies is not None:
                centrs = [self._limits(pkc) for pkc in self._manual_search(energies, **search_kwargs)]
            else:
                centrs = [self._limits(pkc) for pkc in self._autocentroid_search(**search_kwargs)]

            vals = np.array([val[1] for val in centrs[:-1]]) > np.array([val[0] for val in centrs[1:]])
            vals = np.append(vals, np.array([False]))

            LK = kwargs['LK']
            if LK <= 0 or LK > self.K:
                LK = self.K

            _cents = np.array([val[0]/2 + val[1]/2 for val in centrs[:-1]])
            FWHM = np.sqrt(_cents * self.cal_fwhm[0] + self.cal_fwhm[1])
            cenvals = _cents + FWHM*LK > np.array([val[0]/2 + val[1]/2 for val in centrs[1:]])
            cenvals = np.append(cenvals, np.array([False]))

            vals = vals & cenvals

            start = 0
            for idx, (ctr, value) in enumerate(zip(centrs, vals)):
                if idx == start:
                    centroids = []
                    if value == False:
                        centroids.append(ctr[0]/2 + ctr[1]/2)
                        self.regions.append(Region(ctr[0], ctr[1], centroids, **reg_kwargs))
                        start += 1
                    else:
                        llmt = ctr[0]
                        final_index = np.where(vals[idx:] == False)[0][0]
                        centroids = [cix[0]/2 + cix[1]/2 for cix in centrs[idx : idx + final_index]]
                        self.regions.append(Region(llmt, centrs[idx + final_index][1], centroids, **reg_kwargs))
                        start = idx + final_index + 1

    def _get_spectrum_information(self, spectrum):
        return spectrum.filename(), spectrum.counts

    def _get_calibration_information(self, calibration):
        return calibration.name, calibration.energy_params, calibration.fwhm_params

    def _manual_search(self, energies, height=None, threshold=0.05, distance=4, min_prominence=2, wlen=10, rel_height=0.5, plateau_size=(1,2), E_min=None, E_max=None):
        chans = self._get_channel(energies)
        FWHM = np.sqrt(chans * self.cal_fwhm[0] + self.cal_fwhm[1])

        low_limits, high_limits = np.floor(chans - FWHM*self.K).astype(int, copy=True), np.ceil(chans + FWHM*self.K).astype(int, copy=True)

        opts = {'height':height, 'threshold':threshold, 'distance':distance, 'prominence':(min_prominence,None), 
                'width':(FWHM/2, FWHM*1.5), 'wlen':wlen, 'rel_height':rel_height, 'plateau_size':plateau_size}

        centroids = []

        for lidx, hlim in zip(low_limits, high_limits):
            if lidx >= 0 and hlim < len(self.spectrum_profile):
                partial_profile = self.spectrum_profile[lidx:hlim]
                xx = np.arange(len(partial_profile))
                FWHM = np.sqrt(xx * self.cal_fwhm[0] + self.cal_fwhm[1])
                opts['width'] = (FWHM/2, FWHM*1.5)
        
                centr, properties = find_peaks(partial_profile, **opts)
                centroids += list(centr + lidx)

        _centroids = np.sort(np.array(centroids), stable=True)

        if E_min is not None or E_max is not None:
            C1, C2 = self._calc_energy_limits(E_min, E_max)
            filt_CH = (C1 < _centroids) & (_centroids < C2)
            return _centroids[filt_CH]

        return _centroids
    
    def _calc_energy_limits(self, E_min, E_max):
        try:
            C1 = self._get_channel(E_min)
        except TypeError:
            C1 = 0
        
        try:
            C2 = self._get_channel(E_max)
        except TypeError:
            C2 = self._get_channel(len(self.spectrum_profile))
        
        if C2 > self._get_channel(len(self.spectrum_profile)):
            C2 = self._get_channel(len(self.spectrum_profile))

        if C2 > C1:
            return C1, C2
        return 0, self._get_channel(len(self.spectrum_profile))

    def _autocentroid_search(self, height=None, threshold=0.05, distance=4, min_prominence=2, wlen=10, rel_height=0.5, plateau_size=(1,2), E_min=None, E_max=None):

        xx = np.arange(len(self.spectrum_profile))
        FWHM = np.sqrt(xx * self.cal_fwhm[0] + self.cal_fwhm[1])

        opts = {'height':height, 'threshold':threshold, 'distance':distance, 'prominence':(min_prominence,None), 
                'width':(FWHM/2, FWHM*1.5), 'wlen':wlen, 'rel_height':rel_height, 'plateau_size':plateau_size}

        centroids, properties = find_peaks(self.spectrum_profile, **opts)

        if E_min is not None or E_max is not None:
            C1, C2 = self._calc_energy_limits(E_min, E_max)
            filt_CH = (C1 < centroids) & (centroids < C2)
            return centroids[filt_CH]

        return centroids

    def _get_peaklist(self):
        filtered_regions = [region.fit for region in self.regions if region.fit is not None]
        elaborated_peaklist = [line for item in filtered_regions for line in item._get_peaklist_equivalent(self.cal_energy, self.cal_fwhm)]
        #LIST OF LISTS
        #| POS | POS_UNC | E | E_UNC | AREA | AREA_UNC | FWHM | FWHM_UNC |
        # all floats, last np.nan
        return elaborated_peaklist
