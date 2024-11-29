# -*- coding: utf-8 -*-

"""
Classes to perform Neutron Analysis
"""

from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
import datetime
import itertools
import numpy as np
import pandas as pd
import scipy.stats as statistics
import xlrd
import csv
import os
import pickle
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

class Spectrum:
    """define a spectrum with all attached information."""
    def __init__(self,identity='Test',start_acquisition=datetime.datetime.today(),real_time=1000,live_time=999,peak_list=None,counts=None,path=None):
        self.identity = identity#Identity(Background,Comparator,Analytes) -> str
        self.datetime = start_acquisition#StartAcquisition -> datetime
        self.real_time = real_time#Real time -> float
        self.live_time = live_time#Live time -> float
        self.peak_list = peak_list#HyperLab_peaklist ->list
        self.counts = counts#spectrum -> np.array of ints
        self.spectrumpath = path
        self.assign_nuclide = None
        
    def deadtime(self,out='str'):
        try:
            deadtime=(self.real_time-self.live_time)/self.real_time
            deadtime=deadtime*100
            if out=='str':
                deadtime=str(deadtime.__round__(2))+' %'
        except:
            if out=='str':
                deadtime='Invalid'
            else:
                deadtime=None
        return deadtime
    
    def readable_datetime(self):
        return self.datetime.strftime("%d/%m/%Y %H:%M:%S")
    
    def number_of_channels(self):
        try:
            return len(self.counts)
        except:
            return 0
        
    def defined_spectrum_integral(self,start,width):
        if start>0 and start<len(self.counts) and start+width<len(self.counts):
            integr=0
            for i in range(width):
                integr += self.counts[start+i]
            return integr
        else:
            return None
        
    def define(self):
        return self.identity
    
    def filename(self):
        filename=str(self.spectrumpath)
        filename=str.split(filename,'/')
        return filename[-1]


class SpectrumAnalysis(Spectrum):
	"""Defines a spectrum class suitable for NAA analysis wich includes
	calibration and peak evaluation features."""
	def __init__(self,identity,start_acquisition,real_time,live_time,peak_list=None,counts=None,path='',prompt_peaksearch=True,prompt_peak_identification=False,source=None,sample=None,energy_tolerance=0.3,database=None,efficiency=None):
		Spectrum.__init__(self,identity,start_acquisition,real_time,live_time,peak_list,counts,path)
		#self.calibration = efficiency #maybe not necessary
		self.counting_position = self._set_default_counting_position(efficiency)#characterization
		self.positioning_variability = 0.0
		self.uncertainty_positioning_variability = 0.0
		self.k0_monitor_index = -1
		self.sample = sample

		if self.peak_list is None:
			self.peak_list = []

		self.suspected_peaks = None
		self.assigned_peaks = None
		if prompt_peaksearch:
			self.discriminate_peaks(database, energy_tolerance)
		if prompt_peak_identification:
			self.autoassignment_peaks()

	def _set_default_counting_position(self, efficiency):
		if efficiency is not None:
			return efficiency.reference_position
		else:
			return None

	def check_for_coincidence(self, energy, tolerance=0.3, comp_net_area=0.0): #moreoptions!
		peaks = np.array([peak[2] for peak in self.peak_list if peak[2] < energy])
		comp_count_rate = comp_net_area / self.live_time
		count_rates = np.array([peak[4]/self.live_time for peak in self.peak_list if peak[2] < energy])
		sumpeak = [result for result, crates in zip(itertools.combinations(peaks,2), itertools.combinations(count_rates,2)) if energy - tolerance < np.sum(result) < energy + tolerance and np.sum(crates) > comp_count_rate]
		return sumpeak
		
	def check_for_escapes(self, energy, tolerance=0.3, peakthreshold=0.0):
		peaks = np.array([peak[2] for peak in self.peak_list if peak[2] > energy and peak[2] > 1022 and peak[4] > peakthreshold])
		singleescape = [result for result in peaks if energy - tolerance < result - 511.0 < energy + tolerance]
		doubleescape = [result for result in peaks if energy - tolerance < result - 1022.0 < energy + tolerance]
		return singleescape, doubleescape

	def get_sample(self):
		if self.sample is not None:
			return self.sample
		return '-'

	def peak_intensity_check(self, count_rate_threshold=100):
		peaks = sorted([(peak[2], peak[4]/self.real_time) for peak in self.peak_list if peak[4]/self.real_time > count_rate_threshold], key=lambda x : x[1], reverse=True)
		if len(peaks) > 0:
			return '\n'.join([f'{item[0]:.0f} keV -> {item[1]:.1f} s⁻¹' for item in peaks])
		return f'found 0 peaks with count rate > {count_rate_threshold:.0f}'

	def peak_summary(self, n=5):
		peaks = sorted([peak[2:3]+peak[4:5] for peak in self.peak_list], key=lambda x : x[1], reverse=True)
		return len(peaks), ', '.join([f'{item[0]:.0f} keV' for item in peaks[:n]])

	def discriminate_peaks(self, database, tolerance=0.3):#in a good way
		if self.suspected_peaks is not None and self.assigned_peaks is not None:
			old_assignments = [sus[ass] if ass > -1 else None for ass, sus in zip(self.assigned_peaks, self.suspected_peaks)]
		else:
			old_assignments = None
		if database is not None:
			self.suspected_peaks = [self._emission_tuple(line[2], tolerance, database) for line in self.peak_list]
			if old_assignments is None:
				self.assigned_peaks = [-1 for line in self.peak_list]
			else:
				self.assigned_peaks = [self.check_line(line, suss) for line, suss in zip(old_assignments, self.suspected_peaks)]
		else:
			self.suspected_peaks = [() for line in self.peak_list]
			self.assigned_peaks = [-1 for line in self.peak_list]

	def autoassignment_peaks(self):
		for nn, suspt in enumerate(self.suspected_peaks):
			if len(suspt) == 1 and self.assigned_peaks[nn] != -2:
				self.assigned_peaks[nn] = 0

	def check_line(self, ass, sus):
		if ass is not None:
			try:
				return sus.index(ass)
			except (ValueError, AttributeError):
				return -1
		return -1

	def _emission_tuple(self, energy, energy_tolerance, database):
		#
		energy_filter = database['E'].between(energy - energy_tolerance,energy + energy_tolerance, inclusive=True)
		subdatabase = database[energy_filter]
		try:
			if self.identity == 'analysis spectrum':
				found = [Emission('k0', subdatabase.loc[line]) for line in subdatabase.index]
			else:
				found = [GSourceEmission('characterization', subdatabase.loc[line]) for line in subdatabase.index]
		except TypeError:
			found = []
		return tuple(found)
	
	def background_corrected_spectrum(self, background, lowchannelcompensation=False, averageof=5):
		if background is not None and self.number_of_channels() == background.number_of_channels():
			if not lowchannelcompensation:
				return self.counts - background.counts / background.live_time * self.live_time
			uncorrected_spectrum = self.counts - background.counts / background.live_time * self.live_time
			positive_mask = uncorrected_spectrum > 0
			start_index = np.where(uncorrected_spectrum > 0)[0][0]
			fillin = np.average(uncorrected_spectrum[positive_mask][:averageof])
			uncorrected_spectrum[:start_index] = fillin
			return uncorrected_spectrum
		return self.counts
	
	def short_report(self, eof_date=None, cunits={'decay time':'d', 'distance':'mm', 'ltime':'h'}, spaces={'sample':10, 'decay time':10, 'distance':10, 'ltime':10, 'dtime':12}, header=False):
		#sample | decay time | distance | live time | dead time
		units = {'h':3600, 'd':86400, 'min':60, 'cm':10, 'm':1000}
		H_sample = str.ljust('sample', spaces.get('sample', 10))
		_sample = str.ljust(self.sample, spaces.get('sample', 10))

		H_cooltime = str.rjust(f'td / {cunits.get("decay time", "s")}', spaces.get('decay time', 10))
		if eof_date is None:
			td_time = 0.0
		else:
			td_time = self.datetime - eof_date
			td_time = td_time.total_seconds() / units.get(cunits.get('decay time', 's'), 1)
		_cooltime = str.rjust(format(td_time, '.1f'), spaces.get('decay time', 10))

		H_distance = str.rjust(f'd / {cunits.get("distance", "mm")}', spaces.get('distance', 10))
		positx = self.counting_position / units.get(cunits.get('distance', 'mm'), 1)
		_distance = str.rjust(format(positx, '.1f'), spaces.get('distance', 10))

		H_ltime = str.rjust(f'tl / {cunits.get("ltime", "s")}', spaces.get('decay time', 10))
		live_time = self.live_time / units.get(cunits.get('ltime', 's'), 1)
		_ltime = str.rjust(format(live_time, '.2f'), spaces.get('ltime', 10))

		H_dedtime = str.rjust(f'tdead / 1', spaces.get('dtime', 10))
		_dedtime = str.rjust(self.deadtime(), spaces.get('dtime', 10))

		head = f"{H_sample}{H_cooltime}{H_distance}{H_ltime}{H_dedtime}\n"
		values = f"{_sample}{_cooltime}{_distance}{_ltime}{_dedtime}"

		if header:
			return head + values

		return values


class PTFit:
	def __init__(self, limit, parameters_L, cov_matrix_L, parameters_P, cov_matrix_P, esp_L=(1,0), esp_P=(2,1,0)):
		self.limit = limit
		self.esp_L = esp_L
		self.parameters_L = parameters_L
		self.cov_matrix_L = cov_matrix_L
		self.esp_P = esp_P
		self.parameters_P = parameters_P
		self.cov_matrix_P = cov_matrix_P

	def eval(self, E):
		E = np.array(E)
		if np.ndim(E) == 0:
			return self._eval_single(np.array([E]))
		return self._eval_array(E)
	
	def _eval_single(self, E):

		if E < self.limit:
			l_esp = self.esp_P
			l_parameters = self.parameters_P
			l_cov = self.cov_matrix_P
		else:
			l_esp = self.esp_L
			l_parameters = self.parameters_L
			l_cov = self.cov_matrix_L

		E = np.log10(E)

		W = E[:, np.newaxis]**l_esp
		value = float(l_parameters@W.T)

		sensitivity = []
		for nn, (xx, ux) in enumerate(zip(l_parameters, np.sqrt(np.diag(l_cov)))):
			mparms = np.copy(l_parameters)
			lparms = np.copy(l_parameters)
			mparms[nn] = xx + ux
			lparms[nn] = xx - ux
			sensitivity.append((float(np.exp(mparms@W.T)) - float(np.exp(lparms@W.T))) / (2 * ux + 1E-24))

		sensitivity = np.array(sensitivity)
		uncertainty = np.sqrt((sensitivity.T@l_cov)@sensitivity)

		runc = uncertainty / value

		return 10**value, 10**value * runc
	
	def _eval_array(self, E):
		energy_filter = E < self.limit
		E = np.log10(E)

		EE = E[energy_filter]
		W = EE[:, np.newaxis]**self.esp_P
		value_P = 10**(self.parameters_P@W.T)

		EE = E[~energy_filter]
		W = EE[:, np.newaxis]**self.esp_L
		value_L = 10**(self.parameters_L@W.T)

		value = np.concatenate((value_P, value_L))

		return value, np.nan
	
	def _showoff(self, space=10, cov=True):
		std_unc_P = np.sqrt(np.diag(self.cov_matrix_P))
		head_P = f'{str("x^").ljust(5)}{str("p").rjust(space)}{str("ur(p)").rjust(space)}'
		if cov:
			head_P += str('').rjust(space) + ''.join([f'{str(esp).rjust(space)}' for esp in self.esp_P])
		if cov:
			body_P = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}{str(esp).rjust(space)}{format(cov_m[0], ".2e").rjust(space)}{format(cov_m[1], ".2e").rjust(space)}{format(cov_m[2], ".2e").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp_P, self.parameters_P, self.cov_matrix_P, std_unc_P)])
		else:
			body_P = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp_P, self.parameters_P, self.cov_matrix_P, std_unc_P)])
		intermezzo = f'\n\ndiscontinuity: {self.limit} keV\n\n'
		std_unc_L = np.sqrt(np.diag(self.cov_matrix_L))
		head_L = f'{str("x^").ljust(5)}{str("p").rjust(space)}{str("ur(p)").rjust(space)}'
		if cov:
			head_L += str('').rjust(space) + ''.join([f'{str(esp).rjust(space)}' for esp in self.esp_L])
		if cov:
			body_L = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}{str(esp).rjust(space)}{format(cov_m[0], ".2e").rjust(space)}{format(cov_m[1], ".2e").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp_L, self.parameters_L, self.cov_matrix_L, std_unc_L)])
		else:
			body_L = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp_L, self.parameters_L, self.cov_matrix_L, std_unc_L)])
		
		return head_P + '\n' + body_P + intermezzo + head_L + '\n' + body_L


class SixParameterFix:
	def __init__(self, parameters, cov_matrix, esp=(1, 0, -1, -2, -3, -4)):
		self.esp = esp
		self.parameters = parameters
		self.cov_matrix = cov_matrix

	def eval(self, E):
		E = np.array(E) / 1000
		if np.ndim(E) == 0:
			return self._eval_single(np.array([E]))
		return self._eval_array(E)

	def _eval_single(self, E):
		W = E[:, np.newaxis]**self.esp
		value = float(np.exp(self.parameters@W.T))

		sensitivity = []
		for nn, (xx, ux) in enumerate(zip(self.parameters, np.sqrt(np.diag(self.cov_matrix)))):
			mparms = np.copy(self.parameters)
			lparms = np.copy(self.parameters)
			mparms[nn] = xx + ux
			lparms[nn] = xx - ux
			sensitivity.append((float(np.exp(mparms@W.T)) - float(np.exp(lparms@W.T))) / (2 * ux + 1E-24))

		sensitivity = np.array(sensitivity)
		uncertainty = np.sqrt((sensitivity.T@self.cov_matrix)@sensitivity)

		return value, uncertainty

	def _eval_array(self, E):
		W = E[:, np.newaxis]**self.esp
		return np.exp(self.parameters@W.T), np.nan
	
	def _div(self, Em, Ea):
		keDE, ukeDE = 1.0, 0.0
		Em = np.array([Em / 1000])
		Ea = np.array([Ea / 1000])
		W = Em[:, np.newaxis]**self.esp - Ea[:, np.newaxis]**self.esp
		keDE = float(np.exp(self.parameters@W.T))

		sensitivity = []
		for nn, (xx, ux) in enumerate(zip(self.parameters, np.sqrt(np.diag(self.cov_matrix)))):
			mparms = np.copy(self.parameters)
			lparms = np.copy(self.parameters)
			mparms[nn] = xx + ux
			lparms[nn] = xx - ux
			sensitivity.append((float(np.exp(mparms@W.T)) - float(np.exp(lparms@W.T))) / (2 * ux + 1E-24))

		sensitivity = np.array(sensitivity)
		ukeDE = np.sqrt((sensitivity.T@self.cov_matrix)@sensitivity)

		return keDE, ukeDE
	
	def _showoff(self, space=10, cov=True):
		std_unc = np.sqrt(np.diag(self.cov_matrix))
		head = f'{str("x^").ljust(5)}{str("p").rjust(space)}{str("ur(p)").rjust(space)}'
		if cov:
			head += str('').rjust(space) + ''.join([f'{str(esp).rjust(space)}' for esp in self.esp])
		if cov:
			body = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}{str(esp).rjust(space)}{format(cov_m[0], ".2e").rjust(space)}{format(cov_m[1], ".2e").rjust(space)}{format(cov_m[2], ".2e").rjust(space)}{format(cov_m[3], ".2e").rjust(space)}{format(cov_m[4], ".2e").rjust(space)}{format(cov_m[5], ".2e").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp, self.parameters, self.cov_matrix, std_unc)])
		else:
			body = "\n".join([f'{str(esp).ljust(5)}{format(param, ".2e").rjust(space)}{(format(np.abs(s_unc / param) *100, ".1f") + " %").rjust(space)}' for esp, param, cov_m, s_unc in zip(self.esp, self.parameters, self.cov_matrix, std_unc)])
		return head + '\n' + body


class d0SixParameterFix(SixParameterFix):
	def __init__(self, parameters, cov_matrix, esp=(1, 0, -1, -2, -3, -4)):
		super().__init__(parameters, cov_matrix, esp)

	def eval(self, E):
		E = np.array(E) / 1000
		if np.ndim(E) == 0:
			value, uncertainty = self._eval_single(np.array([E]))
		else:
			value, uncertainty = self._eval_array(E)
		return -value, uncertainty

	def _get_correlation(self, E1, E2, N=100):
		E1 = np.array([E1]) / 1000
		E2 = np.array([E2]) / 1000
		
		Sparam = np.stack([np.random.normal(param, uparam, N) for param, uparam in zip(self.parameters, np.sqrt(np.diag(self.cov_matrix)))], axis=-1)
		
		W1 = E1[:, np.newaxis]**self.esp
		W2 = E2[:, np.newaxis]**self.esp
		
		R1 = -np.exp(Sparam@W1.T)
		R2 = -np.exp(Sparam@W2.T)

		corr = np.corrcoef(R1.T, R2.T)
		return corr[0,1]


class DetectorCharacterization:
	def __init__(self, filename, detector, source, positions, background, results, udistances):
		self.name = filename
		self.detector = detector #detector class
		self.source = source
		self.background = background
		self.positions = positions

		self._manage_information(results)

		self.udistances = udistances
		
	def _manage_information(self, results):
		self.datetime = results['elaboration_day']

		self.reference_position = self.positions['reference'].fdistance()
		self.distances = tuple([float(kdd_key) for kdd_key in results['kdd_fits'].keys()])

		self.energy_params, self.energy_cov = results['energy characterization']
		self.fwhm_params, self.fwhm_cov = results['FWHM characterization']

		self.reference_curve = results['reference efficiency']

		self.DD_curves = results['kdd_fits']
		self.d0p_curves = results['d0p_fits']
		self.PT_curves = results['PT_fits']

		self.channel_data = results['channel_data']
		self.energy_data = results['energy_data']
		self.fwhm_data = results['fwhm_data']
		self.efficiency_data = results['eff_data']
		self.uefficiency_data = results['ueff_data']
		self.C_values_data = results['C_values']
		self.d0_values_data = results['d0_values']

	def create_report(self):
		return f"""Characterization: {self.name}
on detector: {self.detector.name} ({self.detector.relative_efficiency} % relative efficiency)
performed on: {self.datetime.strftime("%d/%m/%Y")}

reference position: {self.reference_position:.1f} mm"""
	
	def _get_COI_correction(self, coi_df, same_target, same_position, emission_standard, energy_standard, pos_standard, emission_sample, energy_sample, pos_sample, R=0.2):
		if same_target and same_position:
			return 1.0, 0.0
		COI_m, uCOI_m = self._get_COI_evaluation(coi_df, emission_standard, energy_standard, pos_standard, R)
		COI_a, uCOI_a = self._get_COI_evaluation(coi_df, emission_sample, energy_sample, pos_sample, R)

		rCOI = COI_m / COI_a
		urCOI = rCOI * np.sqrt(np.power(uCOI_m / COI_m, 2) + np.power(uCOI_a / COI_a, 2))

		if np.isnan(rCOI) or np.isnan(urCOI):
			return 1.0, 0.0
		return rCOI, urCOI

	def _get_COI_evaluation(self, coi_df, emit, energy, pos, R=0.2):
		filt_emission = coi_df['emitter'] == emit
		emitter_df = coi_df[filt_emission].copy(deep=True)
		emitter_df.set_index('line', drop=True, append=False, inplace=True, verify_integrity=False)

		filt_X = (float(energy) - 0.2 < emitter_df['E']) & (emitter_df['E'] < float(energy) + 0.2)
		try:
			Xindex = int(emitter_df[filt_X].index[0])
			scheme = emitter_df.loc[Xindex, 'type']
			emitter_df['ep'] = self._get_efficiency_point(emitter_df['E'], pos)
			emitter_df['et'] = self._get_PT_point(emitter_df['E'], emitter_df['ep'], pos)

			coincidences = scheme.split(' : ')
			corrections_loss = []
			corrections_sum = []
			for item in coincidences:
				if '-' in item:
					if '*' in item:
						nn, item = item.split('*')
						nn = int(nn)
						item = item.replace('(','').replace(')','')
						idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
						corrections_loss.append(nn * self.manage_losses(emitter_df, Xindex, idxs))
					else:
						idxs = [int(idx) if idx!='X' else idx for idx in item.split('-')]
						corrections_loss.append(self.manage_losses(emitter_df, Xindex, idxs))
				else:
					item = item.replace('=',' ').replace('+',' ')
					idxs = [int(idx) if idx!='X' else idx for idx in item.split()]
					corrections_sum.append(self.manage_sum(emitter_df, Xindex, idxs))
			coi = (1-np.sum(corrections_loss)) * (1+np.sum(corrections_sum))
			ucoi = coi * np.sqrt(np.power((np.sum(corrections_loss)*R)/(1-np.sum(corrections_loss)),2) + np.power((np.sum(corrections_sum)*R)/(1-np.sum(corrections_sum)),2))
		except IndexError:
			coi, ucoi = 1.0, 0.0
		return coi, ucoi
	
	def _get_energy_point(self, channel):
		return self.energy_params[0] * channel + self.energy_params[1]
	
	def pos_key(self, value):
		return f'{value:.1f}'
	
	def _get_keDEDD(self, pos_a, pos_m, E_a, E_m):
		keDE, ukeDE, keDD, ukeDD = 1.0, 0.0, 1.0, 0.0
		pos_a, pos_m = self.pos_key(pos_a), self.pos_key(pos_m)
		ks = self._get_keys()

		keDE, ukeDE = self.reference_curve._div(E_m, E_a)
		check_ref = self.pos_key(self.reference_position)

		#condition 1: monitor at reference, analyte elsewhere (except reference)
		if pos_m == check_ref and pos_a in ks:
			pos_curve = self.DD_curves.get(pos_a, None)
			if pos_curve is not None:
				keDD, ukeDD = pos_curve.eval(E_a)

		#condition 2: analyte at reference, monitor elsewhere (except reference)
		elif pos_a == check_ref and pos_m in ks:
			pos_curve = self.DD_curves.get(pos_m, None)
			if pos_curve is not None:
				keDD, ukeDD = pos_curve.eval(E_m)
				urkeDD = ukeDD / keDD
				keDD = 1 / keDD
				ukeDD = urkeDD * keDD

		#condition 3: monitor and analyte at reference
		elif pos_a == check_ref and pos_m == check_ref:
			keDD, ukeDD = 1.0, 0.0

		#condition 4bis: monitor and analyte not at reference (but same position)
		elif pos_a == pos_m and pos_m in ks:
			pos_curve = self.DD_curves.get(pos_m, None)
			if pos_curve is not None:
				keDD, ukeDD = pos_curve._div(E_m, E_a)

		#condition 4: monitor and analyte not at reference (but two different positions)
		else:
			pos1_curve = self.DD_curves.get(pos_a, None)
			pos2_curve = self.DD_curves.get(pos_m, None)
			if pos1_curve is not None and pos2_curve is not None:
				keDDa, ukeDDa = pos1_curve.eval(E_a)

				keDDm, ukeDDm = pos2_curve.eval(E_m)
				urkeDD = ukeDDm / keDDm
				keDDm = 1 / keDDm
				ukeDDm = urkeDD * keDDm

				keDD, ukeDD = keDDa * keDDm, keDDa * keDDm * np.sqrt(np.power(ukeDDa / keDDa, 2) + np.power(ukeDDm / keDDm, 2))

		return keDE, ukeDE, keDD, ukeDD
	
	def _get_d0primes(self, pos_a, pos_m, E_a, E_m):
		d0a, ud0a, d0m, ud0m, corr = 0.0, 0.0, 0.0, 0.0, 0
		pos_a, pos_m = self.pos_key(pos_a), self.pos_key(pos_m)
		ks = self._get_keys()

		#condition 1: d=d d'0=d'0 (full relative)
		if pos_m == pos_a and pos_a in ks:
			d0_curve = self.d0p_curves.get(pos_a, None)
			if d0_curve is not None:
				d0a, ud0a = d0_curve.eval(E_a)
				d0m, ud0m = d0_curve.eval(E_m)

				corr = d0_curve._get_correlation(E_a, E_m)

		#condition 2: analyte at reference, monitor elsewhere (except reference)
		elif pos_a in ks and pos_m in ks:
			d0a_curve = self.d0p_curves.get(pos_a, None)
			d0m_curve = self.d0p_curves.get(pos_m, None)
			if d0a_curve is not None:
				d0a, ud0a = d0a_curve.eval(E_a)
			if d0m_curve is not None:
				d0m, ud0m = d0m_curve.eval(E_m)

		return d0a, ud0a, d0m, ud0m, corr
	
	def _get_PT_point(self, energy, efficiency, position=None):
		kPT = 0.0
		if position is None:
			position = self.reference_position
		position_key = self.pos_key(position)

		PT_curve = self.PT_curves.get(position_key, None)
		if PT_curve is not None:
			kPT, _ = PT_curve.eval(energy)

		return efficiency / kPT

	def _get_efficiency_point(self, energy, position=None):
		keDE, keDd = 0.0, 0.0
		if position is None:
			position = self.reference_position
		position_key = self.pos_key(position)
		ks = self._get_keys()
		energy = np.array(energy) / 1000
		W = energy[:, np.newaxis]**self.reference_curve.esp
		keDE = np.exp(self.reference_curve.parameters@W.T)
		if position_key == self.pos_key(self.reference_position):
			keDd = 1.0
		elif position_key in ks:
			pos_curve = self.DD_curves.get(position_key, None)
			if pos_curve is not None:
				keDd, _ = pos_curve.eval(energy*1000)
		else:
			keDd = 0.0
		return keDE / keDd
	
	def manage_losses(self, emitter_df, Xindex, idxs):
		correction = 0.0
		if idxs.index('X') == 0:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_I(emitter_df, idxs, Xindex)
			F1 = aB*cB*etB+aB*aC*cC*etC+aB*aC*aD*cD*etD+aB*aC*aD*aE*cE*etE 
			F2 = aB*aC*cB*cC*etB*etC+aB*aC*aD*cB*cD*etB*etD+aB*aC*aD*aE*cB*cE*etB*etE+aB*aC*aD*cC*cD*etC*etD+aB*aC*aD*aE*cC*cE*etC*etE+aB*aC*aD*aE*cD*cE*etD*etE
			F3 = aB*aC*aD*cB*cC*cD*etB*etC*etD+aB*aC*aD*aE*cB*cC*cE*etB*etC*etE+aB*aC*aD*aE*cB*cD*cE*etB*etD*etE+aB*aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = aB*aC*aD*aE*cB*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 1:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_II(emitter_df, idxs, Xindex)
			F1 = gB/gA*aA*cA*etB+aC*cC*etC+aC*aD*cD*etD+aC*aD*aE*cE*etE
			F2 = gB/gA*aA*aC*cA*cC*etB*etC+gB/gA*aA*aC*aD*cA*cD*etB*etD+gB/gA*aA*aC*aD*aE*cA*cE*etB*etE+aC*aD*cC*cD*etC*etD+aC*aD*aE*cC*cE*etC*etE+aC*aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aA*aC*aD*cA*cC*cD*etB*etC*etD+gB/gA*aA*aC*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+aC*aD*aE*cC*cD*cE*etC*etD*etE
			F4 = gB/gA*aA*aC*aD*aE*cA*cC*cD*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 2:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_III(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aA*cA*etB+gC/gA*aA*cA*etC+aD*cD*etD+aD*aE*cE*etE
			F2 = gB/gA*aC*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+aD*aE*cD*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 3:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_IV(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aA*cA*etB+gC/gA*aD*aA*cA*etC+gD/gA*aA*cA*etD+aE*cE*etE
			F2 = gB/gA*aC*aD*aA*cC*cA*etB*etC+gB/gA*aC*aA*aD*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cA*cE*etB*etE+gC/gA*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aA*aC*aD*aE*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		elif idxs.index('X') == 4:
			aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE = self.loss_type_V(emitter_df, idxs, Xindex)
			F1 = gB/gA*aC*aD*aE*aA*cA*etB+gC/gA*aD*aE*aA*cA*etC+gD/gA*aE*aA*cA*etD+gE/gA*aA*cA*etE
			F2 = gB/gA*aC*aD*aE*aA*cE*cA*etB*etE+gB/gA*aC*aD*aE*aA*cA*cD*etB*etD+gB/gA*aC*aA*aD*aE*cC*cA*etB*etC+gC/gA*aE*aA*aD*cA*cD*etC*etD+gC/gA*aA*aD*aE*cA*cE*etC*etE+gD/gA*aA*aE*cA*cE*etD*etE
			F3 = gB/gA*aC*aE*aA*aD*cA*cC*cD*etB*etC*etD+gB/gA*aC*aA*aD*aE*cA*cC*cE*etB*etC*etE+gB/gA*aE*aA*aC*aD*cA*cD*cE*etB*etD*etE+gC/gA*aA*aD*aE*cA*cD*cE*etC*etD*etE
			F4 = gB/gA*aC*aA*aD*aE*cC*cD*cA*cE*etB*etC*etD*etE
			correction = F1 - F2 + F3 - F4
		return correction

	def loss_type_I(self, emitter_df, idxs, Xindex):
		# (*A-B-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_II(self, emitter_df, idxs, Xindex):
		# (B-*A-C-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 1:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_III(self, emitter_df, idxs, Xindex):
		# (B-C-*A-D-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 2:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_IV(self, emitter_df, idxs, Xindex):
		# (B-C-D-*A-E)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 3:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 4:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE

	def loss_type_V(self, emitter_df, idxs, Xindex):
		# (B-C-D-E-*A)
		aA, cA, gA, etA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, etB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, etC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, etD = 0.0, 0.0, 1.0 ,0.0
		aE, cE, gE, etE = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 4:
				aA, cA, gA, etA = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 0:
				aB, cB, gB, etB = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 1:
				aC, cC, gC, etC = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 2:
				aD, cD, gD, etD = emitter_df.loc[idx, ['a','c','g','et']]
			elif numcycle == 3:
				aE, cE, gE, etE = emitter_df.loc[idx, ['a','c','g','et']]
		return aA, cA, gA, etA, aB, cB, gB, etB, aC, cC, gC, etC, aD, cD, gD, etD, aE, cE, gE, etE


	def manage_sum(self, emitter_df, Xindex, idxs):
		correction = 0.0
		if len(idxs) == 3:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = self.sum_type_I(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*epB*epC/epA
		elif len(idxs) == 4:
			aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD = self.sum_type_II(emitter_df, idxs, Xindex)
			correction = gB/gA*aC*cC*aD*cD*epB*epC*epD/epA
		return correction

	def sum_type_I(self, emitter_df, idxs, Xindex):
		# (*A=B+C)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def sum_type_II(self, emitter_df, idxs, Xindex):
		# (*A=B+C+D)
		aA, cA, gA, epA = 0.0, 0.0, 1.0 ,0.0
		aB, cB, gB, epB = 0.0, 0.0, 1.0 ,0.0
		aC, cC, gC, epC = 0.0, 0.0, 1.0 ,0.0
		aD, cD, gD, epD = 0.0, 0.0, 1.0 ,0.0
		for numcycle, idx in enumerate(idxs):
			if idx == 'X':
				idx = Xindex
			if numcycle == 0:
				aA, cA, gA, epA = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 1:
				aB, cB, gB, epB = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 2:
				aC, cC, gC, epC = emitter_df.loc[idx, ['a','c','g','ep']]
			elif numcycle == 3:
				aD, cD, gD, epD = emitter_df.loc[idx, ['a','c','g','ep']]
		return aA, cA, gA, epA, aB, cB, gB, epB, aC, cC, gC, epC, aD, cD, gD, epD

	def _get_positions(self):
		dists = [dist for dist in self.distances] + [self.reference_position]
		dists.sort()
		return dists

	def _get_keys(self):
		keys = self._get_positions()
		return [f'{key:.1f}' for key in keys]

	def short_report(self):
		return f"""#########################
DETECTOR CHARACTERIZATION

Characterization: {self.name}
on detector: {self.detector.name} ({self.detector.relative_efficiency} % relative efficiency)
performed on: {self.datetime.strftime("%d/%m/%Y")}

reference position: {self.reference_position:.1f} mm
counting positions ({len(self._get_keys())}): ({", ".join(self._get_keys())})
"""

	def _save(self):
		with open(os.path.join(os.path.join('data', 'characterizations'), f'{self.name}.dcr'),'wb') as filesave:
			pickle.dump(self, filesave)


class Irradiation:
	def __init__(self, filename, irradiation_end, tirr, utirr, channelname, f, uf, a, ua, thermal, uthermal, epithermal, uepithermal, fast, ufast, irradiation_scheme):
		self.code = filename
		self.datetime = irradiation_end
		self.irradiation_time = tirr
		self.unc_irradiation_time = utirr
		self.channel_name = channelname
		self.f_value = f
		self.unc_f_value = uf
		self.a_value = a
		self.unc_a_value = ua
		self.thermal_flux = thermal
		self.unc_thermal_flux = uthermal
		self.epithermal_flux = epithermal
		self.unc_epithermal_flux = uepithermal
		self.fast_flux = fast
		self.unc_fast_flux = ufast
		self.irradiation_scheme = irradiation_scheme
		self.m_datetime = datetime.datetime.today()

	def _save(self):
		with open(os.path.join(os.path.join('data', 'irradiations'), f'{self.code}.irr'),'wb') as filesave:
			pickle.dump(self, filesave)

	def _to_dict(self):
		return {'m_datetime':self.m_datetime, 'datetime':self.datetime, 'channel_name':self.channel_name, 'f_value':self.f_value, 'unc_f_value':self.unc_f_value, 'a_value':self.a_value, 'unc_a_value':self.unc_a_value, 'thermal_flux':self.thermal_flux, 'unc_thermal_flux':self.unc_thermal_flux, 'epithermal_flux':self.epithermal_flux, 'unc_epithermal_flux':self.unc_epithermal_flux, 'fast_flux':self.fast_flux, 'unc_fast_flux':self.unc_fast_flux}
	
	def readable_datetime(self):
		return self.datetime.strftime("%d/%m/%Y %H:%M:%S")
	
	def istherescheme(self):
		if self.irradiation_scheme is not None:
			return True
		return False
	
	def short_report(self):
		return f"""###########
IRRADIATION

Irradiation code: {self.code}
facility: {self.channel_name}
end of irradiation date: {self.readable_datetime()}
irradiation time: {self.irradiation_time:.0f} s ({self.irradiation_time/3600:.2f} h)
irradiation scheme: {self.istherescheme()}
default values for f: {self.f_value:.2f}, a: {self.a_value:.3f}
"""


class BaseItemScheme:
	def __init__(self, code=None):
		self.code, self.role, self.type, self.height, self.uheight, self.s_height, self.s_uheight, self.loffset, self.uloffset = self._get_info(code)

	def _get_info(self, code):
		icode, irole, itype, s_height, s_uheight, loffset, uloffset = 'dummy', 'dummy', '-', 0.1, 0.0, 0.0, 0.0
		try:
			icode = code.name
			irole = code.sampletype
			itype = code.composition.ctype
			s_height, s_uheight = code.height, code.height_unc
			height, uheight = s_height + loffset, np.sqrt(np.power(s_uheight,2) + np.power(uloffset,2))
			return icode, irole, itype, height, uheight, s_height, s_uheight, loffset, uloffset
		except AttributeError:
			height, uheight = s_height + loffset, 0.1
			return icode, irole, itype, height, uheight, s_height, s_uheight, loffset, uloffset
		
	def __add__(self, other):
		return self.height + other.height
		
	def __sub__(self, other):
		return self.height - other.height


class IrradiationScheme:
	def __init__(self, samples_id=()):
		self.scheme = []
		self.initialize(samples_id)

	def initialize(self, samples_id=()):
		self.limits = {item.name : item.height for item in samples_id}
		self.roles = {item.name : item.sampletype for item in samples_id}
		self.samples_id = tuple(list(self.limits.keys()) + ['dummy'])
		self._compact_scheme()
		self.beta_list = {}
		
	def _compact_scheme(self):
		self.scheme = [self.approve(item) for item in self.scheme if self.ratify(item)]

	def ratify(self, item):
		if item.code in self.samples_id and item.role == self.roles.get(item.code, 'dummy'):
			return True
		return False

	def approve(self, item):
		item.s_height = self.limits.get(item.code, 0.1)

		if item.height < item.s_height + item.loffset:
			item.height = item.s_height + item.loffset
			item.uheight = 0.1

		return item
		
	def change_positions(self, n):
		self.scheme = self.define_positions(n)

	def standard_sample_distance(self, st_code, sm_code):
		starting_index, ending_index = -1, -1
		distance, udistance = 0.0, 0.0
		for nn, item in enumerate(self.scheme):
			if item.code == st_code:
				starting_index = nn
			elif item.code == sm_code:
				ending_index = nn

		if starting_index > -1 and ending_index > -1:
			if starting_index > ending_index:
				distance = sum([item.height for item in self.scheme[ending_index+1:starting_index+1]]) + self.scheme[ending_index].loffset + self.scheme[ending_index].s_height/2 - self.scheme[starting_index].loffset - self.scheme[starting_index].s_height/2
				udistance = np.sqrt(np.sum(np.power([item.uheight for item in self.scheme[ending_index+1:starting_index+1]] + [self.scheme[ending_index].uloffset, self.scheme[starting_index].uloffset, self.scheme[ending_index].s_height/2 * self.scheme[ending_index].s_uheight / self.scheme[ending_index].s_height], 2)))##########check udistance

			else:
				distance = -sum([item.height for item in self.scheme[starting_index+1:ending_index+1]]) + self.scheme[ending_index].loffset + self.scheme[ending_index].s_height/2 - self.scheme[starting_index].loffset - self.scheme[starting_index].s_height/2
				udistance = np.sqrt(np.sum(np.power([item.uheight for item in self.scheme[starting_index+1:ending_index+1]] + [self.scheme[ending_index].uloffset, self.scheme[starting_index].uloffset, self.scheme[ending_index].s_height/2 * self.scheme[ending_index].s_uheight / self.scheme[ending_index].s_height], 2)))##########check udistance

		return distance, udistance

	def _get_adjacent_standards(self, std, smp):
		smp_idx = 0
		std_idx = 0
		st_idxs = []
		for idx, item in enumerate(self.scheme):
			if item.code == smp:
				smp_idx = idx
			elif item.code == std:
				std_idx = idx
			elif item.role == 'standard':				
				st_idxs.append(idx)

		value_list = sorted(st_idxs, key=lambda x:abs(x-smp_idx))

		for item in value_list:
			if std_idx > smp_idx > item or std_idx < smp_idx < item:
				return self.scheme[item].code
		
		return ''

	def update_beta(self, beta, ubeta, code1, code2, target, emission, cpos):
		if not np.isnan(beta) and not np.isnan(ubeta):
			if (code1, code2, target, emission, cpos) in self.beta_list.keys():
				or_beta, or_ubeta = self.beta_list[(code1, code2, target, emission, cpos)]
				if np.abs(ubeta/beta) < np.abs(or_ubeta/or_beta):
					self.beta_list[(code1, code2, target, emission, cpos)] = (beta, ubeta)
			else:
				self.beta_list[(code1, code2, target, emission, cpos)] = (beta, ubeta)

	def get_beta_value(self, sample_id, standard_id, st_emission_line, cpos):
		default = (0.0, 0.0)
		
		if (sample_id, standard_id, st_emission_line.target, st_emission_line.emission, cpos) in self.beta_list.keys():
			return self.beta_list.get((sample_id, standard_id, st_emission_line.target, st_emission_line.emission, cpos), default)
		else:
			for key in self.beta_list.keys():
				if (key[0], key[1], key[2]) == (sample_id, standard_id, st_emission_line.target):
					return self.beta_list.get(key, default)
		return default

	def standard_distance(self):
		indexes, distances = [], []
		for nn, item in enumerate(self.scheme):
			if item.role == 'standard':
				indexes.append(nn)
		if len(indexes) > 1:
			for i,k in zip(indexes, indexes[1:]):
				distances.append(sum([item.height for item in self.scheme[i+1:k+1]]) + self.scheme[i].loffset - self.scheme[k].loffset)
			
		return indexes, distances
		
	def add_position(self, ItemScheme):
		codes = [item.code for item in self.scheme]
		if ItemScheme.code not in codes or ItemScheme.code == 'dummy':
			self.scheme.append(ItemScheme)
			text = 'item included in the irradiation scheme'
		else:
			text = 'this item is already present in the irradiation scheme'
		self._compact_scheme()
		return text
		
	def draw(self, canvas):
		self._compact_scheme()
		height, width = canvas.cget('height'), canvas.cget('width')
		start = 25
		textsize = 11
		dwidth = int(int(width) / 3)
		maxheight = int(height) - 2 * start
		space = int(start / 5) + start
		
		canvas.delete("all")
		
		heights = [item.height if item.height != 0 else 0.5 for item in self.scheme]
		try:
			k = maxheight / sum(heights)
		except ZeroDivisionError:
			k = 0
		textfont = ('TkMenuFont', -textsize)
		if len(heights) > 0:
			canvas.create_text(0, int(height) / 2 + 3*textsize, text=f'total height = {np.sum(heights):.1f} mm', anchor='nw', font=textfont, fill='black', angle=90)
		for item, lenght in zip(self.scheme, heights):
			if item.role == 'standard':
				opts = {'fill' : '#FFDB58', 'outline' : 'black'}
			elif item.role == 'sample':
				opts = {'fill' : '#89C35C', 'outline' : 'black'}
			else:
				opts = {'fill' : 'gray', 'outline' : 'black'}
			canvas.create_text(int(1.2 * space + dwidth), start + int((lenght * k) / 2) - int(textsize / 2), text=item.code, anchor='nw', font=textfont, fill='black')
			canvas.create_rectangle(space, start, space + dwidth, start + int(lenght * k), **opts)
			start += int(lenght * k)


class GammaSource:
	def __init__(self, filename):
		self.datetime, self.data = self._open_source(filename)
		self.name = os.path.splitext(filename)[0]
		self.selection = [True]*len(self.data)

	def readable_datetime(self):
		return self.datetime.strftime("%d/%m/%Y %H:%M:%S")

	def _open_source(self, filename):
		with open(os.path.join(os.path.join('data','sources'),f'{filename}'), 'r') as f:
			filelines = [line.replace('\n','') for line in f.readlines()]
		dtime = datetime.datetime.strptime(filelines[0], "%d/%m/%Y %H:%M:%S")
		filelines = [line.split() for line in filelines[1:]]
		datas = pd.DataFrame(filelines, columns=['energy','emitter','activity','u_activity','yield','u_yield','t_half','COIfree'])
		datas['activity'] = datas['activity'].astype(float)
		datas['u_activity'] = datas['u_activity'].astype(float)
		datas['yield'] = datas['yield'].astype(float)
		datas['u_yield'] = datas['u_yield'].astype(float)
		datas['t_half'] = datas['t_half'].astype(float)
		datas['COIfree'] = datas['COIfree'].astype(int).astype(bool)
		datas['lambda'] = np.log(2)/datas['t_half']
		datas['reference'] = [f'{energy} keV {emitter}' for energy, emitter in zip(datas['energy'], datas['emitter'])]
		return dtime, datas


class Detector:
	def __init__(self, filename):
		self.name = os.path.splitext(filename)[0]
		self.mu, self.u_mu, self.relative_efficiency, self.resolution, self.detector_type, self.diameter = self._open_source(filename)

	def _open_source(self, filename):
		mu, umu, relative_efficiency, FWHM, dtype, diameter = 0.0, 0.0, '0', '0', 'unknown', '0'
		with open(os.path.join(os.path.join('data','detectors'),f'{filename}'), 'r') as f:
			filelines = [line.replace('\n','') for line in f.readlines()]
		for line in filelines:
			label, value = line.split(' <#> ')
			if label == 'mu':
				xx, ux = value.split()
				mu, umu = float(xx), float(ux)
			elif label == 'refficiency':
				relative_efficiency = value
			elif label == 'FWHM':
				FWHM = value
			elif label == 'type':
				dtype = value
			elif label == 'diameter':
				diameter = value
		return mu, umu, relative_efficiency, FWHM, dtype, diameter


class Composition:
	"""
	Define composition for various sample or standard material types
	"""
	def __init__(self, ctype, masses=(), unc_masses=(), moistures=(), umoistures=(), samples=()):
		self.compositiontype = ctype #(multiple standard solution, flux monitor, single material)
		self.data = [(mass, umass, moisture, umoisture, sample) for mass, umass, moisture, umoisture, sample in zip(masses, unc_masses, moistures, umoistures, samples)]
		self._get_information()

	def _get_information(self):
		#calculate masses, moistures (with uncertainties) and a combined certificate dictionary containing the union of the elements 
		#present in all the single samples
		self.mass, self.umass, self.moisture, self.umoisture = self.get_total_masses()
		self.original_certificate = self.total_certificate()
		self.certificate = self.original_certificate.copy()
		#data integrity check?

	def _rezero(self):
		self.certificate = self.original_certificate.copy()

	def total_certificate(self):
		try:
			keys = sorted(set.union(*[set(item[4].certificate.keys()) for item in self.data]))
		except TypeError:
			keys = []
		if len(keys) > 0:
			masstrix = np.array([[item[0] * (1 - item[2]/100) * item[4].certificate.get(key, (0.0, 0.0))[0] for key in keys] for item in self.data])
			umasstrix = np.power(np.array([[item[0] * (1 - item[2]/100) * item[4].certificate.get(key, (0.0, 0.0))[1] for key in keys] for item in self.data]),2)
			masstrix, umasstrix = np.sum(masstrix.T, axis=1), np.sqrt(np.sum(umasstrix.T, axis=1))
			masstrix = masstrix / (self.mass * (1 - self.moisture / 100))
			umasstrix = umasstrix / (self.mass * (1 - self.moisture / 100))
			return {key : (value, uncertainty) for key, value, uncertainty in zip(keys, masstrix, umasstrix)}
		return {}
	
	def get_total_masses(self):
		mass, umass, moisture, umoisture = 0.0, 0.0, 0.0, 0.0
		for item in self.data:
			mass += item[0]
			umass += np.power(item[1],2)
			moisture += item[0] * item[2]/100
			try:
				umoisture += np.power(item[0] * item[2] * np.sqrt(np.power(item[1]/item[0],2) + np.power(item[3]/item[2], 2)), 2)
			except ZeroDivisionError:
				umoisture += 0
			
		umass, umoisture = np.sqrt(umass), np.sqrt(umoisture)
		try:
			umoisture = moisture/mass * np.sqrt(np.power(umoisture/moisture,2) + np.power(umass/mass,2))
		except ZeroDivisionError:
			umoisture = 0.0
		try:
			moisture = moisture/mass * 100
		except ZeroDivisionError:
			moisture = 0.0
		if np.isnan(umoisture):
			umoisture = 0.0
		return mass, umass, moisture, umoisture

	def isnan(self):
		if len(self.data) == 0:
			return True
		return False

	def isvoid(self):
		if len(self.data) == 0 or len(self.certificate) == 0:
			return True
		return False

	def add_information(self, masses=(), unc_masses=(), moistures=(), umoistures=(), samples=()):
		self.data += [(mass, umass, moisture, umoisture, sample) for mass, umass, moisture, umoisture, sample in zip(masses, unc_masses, moistures, umoistures, samples)]
		self._get_information()

	def get_information_text(self):
		if not self.isnan():
			return f'# mass: {self.mass:.3e} g\n# moisture: {self.moisture:.2f} %\n# material: {", ".join([item[4].name for item in self.data])}\n\n' + self.composition_triage()
		return 'composition is not defined'

	def composition_triage(self):

		def dispense(el_list):
			text = ", ".join(el_list)
			if len(text) > 0:
				return text
			return '-'

		major, traces, ultratraces = [], [], []
		for el in self.certificate:
			value = self.certificate.get(el, (np.nan, 0.0))[0]
			if 1 >= value > 0.009:
				major.append(el)
			elif value < 1.0E-6:
				ultratraces.append(el)
			elif not np.isnan(value):
				traces.append(el)

		return f'composition\n# major: {dispense(major)}\n# traces: {dispense(traces)}\n# ultratraces: {dispense(ultratraces)}'

	def _get_total_weightedmass(self, symbol=None, total=False):
		return np.sum([item[0] * self._get_element_massfraction(item[2], symbol, total) for item in self.data]), np.sqrt(np.sum([np.power(item[1],2) for item in self.data]))
	
	def _get_element_massfraction(self, item, symbol=None, total=False):
		if item.state == 'solution' and not total:
			default = 0.0
		else:
			default = 1.0
		return item.certificate.get(symbol, default)


class Material:
	"""
	Define macroscopic sample types to be irradiated
	"""
	def __init__(self, filename, folder=os.path.join('data','samples'),non_certified_uncertainty=20, old_sample=None):
		name, description, stype, physical_state, density, udensity, certificate, index = self._get_sample_information(filename,folder,non_certified_uncertainty,old_sample)
		self.name = name
		self.description = description.replace('\n','')
		self.sample_type = stype.replace('\n','')
		self.state = physical_state.replace('\n','')
		try:
			self.o_density = float(density.replace('\n',''))
		except (ValueError, TypeError):
			self.o_density = 1.0
		try:
			self.o_udensity = float(udensity.replace('\n',''))
		except (ValueError, TypeError):
			self.o_udensity = 0.0
		self.certificate = certificate
		self.non_certified = index

	def _to_csv(self):
		text = [f'{key},{item[0]},{item[1]}' for key,item in self.certificate.items() if key not in self.non_certified]
		text_non = [f'{key},{item[0]},{""}' for key,item in self.certificate.items() if key in self.non_certified]
		text += text_non
		return '\n'.join(text)

	def _get_sample_information(self, filename, folder, non_certified_uncertainty, old_sample=None):
		nfile = os.path.join(folder,filename)
		try:
			with open(nfile, 'r') as samplefile:
				description = samplefile.readline()
				stype = samplefile.readline()
				physical_state = samplefile.readline()
				density = samplefile.readline()
				udensity = samplefile.readline()
				elements = pd.read_csv(samplefile, header=None, names=['element','value','uncertainty'], index_col=0)
				index = list(elements['uncertainty'].index[elements['uncertainty'].isnull()])
				certificate = {key : self._fillna(key,elements.loc[key,'value'], elements.loc[key,'uncertainty'],non_certified_uncertainty,index) for key in elements.index}
				name = os.path.splitext(filename)[0]
		except FileNotFoundError:
			if old_sample is None:
				name, description, stype, physical_state, density, udensity, certificate, index = 'Unknown', '', 'unknown', 'unknown', '1.0', '0.0', {}, []
			else:
				name, description, stype, physical_state, density, udensity, certificate, index = old_sample.name, old_sample.description, old_sample.sample_type, old_sample.state, old_sample.o_density, old_sample.o_udensity, old_sample.certificate, old_sample.non_certified
		return name, description, stype, physical_state, density, udensity, certificate, index

	def _fillna(self, key, value, uncertainty, default, index):
		if key in index:
			if default is not None:
				return (value,value*default/100)
			else:
				return (value,np.nan)
		else:
			return (value,uncertainty)

	def _as_text_display(self, preamble='Elemental components of the sample listed in decreasing value of mass fraction, relative uncertainty (k=1) is reported while non certified values are indicated as "nan"\n\n', header=['El','x / g g⁻¹','urx / %'], unit=None, include_header=True):
		spaces = [4,11,11]
		if include_header:
			head = f'{header[0].ljust(spaces[0]," ")}{header[1].rjust(spaces[1]," ")}{header[2].rjust(spaces[2]," ")}\n'
		else:
			head = ''
		lines = sorted([(key,value[0],value[1]/value[0]) for key,value in self.certificate.items()], key=lambda x:x[1], reverse=True)
		if unit == 'ppm':
			astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1]*1000000,".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
			if include_header:
				header[1] = 'x / ppm'
		else:
			astext = '\n'.join([f'{line[0].ljust(spaces[0]," ")}{format(line[1],".3e").rjust(spaces[1]," ")}{format(line[2]*100,".1f").rjust(spaces[2]," ")}' for line in lines])
			if include_header:
				header[1] = 'x / g g⁻¹'
		return preamble+head+astext

	def _update_uncertainties(self, non_certified_uncertainty=20):
		certificate_updated = {key : (self.certificate[key][0], self.certificate[key][0]*non_certified_uncertainty/100) for key in self.non_certified}

		self.certificate = {**self.certificate, **certificate_updated}


class MeasurementSample:
	"""
	Define measurement sample
	"""
	def __init__(self, name, composition, sampletype, asCRMvariable, height, height_unc, diameter, diameter_unc, density, density_unc, ssh_database=None):
		self.name = name
		self.composition = composition#[]
		self.sampletype = sampletype #('sample', 'standard'), 'flux-monitor')
		self.asCRM = bool(asCRMvariable)

		self.height, self.height_unc = height, height_unc #mm
		self.diameter, self.diameter_unc = diameter, diameter_unc #mm

		self.density, self.density_unc = density, density_unc #g cm-3

		self.Gth, self.uGth = self._calculate_thermal_self_shielding(ssh_database)

		self.epi_shielding = self._calculate_epithermal_self_shielding(ssh_database)

	def _get_epithermal(self, target, emitter):
		g_target = self.epi_shielding.get(target, {})
		return g_target.get(f'{target}-{emitter}', (1.0, 0.0))

	def _calculate_epithermal_self_shielding(self, cross_section_df):
		if cross_section_df is not None and self.composition.certificate:
			return self.calculate_Ge(cross_section_df)
		return {}
	
	def calculate_Ge(self, cross_section_df):
		"""Calculate epithermal self shielding correction factor adopting Martinho universal curve for cylindrical samples"""
		Ge = {}
		master_plan = [(element, A) for element, A in zip(cross_section_df['element'], cross_section_df['A'])]
		for element_x in list(self.composition.certificate.keys()):
			submaster_plan = [item for item in master_plan if item[0] == element_x]
			for element, A in submaster_plan:
				Ge_M, uGe_M = self.MAR_cylinderE(self.diameter/20, self.diameter_unc/20, self.height/10, self.height_unc/10, self.composition.mass, self.composition.umass, self.composition.certificate, cross_section_df, element, A)
				values = Ge.get(element, {})
				values[f'{element}-{A}'] = (Ge_M, uGe_M)
				Ge[element] = values
		return Ge

	def _calculate_thermal_self_shielding(self, cross_section_df):
		"""Calculate thermal self shielding correction factor adopting Martinho universal curve for cylindrical samples"""
		if cross_section_df is not None and self.composition.certificate:
			radius, uradius, height, uheight = self.diameter/20, self.diameter_unc/20, self.height/10, self.height_unc/10
			return self.MAR_cylinder(radius, uradius, height, uheight, cross_section_df)
		return 1.0, 0.0
	
	def get_weighting_density(self, element=''):
		default, udefault = 1.0, 0.0
		if self.composition.compositiontype == 'single material':
			return self.density, self.density_unc
		else:
			for dataitem in self.composition.data:
				if element in dataitem[4].certificate:
					return dataitem[4].o_density, dataitem[4].o_udensity
		return default, udefault

	def _display_thermal_self_shielding_contributors(self, cross_section_df):
		elements = set(self.composition.certificate.keys())
		pp = np.array([self._MAR_sigma_function(cross_section_df, element) for element in elements])
		try:
			sumpp = np.sum(pp[:,0])
		except IndexError:
			sumpp = 1.0
		return {element : self._MAR_sigma_function(cross_section_df, element)[0]/sumpp for element in elements}

	def reduce_element_data(self, df, element):
		reduced = df['element'] == element
		reduced = df[reduced]
		SCATT = np.sum(reduced['scatt'] * reduced['abundance'])
		uSCATT = np.sqrt(np.sum(np.power(reduced['scatt'] * reduced['abundance'] * np.sqrt(np.power(reduced['uscatt'] / reduced['scatt'], 2) + np.power(reduced['uabundance'] / reduced['abundance'], 2)), 2)))
		ABSORPTION = np.sum(reduced['absorption'] * reduced['abundance'])
		uABSORPTION = np.sqrt(np.sum(np.power(reduced['absorption'] * reduced['abundance'] * np.sqrt(np.power(reduced['uabsorption'] / reduced['absorption'], 2) + np.power(reduced['uabundance'] / reduced['abundance'], 2)), 2)))
		M = np.sum(reduced['M'] * reduced['abundance'])
		uM = np.sqrt(np.sum(np.power(reduced['M'] * reduced['abundance'] * np.sqrt(np.power(reduced['uM'] / reduced['M'], 2) + np.power(reduced['uabundance'] / reduced['abundance'], 2)), 2)))
		TOTAL = SCATT + ABSORPTION
		uTOTAL = np.sqrt(np.power(uSCATT, 2) + np.power(uABSORPTION, 2))
		return SCATT, uSCATT, ABSORPTION, uABSORPTION, M, uM, TOTAL, uTOTAL

	def _MAR_sigma_function(self, cross_section_df, element):
		SCATT, uSCATT, ABSORPTION, uABSORPTION, M, uM, TOTAL, uTOTAL = self.reduce_element_data(cross_section_df, element)
		mf, umf = self.composition.certificate.get(element, (np.nan, np.nan))
		MS = (mf * TOTAL) / M * (ABSORPTION/TOTAL)**0.85
		if np.isnan(MS):
			MS = 0
		#uncertainty
		ux = np.array([umf, uM, uABSORPTION, uSCATT])
		sc0 = (((mf + ux[0]) * (SCATT + ABSORPTION)) / M * (ABSORPTION/(SCATT + ABSORPTION))**0.85 - ((mf - ux[0]) * (SCATT + ABSORPTION)) / M * (ABSORPTION/(SCATT + ABSORPTION))**0.85) / (2 * ux[0] + 1E-24)
		sc1 = ((mf * (SCATT + ABSORPTION)) / (M + ux[1]) * (ABSORPTION/(SCATT + ABSORPTION))**0.85 - (mf * (SCATT + ABSORPTION)) / (M - ux[1]) * (ABSORPTION/(SCATT + ABSORPTION))**0.85) / (2 * ux[1] + 1E-24)
		sc2 = ((mf * (SCATT + ABSORPTION + ux[2])) / M * ((ABSORPTION + ux[2])/(SCATT + ABSORPTION + ux[2]))**0.85 - (mf * (SCATT + ABSORPTION - ux[2])) / M * ((ABSORPTION - ux[2])/(SCATT + ABSORPTION - ux[2]))**0.85) / (2 * ux[2] + 1E-24)
		sc3 = ((mf * (SCATT + ABSORPTION + ux[3])) / M * (ABSORPTION/(SCATT + ABSORPTION + ux[3]))**0.85 - (mf * (SCATT + ABSORPTION - ux[3])) / M * (ABSORPTION/(SCATT + ABSORPTION - ux[3]))**0.85) / (2 * ux[3] + 1E-24)
		cs = np.array([sc0, sc1, sc2, sc3])
		uMS = np.sqrt(np.sum(np.power(ux * cs, 2)))
		if np.isnan(uMS):
			uMS = 0
		return MS, uMS

	def evaluate_macroscopic_crossesction(self, cross_section_df):
		elements = set(self.composition.certificate.keys())
		pp = np.array([self._MAR_sigma_function(cross_section_df, element) for element in elements])
		return np.sum(pp[:,0]), np.sqrt(np.sum(np.power(pp[:,1],2)))

	def MAR_z_cylinder(self, radius, uradius, height, uheight, cross_section_df):
		"""MXS = Macroscopic Cross-Section"""
		#Avogadro / mol-1
		NA = 6.022E23
		MXS, uMXS = self.evaluate_macroscopic_crossesction(cross_section_df)
		ux = np.array([uradius, uheight, self.composition.umass, uMXS])
		sc0 = ((1 / (np.pi * (radius + ux[0]) * ((radius + ux[0]) + height)) * self.composition.mass * NA * MXS) - (1 / (np.pi * (radius - ux[0]) * ((radius - ux[0]) + height)) * self.composition.mass * NA * MXS)) / (2 * ux[0] + 1E-24)
		sc1 = ((1 / (np.pi * radius * (radius + height + ux[1])) * self.composition.mass * NA * MXS) - (1 / (np.pi * radius * (radius + height - ux[1])) * self.composition.mass * NA * MXS)) / (2 * ux[1] + 1E-24)
		sc2 = ((1 / (np.pi * radius * (radius + height)) * (self.composition.mass + ux[2]) * NA * MXS) - (1 / (np.pi * radius * (radius + height)) * (self.composition.mass - ux[2]) * NA * MXS)) / (2 * ux[2] + 1E-24)
		sc3 = ((1 / (np.pi * radius * (radius + height)) * self.composition.mass * NA * (MXS + ux[3])) - (1 / (np.pi * radius * (radius + height)) * self.composition.mass * NA * (MXS - ux[3]))) / (2 * ux[3] + 1E-24)
		cs = np.array([sc0, sc1, sc2, sc3])
		return 1 / (np.pi * radius * (radius + height)) * self.composition.mass * NA * MXS, np.sqrt(np.sum(np.power(ux * cs, 2)))

	def MAR_cylinder(self, radius, uradius, height, uheight, cross_section_df):
		z0, uz0 = 0.635, 0.002
		p0, up0 = 1.061, 0.004
		Z, uZ = self.MAR_z_cylinder(radius, uradius, height, uheight, cross_section_df)
		ux = np.array([uZ, uz0, up0])
		cs0 = (1 / (1 + ((Z + ux[0]) / z0)**p0) - 1 / (1 + ((Z - ux[0]) / z0)**p0)) / (2 * ux[0] + 1E-24)
		cs1 = (1 / (1 + (Z / (z0 + ux[1]))**p0) - 1 / (1 + (Z / (z0 - ux[1]))**p0)) / (2 * ux[1] + 1E-24)
		cs2 = (1 / (1 + (Z / z0)**(p0 + ux[2])) - 1 / (1 + (Z / z0)**(p0 - ux[2]))) / (2 * ux[2] + 1E-24)
		cs = np.array([cs0, cs1, cs2])
		return 1 / (1 + (Z / z0)**p0), np.sqrt(np.sum(np.power(ux * cs, 2)))
	
	def MAR_cylinderE(self, radius, uradius, height, uheight, mass, umass, mass_fractions, cross_section_df, element, A):
		A1, uA1 = 1.000, 0.005
		A2, uA2 = 0.06, 0.0
		z0, uz0 = 2.70, 0.09
		p0, up0 = 0.82, 0.02
		Z, uZ = self.MAR_z_cylinderE(radius, uradius, height, uheight, mass, umass, mass_fractions, cross_section_df, element, A)
		ux = np.array([uA1, uA2, uz0, up0, uZ])
		cs0 = ((A1 + ux[0] - A2) / (1 + (Z / z0)**p0) - (A1 - ux[0] - A2) / (1 + (Z / z0)**p0)) / (2 * ux[0] + 1E-24)
		cs1 = ((A1 - A2 + ux[1]) / (1 + (Z / z0)**p0) - (A1 - A2 - ux[1]) / (1 + (Z / z0)**p0)) / (2 * ux[0] + 1E-24)
		cs2 = ((A1 - A2) / (1 + (Z / (z0 + ux[2]))**p0) - (A1 - A2) / (1 + (Z / (z0 - ux[2]))**p0)) / (2 * ux[0] + 1E-24)
		cs3 = ((A1 - A2) / (1 + (Z / z0)**(p0 + ux[3])) - (A1 - A2) / (1 + (Z / z0)**(p0 - ux[3]))) / (2 * ux[0] + 1E-24)
		cs4 = ((A1 - A2) / (1 + ((Z + ux[4]) / z0)**p0) - (A1 - A2) / (1 + ((Z - ux[4]) / z0)**p0)) / (2 * ux[0] + 1E-24)
		cs = np.array([cs0, cs1, cs2, cs3, cs4])
		return (A1 - A2) / (1 + (Z / z0)**p0) + A2, np.sqrt(np.sum(np.power(ux * cs, 2)))
	
	def MAR_z_cylinderE(self, radius, uradius, height, uheight, mass, umass, mass_fractions, cross_section_df, element, A):
		"""MXS = Macroscopic Cross-Section"""
		#Avogadro / mol-1
		NA = 6.022E23
		wi, uwi = mass_fractions.get(element, (0.0, 0.0))
		line = cross_section_df.loc[(cross_section_df['element'] == element) & (cross_section_df['A'] == A)]
		thi, uthi, M, uM = line.loc[line.index[0], 'abundance'], line.loc[line.index[0], 'uabundance'], line.loc[line.index[0], 'M'], line.loc[line.index[0], 'uM']
		SIGMARES, uSIGMARES, RES_G, uRES_G = line.loc[line.index[0], 'resonance'], line.loc[line.index[0], 'uresonance'], line.loc[line.index[0], 'Gamma_ratio'], line.loc[line.index[0], 'uGamma_ratio']
		SIGMARES, uSIGMARES = SIGMARES * 1E-24, uSIGMARES * 1E-24
		if np.isnan(SIGMARES) or np.isnan(RES_G):
			return 0.0, 0.0
		ux = np.array([uradius, uheight, umass, uwi, uthi, uSIGMARES, uRES_G])
		sc0 = ((1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + ux[0] + height) * np.pi * (radius + ux[0]) * M) - (1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius - ux[0] + height) * np.pi * (radius - ux[0]) * M)) / (2 * ux[0] + 1E-24)
		sc1 = ((1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height + ux[1]) * np.pi * radius * M) - (1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height - ux[1]) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		sc2 = ((1.65 * (mass + ux[2]) * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M) - (1.65 * (mass - ux[2]) * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		sc3 = ((1.65 * mass * NA * (wi + ux[3]) * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M) - (1.65 * mass * NA * (wi - ux[3]) * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		sc4 = ((1.65 * mass * NA * wi * (thi + ux[4]) * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M) - (1.65 * mass * NA * wi * (thi - ux[4]) * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		sc5 = ((1.65 * mass * NA * wi * thi * (SIGMARES + ux[5]) * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M) - (1.65 * mass * NA * wi * thi * (SIGMARES - ux[5]) * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		sc6 = ((1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt((RES_G + ux[6]))) / ((radius + height) * np.pi * radius * M) - (1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt((RES_G - ux[6]))) / ((radius + height) * np.pi * radius * M)) / (2 * ux[0] + 1E-24)
		cs = np.array([sc0, sc1, sc2, sc3, sc4, sc5, sc6])
		try:
			Z = (1.65 * mass * NA * wi * thi * SIGMARES * np.sqrt(RES_G)) / ((radius + height) * np.pi * radius * M)
		except ZeroDivisionError:
			return 0.0, 0.0
		return Z, np.sqrt(np.sum(np.power(ux * cs, 2)))


def _call_database(name, folder, des):
	path = os.path.join(os.path.join('data', folder), f'{name}.{des}')
	with open(path, 'rb') as database_file:
		return pickle.load(database_file)
	
def _indicize_code(budget, new_index):
	budget.code = f'{new_index}{budget.standard_code}_{budget.sample_code}_{budget.target}_{budget.emission.replace(" keV", "")}'
	return budget
	
def _call_results_and_indicize(path, idx):
	IDX = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	result_file = _call_results(path)
	result_file.results = [_indicize_code(item, IDX[idx]) for item in result_file.results]
	return result_file.results
	
def _call_results(path):
	with open(path, 'rb') as analysisresults_file:
		return pickle.load(analysisresults_file)

def nuclear_data():
	with open(os.path.join(os.path.join('data', 'nuclear_data'), 'nndc_nudat_data_export.nds'), 'rb') as database_file:
		return pickle.load(database_file)

def _save_naalysis_file(file, namefile):
	with open(namefile,'wb') as filesave:
		pickle.dump(file, filesave)

def _save_preset_datum(file, filename):
	with open(os.path.join(os.path.join('data', 'presets'), f'{filename}.pst'),'wb') as filesave:
		pickle.dump(file, filesave)

def _save_facility_database(file):
	with open(os.path.join(os.path.join('data', 'facilities'), 'channels.chs'),'wb') as filesave:
		pickle.dump(file, filesave)

def get_characterization(filename):
	with open(os.path(os.path.join('data', 'characterizations'), f'{filename}.dcr'), 'rb') as characterization_file:
		return pickle.load(characterization_file)

def _call_detection_characterizations(name=None):
	if name is not None and name.get() != '':
		return [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr') and get_characterization(filename).detector == name]
	return [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join('data', 'characterizations')) if filename.lower().endswith('.dcr')]


class RelAnalysis:
	def __init__(self, settings_dict):
		#settings read form settings_dict on initialization

		#get databases
		database_info = (('database', ('k0data', 'k0d')), ('cross_chem_data', ('chemical_data', 'mmd')), ('gabs_data', ('chemical_data', 'gbs')), ('coincidence_data', ('coincidences', 'coi')), ('yfiss_data', ('fission', 'fis')))
		database_info_line = database_info[0]
		self.k0_database = _call_database(settings_dict.get(database_info_line[0]), *database_info_line[1])
		database_info_line = database_info[1]
		self.abundances_database = _call_database(settings_dict.get(database_info_line[0]), *database_info_line[1])
		self._fill_uncertainty_df(settings_dict.get('literature cross section non certified uncertainties'))
		database_info_line = database_info[2]
		self.absorptions_database = _call_database(settings_dict.get(database_info_line[0]), *database_info_line[1])
		database_info_line = database_info[3]
		self.COI_database = _call_database(settings_dict.get(database_info_line[0]), *database_info_line[1])
		database_info_line = database_info[4]
		self.fiss_database = _call_database(settings_dict.get(database_info_line[0]), *database_info_line[1])

		#attributes
		self.analysis_name = 'new analysis'
		self.air_buoyancy = {'pressure':1020, 'u_pressure':10, 'relative humidity':60, 'u_relative humidity':10, 'temperature':20, 'u_temperature':1, 'steel':8.000, 'u_steel':0.001}
		self.irradiation = None
		self.characterization = None
		self.background_spectrum = None#
		self.blank_info = None#
		self.samples_id = []
		self.spectra = []
		self.pairings = []

	def _save(self, filename):
		with open(filename,'wb') as filesave:
			pickle.dump(self, filesave)

	def get_sample(self, code):
		codes = [item.name for item in self.samples_id]
		try:
			return self.samples_id[codes.index(code)]
		except ValueError:
			return None
		
	def get_sampletype(self, code):
		codes = {item.name : item.sampletype for item in self.samples_id}
		return codes.get(code, '-')
	
	def get_pair(self, code):
		default = None
		for item in self.pairings:
			if item[0] == code:
				return item[1]
		return default

	def _fill_uncertainty_df(self, fill_relative_uncertainty):
		filldf = pd.DataFrame()
		filldf['uscatt'] = self.abundances_database['scatt'] * fill_relative_uncertainty/100
		filldf['uabsorption'] = self.abundances_database['absorption'] * fill_relative_uncertainty/100
		self.abundances_database.fillna(filldf, inplace=True)


class Parameter:
	"""Base class for parameter in UncBudget"""
	def __init__(self, value=0.0, uncertainty=0.0, symbol=r'$x$', ddof=15):
		self.value = value
		self.uncertainty = uncertainty
		self.symbol = symbol
		self._dof = self._dof_rule(ddof)

	def get_value(self, increment=''):
		if increment == '+':
			return self.value + self.uncertainty
		elif increment == '-':
			return self.value - self.uncertainty
		return self.value
	
	def get_unc(self, k=1):
		return self.uncertainty * k
	
	def _dof_rule(self, dof):
		v_dof = {r'$n_\mathrm{p\:smp}$':30, r'$n_\mathrm{p\:std}$':30}
		return v_dof.get(self.symbol, dof)


class PartialBudget:
	"""Base class for unitary uncertainy budgets to be used in UncBudget"""
	def __init__(self):
		self.correlations = {}
		self.parameters = []

	def get_covariance_matrix(self):
		data = np.array([item.get_unc() for item in self.parameters])
		cov_matrix = np.identity(len(data))
		for key, value in self.correlations.items():
			if key[0] != key[1]:
				cov_matrix[key[0], key[1]] = value
				cov_matrix[key[1], key[0]] = value
		return np.outer(data, data) * cov_matrix

	def _corr_matrix(self):
		cov_matrix = np.identity(len(self.parameters))
		for key, value in self.correlations.items():
			if key[0] != key[1]:
				cov_matrix[key[0], key[1]] = value
				cov_matrix[key[1], key[0]] = value

		lines = [np.array2string(line, separator=',', sign='+') for line in cov_matrix]
		cov_matrix = ';'.join(lines)
		cov_matrix = cov_matrix.replace('[','')
		cov_matrix = cov_matrix.replace(']','')
		return '{'+cov_matrix+'}'
	
	def contribution_list(self, first=-1, limit=0.0001):
		thisone = sorted([(key.symbol, value) for key, value in self.indexes.items() if value > limit], key=lambda x:x[1], reverse=True)
		if len(thisone) > first > 0:
			return thisone[:first+1]
		return thisone


class TotalBudget(PartialBudget):
	def __init__(self, NAP, CS, SC, NF, EF, MSS, BNK, FSS):
		super().__init__()

		NAP, CS, SC, NF, EF, MSS, BNK, FSS = Parameter(NAP.x, NAP.ux, 'net area ratio'), Parameter(CS.x, CS.ux, 'decay ratio'), Parameter(SC.x, SC.ux, 'k0 ratio'), Parameter(NF.x, NF.ux, 'neutron flux ratio'), Parameter(EF.x, EF.ux, 'efficiency ratio'), Parameter(MSS.x, MSS.ux, 'mass ratio'), Parameter(BNK.x, BNK.ux, 'blank correction'), Parameter(FSS.x, FSS.ux, 'U fission correction')

		self.correlations = {}
		self.parameters = [NAP, CS, SC, NF, EF, MSS, BNK, FSS]

		self.x, self.ux, self.indexes = self.solve()

	def solve(self):
		return self.measurand_result()
		
	def measurand_result(self):

		def _best_estimate(pms):
			return pms[0] * pms[1] * pms[2] * pms[3] * pms[4] * pms[5] - pms[6] - pms[7]

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

		#analytic sensitivity coefficients (think about it)
		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		return best_estimate, uncertainty, contributions_to_variance


class NetAreaCounts(PartialBudget):
	"""Budget including counting statistics and net area peak data"""
	def __init__(self, M, standard_spectrum, sample_spectrum, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id):
		super().__init__()

		_tol = M.settings.get('energy tolerance')
		smp_BKG_area, smp_BKG_uarea, std_BKG_area, std_BKG_uarea = 0, 0, 0, 0
		background_spectrum = M.INAAnalysis.background_spectrum
		if background_spectrum is not None:
			for pline in background_spectrum.peak_list:
				if sm_emission_line.energy -_tol < pline[2] < sm_emission_line.energy +_tol:
					if pline[4] > smp_BKG_area:
						smp_BKG_area, smp_BKG_uarea = pline[4], pline[5]
				if st_emission_line.energy -_tol < pline[2] < st_emission_line.energy +_tol:
					if pline[4] > std_BKG_area:
						std_BKG_area, std_BKG_uarea = pline[4], pline[5]

				if pline[2] > sm_emission_line.energy +_tol and pline[2] > st_emission_line.energy +_tol:
					break

			ursmp, urstd = 0, 0
			if smp_BKG_area > 0:
				ursmp = smp_BKG_uarea / smp_BKG_area
			if std_BKG_area > 0:
				urstd = std_BKG_uarea / std_BKG_area

			smp_BKG_area = smp_BKG_area / background_spectrum.live_time * sample_spectrum.live_time
			smp_BKG_uarea = smp_BKG_area * ursmp

			std_BKG_area = std_BKG_area / background_spectrum.live_time * standard_spectrum.live_time
			std_BKG_uarea = std_BKG_area * urstd

		self.sample_netarea = Parameter(sample_spectrum.peak_list[sm_emiss_id][4], sample_spectrum.peak_list[sm_emiss_id][5], r'$n_\mathrm{p\:smp}$')

		self.sample_background_area = Parameter(smp_BKG_area, smp_BKG_uarea, r'$n_\mathrm{bkg\:smp}$')

		self.sample_interference_area = Parameter(0, 0, r'$n_\mathrm{intrf\:smp}$')

		self.standard_netarea = Parameter(standard_spectrum.peak_list[st_emiss_id][4], standard_spectrum.peak_list[st_emiss_id][5], r'$n_\mathrm{p\:std}$')

		self.standard_background_area = Parameter(std_BKG_area, std_BKG_uarea, r'$n_\mathrm{bkg\:std}$')

		self.standard_interference_area = Parameter(0, 0, r'$n_\mathrm{intrf\:std}$')

		self.correlations = {}
		self.parameters = [self.sample_netarea, self.sample_background_area, self.sample_interference_area, self.standard_netarea, self.standard_background_area, self.standard_interference_area]
		
		self.x, self.ux, self.indexes, self._dof = self.solve()

	def solve(self):
		return self.solve_direct()
	
	def solve_direct(self):
		
		def _best_estimate(pms):
			return (pms[0] - pms[1] - pms[2]) / (pms[3] - pms[4] - pms[5])

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF


class CountingStatistics(PartialBudget):
	"""Budget including decay correction and gamma-counting data"""
	def __init__(self, M, standard_spectrum, sample_spectrum, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id):
		super().__init__()

		self.direct_types = ('I', 'IVB', 'VI')

		self.decaytype = sm_emission_line.line['type']
		self.analtype = st_emission_line == sm_emission_line

		self.irr_time = Parameter(M.INAAnalysis.irradiation.irradiation_time, M.INAAnalysis.irradiation.unc_irradiation_time, r'$t_\mathrm{i}$')
		self.sample_lambda3 = Parameter(*sm_emission_line.get_lambda(sm_emission_line.line['C3_t1/2'], sm_emission_line.line['C3_ut1/2'], sm_emission_line.line['C3_unit']), r'$\lambda_\mathrm{smp}^{\prime}$')
		self.sample_lambda2 = Parameter(*sm_emission_line.get_lambda(sm_emission_line.line['C2_t1/2'], sm_emission_line.line['C2_ut1/2'], sm_emission_line.line['C2_unit']), r'$\lambda_\mathrm{smp}^{\prime\prime}$')
		self.sample_lambda1 = Parameter(*sm_emission_line.get_lambda(sm_emission_line.line['C1_t1/2'], sm_emission_line.line['C1_ut1/2'], sm_emission_line.line['C1_unit']), r'$\lambda_\mathrm{smp}^{\prime\prime\prime}$')
		self.sample_real = Parameter(sample_spectrum.real_time, M.settings.get('default tc&tl uncertainties'), r'$t_\mathrm{c\:smp}$')
		self.sample_live = Parameter(sample_spectrum.live_time, M.settings.get('default tc&tl uncertainties'), r'$t_\mathrm{l\:smp}$')
		td = sample_spectrum.datetime - standard_spectrum.datetime
		self.sample_to_standard_td = Parameter(td.total_seconds(), np.sqrt(2), r'$\Delta t_\mathrm{d}$')

		self.standard_lambda3 = Parameter(*st_emission_line.get_lambda(st_emission_line.line['C3_t1/2'], st_emission_line.line['C3_ut1/2'], st_emission_line.line['C3_unit']), r'$\lambda_\mathrm{std}^{\prime}$')
		self.standard_lambda2 = Parameter(*st_emission_line.get_lambda(st_emission_line.line['C2_t1/2'], st_emission_line.line['C2_ut1/2'], st_emission_line.line['C2_unit']), r'$\lambda_\mathrm{std}^{\prime\prime}$')
		self.standard_lambda1 = Parameter(*st_emission_line.get_lambda(st_emission_line.line['C1_t1/2'], st_emission_line.line['C1_ut1/2'], st_emission_line.line['C1_unit']), r'$\lambda_\mathrm{std}^{\prime\prime\prime}$')
		self.standard_real = Parameter(standard_spectrum.real_time, M.settings.get('default tc&tl uncertainties'), r'$t_\mathrm{c\:std}$')
		self.standard_live = Parameter(standard_spectrum.live_time, M.settings.get('default tc&tl uncertainties'), r'$t_\mathrm{l\:std}$')
		td = standard_spectrum.datetime - M.INAAnalysis.irradiation.datetime
		self.standard_td = Parameter(td.total_seconds(), 60, r'$t_\mathrm{d\:std}$')

		self.mu = Parameter(M.INAAnalysis.characterization.detector.mu, M.INAAnalysis.characterization.detector.u_mu, r'$\mu$')

		self.correlations = {}
		self.parameters = [self.irr_time, self.sample_lambda3, self.sample_real, self.sample_live, self.sample_to_standard_td, self.standard_real, self.standard_live, self.standard_td, self.mu, self.standard_lambda3]
		
		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _model(self):
		if self.analtype and self.decaytype in self.direct_types:
			return 'relative_direct'
		elif not self.analtype and self.decaytype in self.direct_types:
			return 'k0_direct'
		return 'error'

	def solve(self):
		if self.analtype and self.decaytype in self.direct_types:
			return self.solve_relative_direct()
		elif not self.analtype and self.decaytype in self.direct_types:
			return self.solve_k0_direct()
		return 0.0, 0.0, {}, 15
	
	def solve_k0_direct(self):
		
		def _best_estimate(pms):
			return (pms[1] * pms[2] * np.exp(pms[8]*(1 - pms[3]/pms[2])) * (1 - np.exp(-pms[9] * pms[0])) * (1 - np.exp(-pms[9] * pms[5])) * pms[6]) / (pms[9] * pms[5] * np.exp(pms[8]*(1 - pms[6]/pms[5])) * (1 - np.exp(-pms[1] * pms[0])) * (1 - np.exp(-pms[1] * pms[2])) * pms[3]) * np.exp((pms[1] - pms[9]) * pms[7] + pms[1] * pms[4])

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
		
	def solve_relative_direct(self):

		def _best_estimate(pms):
			return (pms[2] * pms[6] * (1-np.exp(-pms[1] * pms[5]))) / (pms[5] * pms[3] * (1-np.exp(-pms[1] * pms[2]))) * np.exp(pms[8]*(pms[6]/pms[5]-pms[3]/pms[2])) * np.exp(pms[1] * pms[4])

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF


class SampleComposition(PartialBudget):
	"""Budget including k0 data ratio"""
	def __init__(self, M, st_emission_line, sm_emission_line):

		self.analtype = st_emission_line == sm_emission_line
		self.targettype = st_emission_line.target == sm_emission_line.target

		subspace_filter = M.INAAnalysis.abundances_database['element'] == sm_emission_line.target

		subspace = M.INAAnalysis.abundances_database[subspace_filter]

		data = subspace.loc[subspace['A'] == sm_emission_line.line['T_A']][['abundance','uabundance','M','uM']]

		col_list = list(data.columns)

		self.theta_a = Parameter(data.iloc[0, col_list.index('abundance')], data.iloc[0, col_list.index('uabundance')], r'$\theta_\mathrm{smp}$')
		self.M_0 = Parameter(data.iloc[0, col_list.index('M')], data.iloc[0, col_list.index('uM')], r'$M_\mathrm{smp}$')

		data = subspace.loc[subspace['A'] != sm_emission_line.line['T_A']][['A','abundance','uabundance','M','uM']]

		col_list = list(data.columns)

		nn = 0
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a1 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_1 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a1 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_1 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a2 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_2 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a2 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_2 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a3 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_3 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a3 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_3 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a4 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_4 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a4 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_4 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a5 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_5 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a5 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_5 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a6 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_6 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a6 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_6 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a7 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_7 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a7 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_7 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a8 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_8 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a8 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_8 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_a9 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
			self.M_9 = Parameter(data.iloc[nn, col_list.index('M')], data.iloc[nn, col_list.index('uM')], rf'$M_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_a9 = Parameter(0.0, 0.0, r'$\theta_\mathrm{smp}$')
			self.M_9 = Parameter(0.0, 0.0, r'$M_\mathrm{smp}$')

		subspace_filter = M.INAAnalysis.abundances_database['element'] == st_emission_line.target

		subspace = M.INAAnalysis.abundances_database[subspace_filter]

		data = subspace.loc[subspace['A'] == st_emission_line.line['T_A']][['abundance','uabundance','M','uM']]

		col_list = list(data.columns)

		self.theta_m = Parameter(data.iloc[0, col_list.index('abundance')], data.iloc[0, col_list.index('uabundance')], r'$\theta_\mathrm{std}$')

		data = subspace.loc[subspace['A'] != st_emission_line.line['T_A']][['A','abundance','uabundance','M','uM']]

		col_list = list(data.columns)

		nn = 0
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m1 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m1 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m2 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m2 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m3 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m3 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m4 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m4 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m5 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m5 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m6 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m6 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m7 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m7 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m8 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m8 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		nn += 1
		try:
			isot = f"{sm_emission_line.target}-{data.iloc[nn]['A']}"
			self.theta_m9 = Parameter(data.iloc[nn, col_list.index('abundance')], data.iloc[nn, col_list.index('uabundance')], rf'$\theta_\mathrm{{{isot}}}$')
		except IndexError:
			self.theta_m9 = Parameter(0.0, 0.0, r'$\theta_\mathrm{std}$')

		self.k0_m = Parameter(st_emission_line.line['k0'], st_emission_line.line['uk0'], r'$k_\mathrm{0\:Au}\left(\mathrm{m}\right)$')
		self.k0_a = Parameter(sm_emission_line.line['k0'], sm_emission_line.line['uk0'], r'$k_\mathrm{0\:Au}\left(\mathrm{a}\right)$')

		self.parameters = [self.theta_a, self.M_0, self.theta_a1, self.M_1, self.theta_a2, self.M_2, self.theta_a3, self.M_3, self.theta_a4, self.M_4, self.theta_a5, self.M_5, self.theta_a6, self.M_6, self.theta_a7, self.M_7, self.theta_a8, self.M_8, self.theta_a9, self.M_9, self.theta_m, self.theta_m1, self.theta_m2, self.theta_m3, self.theta_m4, self.theta_m5, self.theta_m6, self.theta_m7, self.theta_m8, self.theta_m9, self.k0_m, self.k0_a]

		self.correlations = {}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _model(self):
		if self.analtype:
			return 'relative_direct'
		elif self.targettype:
			return 'relative_direct'#provisional!!!!!!!!!!
		elif not self.analtype and not self.targettype:
			return 'k0_direct'
		return 'error'

	def solve(self):
		if self.analtype:
			return self.solve_relative()
		elif self.targettype:
			return self.solve_relative()#provisional!!!!!!!!!!
		elif not self.analtype and not self.targettype:
			return self.solve_k0()
		return 0.0, 0.0, {}, 15
	
	def solve_k0(self):
		
		def _best_estimate(pms):
			return pms[30] / pms[31]

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	
	def solve_relative(self):

		def _best_estimate(pms):
			return (pms[20] * (pms[0]*pms[1] + pms[2]*pms[3] + pms[4]*pms[5] + pms[6]*pms[7] + pms[8]*pms[9] + pms[10]*pms[11] + pms[12]*pms[13] + pms[14]*pms[15] + pms[16]*pms[17] + pms[18]*pms[19])) / (pms[0] * (pms[20]*pms[1] + pms[21]*pms[3] + pms[22]*pms[5] + pms[23]*pms[7] + pms[24]*pms[9] + pms[25]*pms[11] + pms[26]*pms[13] + pms[27]*pms[15] + pms[28]*pms[17] + pms[29]*pms[19]))
		

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	

class NeutronFlux(PartialBudget):
	"""Budget involving the ratio of neutron acativation for standard and sample"""
	def __init__(self, M, standard_id, sample_id, st_emission_line, sm_emission_line):

		self.relative = st_emission_line == sm_emission_line
		self.target_E, self.target_A = sm_emission_line.target, f'{int(sm_emission_line.line["A"]-1)}'

		self.beta, self.delta_l = self._get_gradient(M.INAAnalysis.irradiation, standard_id, sample_id, st_emission_line, M.INAAnalysis.characterization.reference_position)

		sample_a = M.INAAnalysis.get_sample(sample_id)
		sample_m = M.INAAnalysis.get_sample(standard_id)

		Ge_a, uGe_a = sample_a._get_epithermal(sm_emission_line.target, f'{int(sm_emission_line.line["A"]-1)}')
		Ge_m, uGe_m = sample_m._get_epithermal(st_emission_line.target, f'{int(st_emission_line.line["A"]-1)}')

		self.Gth_a, self.Ge_a = Parameter(sample_a.Gth, sample_a.uGth, r'$G_\mathrm{th\:smp}$'), Parameter(Ge_a, uGe_a, r'$G_\mathrm{e\:smp}$') #-> functions depending on elemental characterization
		self.Gth_m, self.Ge_m = Parameter(sample_m.Gth, sample_m.uGth, r'$G_\mathrm{th\:std}$'), Parameter(Ge_m, uGe_m, r'$G_\mathrm{e\:std}$') #-> functions depending on elemental characterization

		self.f, self.alpha = self._get_f_alpha(M.INAAnalysis.irradiation) #-> online evaluation or fallback to default, also correlation between these two values

		if isinstance(sm_emission_line.line['uQ0'], str):
			QErr = sm_emission_line.line['Q0'] * 0.2
		else:
			QErr = sm_emission_line.line['Q0'] * sm_emission_line.line['uQ0'] / 100
		if isinstance(sm_emission_line.line['uEr'], str):
			EErr = sm_emission_line.line['Er'] * 0.5
		else:
			EErr = sm_emission_line.line['Er'] * sm_emission_line.line['uEr'] / 100
		self.Q0_a, self.Er_a = Parameter(sm_emission_line.line['Q0'], QErr, r'$Q_\mathrm{0\:smp}$'), Parameter(sm_emission_line.line['Er'], EErr, r'$\bar{E}_\mathrm{r\:smp}$') #-> from database

		if isinstance(st_emission_line.line['uQ0'], str):
			QErr = st_emission_line.line['Q0'] * 0.2
		else:
			QErr = st_emission_line.line['Q0'] * st_emission_line.line['uQ0'] / 100
		if isinstance(st_emission_line.line['uEr'], str):
			EErr = st_emission_line.line['Er'] * 0.5
		else:
			EErr = st_emission_line.line['Er'] * st_emission_line.line['uEr'] / 100

		self.Q0_m, self.Er_m = Parameter(st_emission_line.line['Q0'], QErr, r'$Q_\mathrm{0\:std}$'), Parameter(st_emission_line.line['Er'], EErr, r'$\bar{E}_\mathrm{r\:std}$') #-> from database

		self.parameters = [self.beta, self.delta_l, self.Gth_a, self.Ge_a, self.Gth_m, self.Ge_m, self.f, self.alpha, self.Q0_a, self.Er_a, self.Q0_m, self.Er_m]

		self.correlations = {(6,7):M.settings.get('f&a correlation')}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _update(self, sample, ssh_database):
		sample.Gth, sample.uGth = sample._calculate_thermal_self_shielding(ssh_database)
		sample.epi_shielding = sample._calculate_epithermal_self_shielding(ssh_database)
		Ge_a, uGe_a = sample._get_epithermal(self.target_E, self.target_A)
		self.Gth_a, self.Ge_a = Parameter(sample.Gth, sample.uGth, r'$G_\mathrm{th\:smp}$'), Parameter(Ge_a, uGe_a, r'$G_\mathrm{e\:smp}$') #-> functions depending on elemental characterization
		self.parameters[2] = self.Gth_a
		self.parameters[3] = self.Ge_a

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _get_gradient(self, irradiation, standard_id, sample_id, st_emission_line, cpos):
		self.outcome_message = ''
		_dd, _udd = irradiation.irradiation_scheme.standard_sample_distance(standard_id, sample_id)
		aux_code = irradiation.irradiation_scheme._get_adjacent_standards(standard_id, sample_id)
		gradient, ugradient = irradiation.irradiation_scheme.get_beta_value(aux_code, standard_id, st_emission_line, cpos)
		return Parameter(gradient, ugradient, r'$\beta$'), Parameter(_dd, _udd, r'$\Delta l$')

	def _get_f_alpha(self, irradiation):
		#calculate f and alpha

		#if f<=0 or any other issue, fallback to default value
		return Parameter(irradiation.f_value, irradiation.unc_f_value, r'$f$'), Parameter(irradiation.a_value, irradiation.unc_a_value, r'$\alpha$')
	
	def _model(self):
		if self.relative:
			return 'relative_direct'
		else:
			return 'not-relative_direct'

	def solve(self):
		if self.relative:
			return self.solve_relative()
		else:
			return self.solve_not_relative()

	def solve_not_relative(self):

		def _best_estimate(pms):
			return (1 / (1 + pms[0] * pms[1])) * (pms[4] + pms[5]/pms[6] * ((pms[10]-0.429) / pms[11]**pms[7] + 0.429/(0.55**pms[7] * (1+2*pms[7])))) / (pms[2] + pms[3]/pms[6] * ((pms[8]-0.429) / pms[9]**pms[7] + 0.429/(0.55**pms[7] * (1+2*pms[7]))))

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	
	def solve_relative(self):

		def _best_estimate(pms):
			return (1 / (1 + pms[0] * pms[1])) * (pms[4] + pms[5]/pms[6] * ((pms[10]-0.429) / pms[11]**pms[7] + 0.429/(0.55**pms[7] * (1+2*pms[7])))) / (pms[2] + pms[3]/pms[6] * ((pms[10]-0.429) / pms[11]**pms[7] + 0.429/(0.55**pms[7] * (1+2*pms[7]))))

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF


class Efficiency(PartialBudget):
	"""Budget involving ratio of detection efficiencies"""
	def __init__(self, M, standard_spectrum, sample_spectrum, st_emission_line, sm_emission_line):

		self.E_a, self.E_m = sm_emission_line.energy, st_emission_line.energy

		self.same_target = st_emission_line == sm_emission_line
		self.same_distance = sample_spectrum.counting_position == standard_spectrum.counting_position
		self.onereference = True

		keDE, ukeDE, keDD, ukeDD = M.INAAnalysis.characterization._get_keDEDD(sample_spectrum.counting_position, standard_spectrum.counting_position, self.E_a, self.E_m)

		self._keDE, self._keDD = Parameter(keDE, ukeDE, r'$k_{\varepsilon\:\Delta E}$'), Parameter(keDD, ukeDD, r'$k_{\varepsilon\:\Delta d}$')

		d0a, ud0a, d0m, ud0m, _corr = M.INAAnalysis.characterization._get_d0primes(sample_spectrum.counting_position, standard_spectrum.counting_position, self.E_a, self.E_m)

		self.d0_m, self.d0_a = Parameter(d0m, ud0m, r'$d\prime_\mathrm{0\:std}$'), Parameter(d0a, ud0a, r'$d\prime_\mathrm{0\:smp}$')

		self.d_m, self.deltad_m = Parameter(standard_spectrum.counting_position, 0.1, r'$d_\mathrm{std}$'), Parameter(standard_spectrum.positioning_variability, standard_spectrum.uncertainty_positioning_variability, r'$\delta d_\mathrm{std}$')
		self.d_a, self.deltad_a = Parameter(sample_spectrum.counting_position, 0.1, r'$d_\mathrm{smp}$'), Parameter(sample_spectrum.positioning_variability, sample_spectrum.uncertainty_positioning_variability, r'$\delta d_\mathrm{smp}$')

		Msample_a = M.INAAnalysis.get_sample(sample_spectrum.sample)
		Msample_m = M.INAAnalysis.get_sample(standard_spectrum.sample)

		self.h_m, self.h_a = Parameter(Msample_m.height, Msample_m.height_unc, r'$h_\mathrm{std}$'), Parameter(Msample_a.height, Msample_a.height_unc, r'$h_\mathrm{smp}$')

		self.rho_m, self.rho_a = Parameter(Msample_m.density, Msample_m.density_unc, r'$\rho_\mathrm{std}$'), Parameter(Msample_a.density, Msample_a.density_unc, r'$\rho_\mathrm{smp}$')

		sm_murho, sm_umurho = self.get_mu_value(M.INAAnalysis.absorptions_database, self.E_a/1000, Msample_a.composition)
		self.nu_a = Parameter(sm_murho*100, sm_umurho*100, r'$\nu_\mathrm{smp}$')

		std_murho, std_umurho = self.get_mu_value(M.INAAnalysis.absorptions_database, self.E_m/1000, Msample_m.composition)
		self.nu_m = Parameter(std_murho*100, std_umurho*100, r'$\nu_\mathrm{std}$')

		#COI things
		COI_value, COI_uncertainty = M.INAAnalysis.characterization._get_COI_correction(M.INAAnalysis.COI_database, self.same_target, self.same_distance, st_emission_line.emission.replace(' keV','').split()[0], self.E_m, standard_spectrum.counting_position, sm_emission_line.emission.replace(' keV','').split()[0], self.E_a, sample_spectrum.counting_position)
		self.rCOI = Parameter(COI_value, COI_uncertainty, r'$rCOI$')

		self.parameters = [self._keDE, self._keDD, self.d_m, self.deltad_m, self.d0_m, self.d_a, self.deltad_a, self.d0_a, self.h_m, self.h_a, self.nu_m, self.rho_m, self.nu_a, self.rho_a, self.rCOI]

		self.correlations = {(2,5) : _corr}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _model(self):
		if self.same_distance and self.same_target:
			return 'all_relative_direct'
		elif self.same_distance:
			return 'same_distance'
		elif not self.same_distance:
			return 'different_distance'
		return ''

	def solve(self):
		if self.same_distance and self.same_target:
			return self.solve_fullrelative()
		elif self.same_distance:
			return self.solve_samedistance()#check formula!!!!!
		elif not self.same_distance:
			return self.solve_nosamedistance()#check formula!!!!!
		return 1.0, 0.0, {}, 15
	
	def solve_fullrelative(self):

		def _best_estimate(pms):
			return pms[0] * pms[1] * ((1 + pms[6] / (pms[2] - pms[4])) / (1 + pms[3] / (pms[2] - pms[4]))) * ((1 + (pms[6] + pms[9]) / (pms[2] - pms[4])) / (1 + (pms[3] + pms[8]) / (pms[2] - pms[4]))) * ((1 - np.exp(-pms[10] * pms[8] * pms[11] / 1000)) / (pms[10] * pms[8] * pms[11])) / ((1 - np.exp(-pms[12] * pms[9] * pms[13] / 1000)) / (pms[12] * pms[9] * pms[13])) * pms[14]

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	
	def solve_samedistance(self):

		def _best_estimate(pms):
			return pms[0] * pms[1] * ((1 + pms[6] / (pms[2] - pms[4])) / (1 + pms[3] / (pms[2] - pms[7]))) * ((1 + (pms[6] + pms[9]) / (pms[2] - pms[7])) / (1 + (pms[3] + pms[8]) / (pms[2] - pms[4]))) * ((1 - np.exp(-pms[10] * pms[8] * pms[11] / 1000)) / (pms[10] * pms[8] * pms[11])) / ((1 - np.exp(-pms[12] * pms[9] * pms[13] / 1000)) / (pms[12] * pms[9] * pms[13])) * pms[14]

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	
	def solve_nosamedistance(self):

		def _best_estimate(pms):
			return pms[0] * pms[1] * ((1 + pms[6] / (pms[2] - pms[4])) / (1 + pms[3] / (pms[5] - pms[7]))) * ((1 + (pms[6] + pms[9]) / (pms[5] - pms[7])) / (1 + (pms[3] + pms[8]) / (pms[2] - pms[4]))) * ((1 - np.exp(-pms[10] * pms[8] * pms[11] / 1000)) / (pms[10] * pms[8] * pms[11])) / ((1 - np.exp(-pms[12] * pms[9] * pms[13] / 1000)) / (pms[12] * pms[9] * pms[13])) * pms[14]

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF
	
	def _update(self, sample, absorptions_database):
		sm_murho, sm_umurho = self.get_mu_value(absorptions_database, self.E_a/1000, sample.composition)
		self.nu_a = Parameter(sm_murho*100, sm_umurho*100, r'$\nu_\mathrm{smp}$')
		self.parameters[12] = self.nu_a
		self.x, self.ux, self.indexes, self._dof = self.solve()

	def get_mu_value(self, database, energy, sample):
		murho = np.sum([sample.certificate[element][0] * self.find_mu_value(database, energy, element) for element in sample.certificate.keys()])
		if murho > 0:
			return murho, murho*0.1
		else:
			return 1E-6, 0.0

	def find_mu_value(self, database, value, element, default_value = 1E-6):
		try:
			df = database[element]
			df.dropna(inplace=True)
		except:
			return default_value
		dix = np.array(df.index)
		filt = dix < value
		x, y = [], []

		try:
			x.append(df[filt].index[-1])
			y.append(df[filt].iloc[-1])
		except IndexError:
			pass
		try:
			x.append(df[~filt].index[0])
			y.append(df[~filt].iloc[0])
		except IndexError:
			pass
		if len(y) == 2:
			#linear approximation
			m = (y[1] - y[0]) / (x[1] - x[0])
			yy = y[0] + (value - x[0]) * m
			return yy
		elif len(y) == 1:
			return y[0]
		else:
			return default_value


class Masses_Comp(PartialBudget):
	"""Budget involving ratio of masses"""
	def __init__(self, M, standard_id, sample_id, m_target):

		#self.relative = True#other options
		sample_m = M.INAAnalysis.get_sample(standard_id)
		sample_a = M.INAAnalysis.get_sample(sample_id)

		self.m_m, self.moist_m = Parameter(sample_m.composition.mass, sample_m.composition.umass, r'$m_\mathrm{std}$'), Parameter(sample_m.composition.moisture/100, sample_m.composition.umoisture/100, r'$\eta_\mathrm{std}$')
		self.m_a, self.moist_a = Parameter(sample_a.composition.mass, sample_a.composition.umass, r'$m_\mathrm{smp}$'), Parameter(sample_a.composition.moisture/100, sample_a.composition.umoisture/100, r'$\eta_\mathrm{smp}$')
		xw, uxw = sample_m.composition.certificate.get(m_target, (0.0, 0.0))
		self.w_m = Parameter(xw, uxw, r'$w_\mathrm{std}$')

		self.atmospheric_pressure = Parameter(M.INAAnalysis.air_buoyancy['pressure'], M.INAAnalysis.air_buoyancy['u_pressure'], r'$p$')
		self.relative_humidity = Parameter(M.INAAnalysis.air_buoyancy['relative humidity'], M.INAAnalysis.air_buoyancy['u_relative humidity'], r'$RH$')
		self.temperature = Parameter(M.INAAnalysis.air_buoyancy['temperature'], M.INAAnalysis.air_buoyancy['u_temperature'], r'$T$')
		self.standard_steel = Parameter(M.INAAnalysis.air_buoyancy['steel'], M.INAAnalysis.air_buoyancy['u_steel'], r'$\rho_\mathrm{C}$')

		ddd, udd = sample_m.get_weighting_density(m_target)
		self.density_standard = Parameter(ddd, udd, r'$\ast\rho_\mathrm{m}$')
		ddd, udd = sample_a.get_weighting_density()
		self.density_sample = Parameter(ddd, udd, r'$\ast\rho_\mathrm{a}$')

		self.parameters = [self.m_a, self.moist_a, self.m_m, self.moist_m, self.w_m, self.atmospheric_pressure, self.relative_humidity, self.temperature, self.standard_steel, self.density_standard, self.density_sample]

		self.correlations = {}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def solve(self):
		return self.solve_masses()
	
	def solve_masses(self):

		def _best_estimate(pms):
			return (pms[2] * (1 - pms[3]) * pms[4] * (1 + 0.001 * (0.34848 * pms[5] - 0.009 * pms[6] * np.exp(0.061 * pms[7]))/(273.15 * pms[7]) * (1/pms[9] - 1/pms[8]))) / (pms[0] * (1 - pms[1]) * (1 + 0.001 * (0.34848 * pms[5] - 0.009 * pms[6] * np.exp(0.061 * pms[7]))/(273.15 * pms[7]) * (1/pms[10] - 1/pms[8])))

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF


class Blank_Corr(PartialBudget):
	"""Some information about the blank correction"""
	def __init__(self, M, standard_id, sample_id, a_target):
		sample_a = M.INAAnalysis.get_sample(sample_id)

		if M.INAAnalysis.blank_info is not None:
			mb, umb = M.INAAnalysis.blank_info.mass, M.INAAnalysis.blank_info.umass
			wb, uwb = M.INAAnalysis.blank_info.certificate.get(a_target, (0.0, 0.0))
		else:
			mb, umb, wb, uwb = 0.0, 0.0, 0.0, 0.0

		self.m_blank, self.w_blank = Parameter(mb, umb, r'$m_\mathrm{blank}$'), Parameter(wb, uwb, r'$w_\mathrm{blank}$')

		self.m_a, self.moist_a = Parameter(sample_a.composition.mass, sample_a.composition.umass, r'$m_\mathrm{smp}$'), Parameter(sample_a.composition.moisture/100, sample_a.composition.umoisture/100, r'$\eta_\mathrm{smp}$')

		self.parameters = [self.m_a, self.moist_a, self.m_blank, self.w_blank]

		self.correlations = {}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def solve(self):
		return self.solve_blank()
	
	def solve_blank(self):

		def _best_estimate(pms):
			return (pms[2] * pms[3]) / (pms[0] * (1 - pms[1]))

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		sens_coeff = []
		dofs = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

			dofs.append(pp._dof)

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		dofs = np.array(dofs)
		uncertainties = np.sqrt(np.diag(cov_m))
		try:
			DOF = int(np.power(uncertainty, 4) / np.sum(np.power(sens_coeff * uncertainties, 4) / dofs))
		except ValueError:
			DOF = 15

		return best_estimate, uncertainty, contributions_to_variance, DOF


class Fission_Corr(PartialBudget):
	"""Some information about fission correction"""
	def __init__(self, M, sample_id, a_target, selfSC, selfNF):
		
		theta_a = selfSC.theta_a
		M_0 = selfSC.M_0

		ff = selfNF.f
		aa = selfNF.alpha
		Q0a = selfNF.Q0_a
		Era = selfNF.Er_a

		#default target cross section
		_XS, _uXS = 0.0, 0.0

		e_mitter = a_target.emission.split()[0]
		dataline = M.INAAnalysis.k0_database.loc[(M.INAAnalysis.k0_database['C3'] == e_mitter) & (M.INAAnalysis.k0_database['target'] == a_target.target), ['XS', 'uXS']]

		try:
			XS_value, XS_unc = dataline.iloc[0]
			_XS = XS_value * 1E-24
			_uXS = XS_unc / 100 * _XS
		except (IndexError, TypeError):
			_XS, _uXS = 0.0, 0.0

		#default fission yield
		_FIS, _uFIS = 0.0, 0.0

		termitter = f'{a_target.target} {e_mitter}'
		dataline = M.INAAnalysis.fiss_database.loc[M.INAAnalysis.fiss_database['termitter'] == termitter, ['yFISS', 'uyFISS']]

		try:
			_FIS, _uFIS = dataline.iloc[0]
		except IndexError:
			_FIS, _uFIS = 0.0, 0.0

		#self.relative = True#other options
		sample_a = M.INAAnalysis.get_sample(sample_id)
		xw, uxw = sample_a.composition.certificate.get('U', (0.0, 0.0))
		self.w_U = Parameter(xw, uxw, r'$w_\mathrm{U}$')
		self.theta_a = Parameter(theta_a.value, theta_a.uncertainty, theta_a.symbol, theta_a._dof)
		self.M_0 = Parameter(M_0.value, M_0.uncertainty, M_0.symbol, M_0._dof)
		self.Q0_a = Parameter(Q0a.value, Q0a.uncertainty, Q0a.symbol, Q0a._dof)
		self.Er_a = Parameter(Era.value, Era.uncertainty, Era.symbol, Era._dof)
		self.sigma_a = Parameter(_XS, _uXS, r'$\sigma_\mathrm{a}$')
		self.f = Parameter(ff.value, ff.uncertainty, ff.symbol, ff._dof)
		self.alpha = Parameter(aa.value, aa.uncertainty, aa.symbol, aa._dof)
		self.theta_U = Parameter(7.20E-03, 6.00E-06, r'$\theta_\mathrm{U}$')
		self.M_U = Parameter(238.0289, 3.00E-05, r'$M_\mathrm{U}$')
		self.Q0_U = Parameter(4.70E-01, 8.59E-03, r'$Q_{0\:\mathrm{U}}$')
		self.Er_U = Parameter(5.90E-01, 2.95E-01, r'$\bar{E}_\mathrm{r\:U}$')
		self.sigma_U = Parameter(5.83E-22, 1.10E-24, r'$\sigma_\mathrm{U}$')
		self.yFISS = Parameter(_FIS, _uFIS, r'$y_\mathrm{FISS}$')

		self.parameters = [self.w_U, self.theta_a, self.M_0, self.Q0_a, self.Er_a, self.sigma_a, self.f, self.alpha, self.theta_U, self.M_U, self.Q0_U, self.Er_U, self.sigma_U, self.yFISS]

		self.correlations = {}

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def _update(self, sample):
		xw, uxw = sample.composition.certificate.get('U', (0.0, 0.0))
		self.w_U = Parameter(xw, uxw, r'$w_\mathrm{U}$')
		self.parameters[0] = self.w_U

		self.x, self.ux, self.indexes, self._dof = self.solve()

	def solve(self):
		return self.solve_fission()
	
	def solve_fission(self):

		def _best_estimate(pms):
			return pms[0] * (pms[2] * pms[8] * pms[12] * pms[13] * (pms[6] + ((pms[10] - 0.429)/pms[11]**pms[7] + 0.429/((2*pms[7]+1)*0.55**pms[7])))) / (pms[9] * pms[1] * pms[5] * (pms[6] + ((pms[3] - 0.429)/pms[4]**pms[7] + 0.429/((2*pms[7]+1)*0.55**pms[7]))))

		pms = [item.get_value() for item in self.parameters]

		best_estimate = _best_estimate(pms)

		if np.isnan(best_estimate):
			return 0.0, 0.0, {}, 15

		sens_coeff = []

		for nn, pp in enumerate(self.parameters):
			pms[nn] = pp.get_value('+')
			plus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value('-')
			minus_estimate = _best_estimate(pms)
			pms[nn] = pp.get_value()

			sens_coeff.append((plus_estimate - minus_estimate) / (2 * pp.get_unc() + 1E-24))

		sens_coeff = np.array(sens_coeff)
		cov_m = self.get_covariance_matrix()

		uncertainty = np.sqrt((sens_coeff.T@cov_m) @ sens_coeff)

		contributions_to_variance = {}

		for nn, pp in enumerate(self.parameters):
			contributions_to_variance[pp] = (sens_coeff[nn] * sens_coeff @ cov_m[nn]) / np.power(uncertainty, 2)

		if np.isnan(uncertainty):
			return best_estimate, 0.0, {}, 15

		return best_estimate, uncertainty, contributions_to_variance, 15


class UncBudget:
	"""
	Store information to calculate results and return uncertainty budgets of k0 and relative NAA.
	All uncertainties have to be entered (and are returned) as absolute standard uncertainties
	"""
	def __init__(self, M, standard_spectrum, st_idx, sample_spectrum, sm_idx, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id):#, idx, M, standard_spectrum, sample_spectrum, st_emission_line, sm_emission_line):
		#
		self._version = M._version
		self.standard_code, self.sample_code, self.target, self.emission = f'#{st_idx+1}', f'#{sm_idx+1}', sm_emission_line.target, sm_emission_line.emission
		self.standard_id = standard_spectrum.sample
		self.sample_id = sample_spectrum.sample
		smpl = M.INAAnalysis.get_sample(self.sample_id)
		self.material = smpl.composition.data[0][4].name #name of the material of something like that because different samples can just be subsamples of the same material
		self.sel_id = (sm_idx, sm_emiss_id)
		self.method = self.k0_or_not(st_emission_line, sm_emission_line)#4 possibilities, relative, k0, relative with different counting positions and maybe R or K in UncBudget code to discriminate between k0 and relative? (that might work)
		self.monitor = st_emission_line.emission
		#unique code to identify a budget, (incipit discriminate budgets recalled from different analysis)
		self.code = f'{self._incipit()}{self.standard_code}_{self.sample_code}_{self.target}_{self.emission.replace(" keV", "")}'

		#composition variation with iterative calculations
		self.original_composition = smpl.composition.original_certificate
		self.iterated_composition = {}
		
		#certificate
		self.cert_x, self.cert_ux = self.get_material_certification(M, sample_spectrum, sm_emission_line)
		self.asCRM = smpl.asCRM

		#infodata
		self.info_data = {'detector' : M.INAAnalysis.characterization.detector.name, 'irr_code' : M.INAAnalysis.irradiation.code, 'irr_datetime' : M.INAAnalysis.irradiation.datetime, 'irr_channel' : M.INAAnalysis.irradiation.channel_name, 'standard_path' : standard_spectrum.spectrumpath, 'sample_path' : sample_spectrum.spectrumpath}
		
		#flags
		if 'Use the Westcott formalism' in ():
			self.westcott_warning = True
		else:
			self.westcott_warning = False
		
		#counting positions
		self.counting_position_std = standard_spectrum.counting_position
		self.counting_position_sm = sample_spectrum.counting_position

		self.NAP = NetAreaCounts(M, standard_spectrum, sample_spectrum, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id)

		self.CS = CountingStatistics(M, standard_spectrum, sample_spectrum, st_emission_line, st_emiss_id, sm_emission_line, sm_emiss_id)

		self.SC = SampleComposition(M, st_emission_line, sm_emission_line)

		self.NF = NeutronFlux(M, self.standard_id, self.sample_id, st_emission_line, sm_emission_line)

		self.EF = Efficiency(M, standard_spectrum, sample_spectrum, st_emission_line, sm_emission_line)

		self.MSS = Masses_Comp(M, self.standard_id, self.sample_id, st_emission_line.target)

		self.BNK = Blank_Corr(M, self.standard_id, self.sample_id, sm_emission_line.target)

		self.FSS = Fission_Corr(M, self.sample_id, sm_emission_line, self.SC, self.NF)

		TTB = TotalBudget(self.NAP, self.CS, self.SC, self.NF, self.EF, self.MSS, self.BNK, self.FSS)
		
		self.y, self.uy, self.contributions_to_variance = TTB.x, TTB.ux, TTB.indexes

		self._contribution_list = TTB.contribution_list()

		self.likelihood = -1 #deprecated for the time being
		self.accepted_for_report = True

	def __eq__(self, other):
		return self.code == other.code
	
	def doe_check(self, values, uncertainties, variances, k=2):
		return doe_check(values, uncertainties, variances, k=2)
	
	def _incipit(self, disregard=True):
		if disregard:
			return 'A'
		elif self.method == 'relative':
			return 'R'
		return 'K'
	
	def k0_or_not(self, st_emission_line, sm_emission_line):
		if st_emission_line == sm_emission_line:
			return 'relative'
		return 'k0'
	
	def _update(self, INAAnalysis):
		sample = INAAnalysis.get_sample(self.sample_id)
		self.iterated_composition = sample.composition.certificate
		self.NF._update(sample, INAAnalysis.abundances_database)
		self.EF._update(sample, INAAnalysis.absorptions_database)
		self.FSS._update(sample)

		TTB = TotalBudget(self.NAP, self.CS, self.SC, self.NF, self.EF, self.MSS, self.BNK, self.FSS)
		
		self.y, self.uy, self.contributions_to_variance = TTB.x, TTB.ux, TTB.indexes

		self._contribution_list = TTB.contribution_list()
	
	def get_material_certification(self, M, sample_spectrum, sm_emission_line):
		smpl = M.INAAnalysis.get_sample(sample_spectrum.sample)
		return smpl.composition.certificate.get(sm_emission_line.target, (np.nan, np.nan))
		
	def get_covariance_matrix(self):
		cov_matrix = np.identity(len(self.parameters))
		for key, value in self.correlations.items():
			if key[0] != key[1]:
				cov_matrix[key[0], key[1]] = value
				cov_matrix[key[1], key[0]] = value
		return np.outer(self.data[:,1], self.data[:,1]) * cov_matrix
		
	def _get_uncertainty_components(self):
		if np.isnan(self.y):
			return np.nan, np.nan, np.nan
		statistics, positioning = 0.0, 0.0
		for contrib in self._contribution_list:
			if contrib[0] == 'net area ratio':
				statistics = contrib[1]
			elif contrib[0] == 'efficiency ratio':
				positioning = contrib[1]
		return statistics, positioning, 1 - (statistics + positioning)
		
	def _get_z_score_info(self):
		if np.isnan(self.cert_x) or np.isnan(self.cert_ux):
			return 2.5
		return (self.y - self.cert_x) / np.sqrt(np.power(self.uy, 2) + np.power(self.cert_ux, 2))
	
	def _auto_exclude(self, limit=0.0001):
		if self.likelihood < limit:
			self.accepted_for_report = False
		else:
			self.accepted_for_report = True


class Emission:
	"""
	Store information relative to identified emissions.
	"""
	def __init__(self, dtype, line):
		self.dtype, self.target, self.energy, self.emission = self._decrypt(dtype,line)
		self.line = line

	def _decrypt(self, dtype, line):
		if dtype == 'k0':
			target = line['target']
			energy = line['E']
			emission = f'{line["emitter"]}-{line["A"]}{self._state(line["state"])} {line["E"]:.1f} keV'
		return dtype, target, energy, emission

	def _state(self, identifier):
		if int(float(identifier)) == 2:
			return 'm'
		else:
			return ''
		
	def get_lambda(self, value, uncertainty, unit):
		units = {'Y':365.25 * 86400, 'D':86400, 'H':3600, 'M':60}
		lamb = np.log(2) / (value * units.get(unit, 1))
		return lamb, uncertainty / value * lamb

	def __eq__(self, other):
		return self.line.equals(other.line)


class GSourceEmission:
	"""
	Store information relative to identified gamma source emissions.
	"""
	def __init__(self, dtype, line):
		self.dtype, self.target, self.energy, self.emission = self._decrypt(dtype, line)
		self.line = line

	def _decrypt(self, dtype, line):
		dtype = 'characterization'
		target = line['emitter']
		energy = line['E']
		emission = f'{target} {line["E"]:.1f} keV'
		return dtype, target, energy, emission
	
	def __eq__(self, other):
		return self.line.equals(other.line)


def doe_check(values, uncertainties, contributions, k=2):
	#weighted average
	weights = 1 / np.power(uncertainties, 2)
	AVERG = np.sum(values * weights) / np.sum(weights)
	uAVERG = 1 / np.sum(weights * np.array([1/item[0] for item in contributions]))

	vals = values - AVERG
	absvals = np.abs(vals)
	stats_variances = np.power(uncertainties, 2) * [item[0] for item in contributions]
	Uvals = k * np.sqrt(stats_variances + uAVERG)
	response = absvals - Uvals
	return vals, Uvals, np.sum(response > 0.0)

def _get_composition_updated_improved(budget_list, M):
	#always material-wide
	#merge_with_prior = M.settings.get('merge with prior')
	#average_method = M.settings.get('average method')
	averaged_compositions = get_averages_compositions(budget_list)

	for nn, smpl in enumerate(M.INAAnalysis.samples_id):
		measured = averaged_compositions.get(smpl.composition.data[0][4].name, {})
		M.INAAnalysis.samples_id[nn].composition.certificate = {**M.INAAnalysis.samples_id[nn].composition.certificate, **measured}

def _get_likelihood(budget_list, max_tolerance_result=1.05, streamlined=False):
	AAA = set([ub.code for ub in budget_list])
	budget_list = [ub for ub in budget_list if 0 < ub.y < max_tolerance_result]
	budget_list = [ub for ub in budget_list if not np.isnan(ub.uy) and ub.uy > 0]

	BBB = set([ub.code for ub in budget_list])
	infodict = {'budget tested' : len(AAA), 'discarded' : AAA.difference(BBB), 'multiple assignment solver':[], 'duplicate assignment solver':[]}

	if streamlined:
		return budget_list, infodict

	averaged_compositions = get_averages_compositions(budget_list)

	for item in budget_list:
		averages = averaged_compositions.get(item.material, {})
		champion = averages.get(item.target, (np.nan, np.nan))[0]
		prob_B = 1 - statistics.norm.cdf(np.abs(item._get_z_score_info()))
		if not np.isnan(champion):
			prob_A = 1 - statistics.norm.cdf(np.abs((item.y - champion) / item.uy))
			item.likelihood = prob_A
		else:
			item.likelihood = prob_B

	#resolve conflicts!!!!
	duplicate_budget_list = [x for x in budget_list if budget_list.count(x) >= 2]
	duplicate_names = list(set([dupl.code for dupl in duplicate_budget_list]))

	#resolve multiple assignments of the same emitter
	budget_list = [x for x in budget_list if budget_list.count(x) == 1]
	duplicates_solved = [None] * len(duplicate_names)
	for item in duplicate_budget_list:
		idx = duplicate_names.index(item.code)
		if duplicates_solved[idx] is not None:
			if item.likelihood > duplicates_solved[idx].likelihood:
				duplicates_solved[idx] = item
		else:
			duplicates_solved[idx] = item

	infodict['multiple assignment solver'] = duplicates_solved

	sel_ids = [x.sel_id for x in budget_list]
	sel_ids = sorted(set([x for x in sel_ids if sel_ids.count(x) >= 2]))

	doubt_budget_list = [x for x in budget_list if x.sel_id in sel_ids]
	budget_list = [x for x in budget_list if x.sel_id not in sel_ids]

	#resolve doubts on same energy
	doubts_solved = [None] * len(sel_ids)
	for item in doubt_budget_list:
		idx = sel_ids.index(item.sel_id)
		if doubts_solved[idx] is not None:
			if item.likelihood > doubts_solved[idx].likelihood:
				doubts_solved[idx] = item
		else:
			doubts_solved[idx] = item

	infodict['duplicate assignment solver'] = doubts_solved

	#resolved budget list
	resolved_budget = budget_list + duplicates_solved + doubts_solved
	return resolved_budget, infodict

def get_averages_compositions(budget_list):
	#call of pandas dataframe for a better data management
	_all_target_list = pd.DataFrame([[ub.target, ub.y, ub.uy, ub.material] for ub in budget_list], columns=['target','y','uy', 'material'])

	averaged_compositions = {}

	for label in _all_target_list['material'].unique():
		_sub_target_list = _all_target_list[_all_target_list['material'] == label]

		v_counts = _sub_target_list['target'].value_counts()
		averages = {}

		for idx in v_counts.index:
			#if v_counts[idx] > 1:
			ave, sumofweights = np.average(_all_target_list[_all_target_list['target'] == idx]['y'], weights=np.power(_all_target_list[_all_target_list['target'] == idx]['uy'], 2), returned=True)
			averages[idx] = (ave, np.sqrt(sumofweights))
		averaged_compositions[label] = averages

	return averaged_compositions

def manage_spectra_files_and_get_infos(filename,limit,look_for_peaklist_option):
	"""
	Retrieve information from spectrum and peaklist file, deals with different situations
	"""
	peak_list, counts, start_acquisition, real_time, live_time, result, note = None, None, None, None, None, False, 'a generic error occurred!'
	allowed_extensions = ('.csv','.rpt','.asc','.chn')
	basename, extension = os.path.splitext(filename)
	source = []
	#.csv route
	if extension.lower() == allowed_extensions[0]:
		try:
			peak_list = openhyperlabfile(f'{basename}{extension}',limit)
			source.append((f'{basename}{extension}','peak list'))
		except:
			note = 'error while importing file'#maybe expand
		else:
			if True:#look_for_peaklist_option:
				try:#asc
					start_acquisition, real_time, live_time, counts = openASCfile(f'{basename}{allowed_extensions[2]}')
					source.append((f'{basename}{allowed_extensions[2]}','spectrum'))
					result = True
				except:
					note = 'some note'
				if not result:
					try:
						start_acquisition, real_time, live_time, counts = openchnfile(f'{basename}{allowed_extensions[3]}')
						source.append((f'{basename}{allowed_extensions[3]}','spectrum'))
						result = True
					except:
						note = 'no spectrum file found'#expand here
			else:
				note = 'you need spectrum information!'

	#.rpt route
	elif extension.lower() == allowed_extensions[1]:
		try:
			start_acquisition, real_time, live_time, peak_list = openrptfile(f'{basename}{extension}',limit)
			source.append((f'{basename}{extension}','peak list'))
			result = True
		except:
			note = 'error while importing file'
		else:
			if look_for_peaklist_option:
				try:#asc
					start_acquisition, real_time, live_time, counts = openASCfile(f'{basename}{allowed_extensions[2]}')
					source.append((f'{basename}{allowed_extensions[2]}','spectrum'))
				except:
					note = 'no spectrum file found'
				if counts is None:
					try:
						_start_acquisition, real_time, live_time, counts = openchnfile(f'{basename}{allowed_extensions[3]}')
						source.append((f'{basename}{allowed_extensions[3]}','spectrum'))
						if start_acquisition is None:
							start_acquisition = _start_acquisition
					except:
						note = 'no spectrum file found'#expand here
			else:
				note = 'imported anyway'

	#.asc route
	elif extension.lower() == allowed_extensions[2]:
		pass

	#.chn route
	elif extension.lower() == allowed_extensions[3]:
		pass

	return peak_list, counts, start_acquisition, real_time, live_time, result, note, source

def openhyperlabfile(file,limit=40):
	with open(file, newline='') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(spamreader)
		S = [[float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), float(row[10]), np.nan] for row in spamreader if float(row[9])/float(row[8])*100 < limit]
	return S

def openASCfile(file):
	with open(file,'r') as ascfile:
		filelines = [line.replace('\n','') for line in ascfile.readlines()]
	idx = 0
	for line in filelines[::-1]:
		if '#AcqStart=' in line:
			date_time = line.replace('#AcqStart=','')
		if '#TrueTime=' in line:
			real = float(line.replace('#TrueTime=',''))
		if '#LiveTime=' in line:
			live = float(line.replace('#LiveTime=',''))
			idx = filelines.index(line)
			break
	startcounting = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
	spectrum_counts = np.array([float(iks) for iks in filelines[:idx]])
	return startcounting, real, live, spectrum_counts

def openchnfile(file):
	import struct
	with open(file, "rb") as f:
		cs=4
		data = f.read(2)
		data = f.read(2)
		data = f.read(2)
		data = f.read(2)
		data = f.read(4)
		datev=struct.unpack('<I',data)
		real = int(datev[0])*20/1000
		data = f.read(4)
		datev=struct.unpack('<I',data)
		live = int(datev[0])*20/1000
		date = str(f.read(8),'utf-8')
		time = str(f.read(4),'utf-8')
		data = f.read(2)
		data = f.read(2)
		counts = []
		while data:
			data = f.read(cs)
			try:
				datev=struct.unpack('<I',data)
				counts.append(int(datev[0]))
			except:
				break
	if 65536 <= len(counts) < 131072:
		counts = counts[:65536]
	elif 32768 <= len(counts) < 65536:
		counts = counts[:32768]
	elif 16384 <= len(counts) < 32768:
		counts = counts[:16384]
	elif 8192 <= len(counts) < 16384:
		counts = counts[:8192]
	elif 8192 <= len(counts) < 16384:
		counts = counts[:8192]
	elif 4096 <= len(counts) < 8192:
		counts = counts[:4096]
	elif 2048 <= len(counts) < 4096:
		counts = counts[:2048]

	startcounting = datetime.datetime.strptime(f'{date[:-1]} {time}','%d%b%y %H%M')
	return startcounting, real, live, np.array(counts)

def openrptfile(file,limit):
	idx, ids = None, None
	with open(file, "r") as f:
		data = [line.replace('\r\n','').replace('\n','') for line in f.readlines()]
	for i in range(len(data)):
		if 'Start time:' in data[i]:
			startcounting = datetime.datetime.strptime(f'{data[i].split()[-2]} {data[i].split()[-1][:8]}','%d/%m/%Y %H:%M:%S')
			live = float(data[i+1].split()[-1])
			real = float(data[i+2].split()[-1])
		if '*' in data[i]:
			data[i] = data[i].replace(' ','')
			if '*UNIDENTIFIEDPEAKSUMMARY*' in data[i]:
				idx = i
			elif '*IDENTIFIEDPEAKSUMMARY*' in data[i]:
				ids = i
		if '\x00\x00\x00\x00\x00' in data[i]:
			data[i] = ''
		if '\x0c' in data[i]:
			data[i] = ''
		if 'Microsoft' in data[i]:
			data[i] = ''
		if 'Centroid' in data[i]:
			data[i] = ''
		if 'Channel' in data[i]:
			data[i] = ''
		if 'ORTEC' in data[i]:
			data[i] = ''
		if 'Page' in data[i]:
			data[i] = ''
		if 'Zero offset:' in data[i]:
			try:
				Z = float((data[i].split()[-2]).replace(',','.'))
			except:
				Z = 0
		if 'Gain:' in data[i]:
			try:
				G = float((data[i].split()[-2]).replace(',','.'))
			except:
				G = 1000000.0
		if 'Quadratic:' in data[i]:
			try:
				Q = float((data[i].split()[-2]).replace(',','.'))
			except:
				Q = 0.0
		if 'Spectrum' in data[i]:
			data[i] = ''
	peaklist = []
	if idx is not None:
		while True:
			try:
				values = data[idx+4].split()
				if values != '' and values != []:
					channel, energy, background, net_area, pinten, uncert, FWHM = float(values[0].replace(',','.')), float(values[1].replace(',','.')), float(values[2].replace(',','.')), float(values[3].replace(',','.')), float(values[4].replace(',','.')), float(values[5].replace(',','.')), float(values[6].replace(',','.'))
					if net_area > 0 and uncert >= 0 and uncert < limit:
						FW = (FWHM-Z)/G
						peaklist.append([channel, 0.0, energy, 0.0 , net_area, net_area*uncert/100, FW, background])
			except:
				break
			else:
				idx += 1
	if idx is not None:
		while True:
			try:
				values = data[ids+4].split()
				if values != '' and values != []:
					channel, energy, background, net_area, pinten, uncert, FWHM = float(values[1].replace(',','.')), float(values[2].replace(',','.')), float(values[3].replace(',','.')), float(values[4].replace(',','.')), float(values[5].replace(',','.')), float(values[6].replace(',','.')), float(values[7].replace(',','.')[:-1])
					if net_area > 0 and uncert >= 0 and uncert < limit:
						FW = (FWHM-Z)/G
						peaklist.append([channel, 0.0, energy, 0.0 , net_area, net_area*uncert/100, FW, background])
			except:
				break
			else:
				ids += 1
	peaklist.sort(key=lambda x:x[0])
	return startcounting, real, live, peaklist