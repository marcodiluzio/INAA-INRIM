# -*- coding: utf-8 -*-

"""
Classes to get various outputs from NAA analysis
"""

import xlsxwriter
import pickle


class ResultReport:
	"""Convenience class to transfer result data"""
	def __init__(self, result):
		self.results = result
		self.information = ''

	def _save(self, filename):
		with open(filename,'wb') as filesave:
			pickle.dump(self, filesave)


class BudgetAggregator:
    def __init__(self, sample_name):
        self.sample_name = sample_name
        self.code = f'Sample {self.sample_name}'
        self.budget_links = []
        self.index_row = 0
        self.max_value = None
        self.min_value = None

    def add_B(self, budget):
        self.budget_links.append(budget.code)

        V, U = budget.y, budget.uy
        if self.max_value is None or V + 3*U > self.max_value:
            self.max_value = V + 3*U

        if self.min_value is None or V - 3*U < self.min_value:
            self.min_value = V - 3*U

    def len(self):
        return len(self.budget_links)
    
    def _update(self, base):
        self.index_row = base + self.len()

        if self.max_value is None:
            self.max_value = 1
        if self.min_value is None:
            self.min_value = 0


class SingleBudget:
    def __init__(self, budget, wb):
        self._add_sheet(wb, budget)
        
    def _add_sheet(self, wb, budget):
        worksheet = wb.add_worksheet(budget.code)
        worksheet.hide_gridlines(self.hide_gridlines)
        
        worksheet.write(0, 0, 'Target', self.grey_fill)
        worksheet.write(0, 1, budget.target, self.grey_header)
        worksheet.write(0, 2, 'Emitter', self.grey_fill)
        Eemitter, Eenergy = budget.emission.replace(" keV", "").split()
        worksheet.write(0, 3, Eemitter, self.grey_header)
        worksheet.write(0, 4, 'E / keV', self.grey_fill)
        worksheet.write(0, 5, Eenergy, self.grey_header)

        worksheet.set_column('I:I', 14)
        worksheet.set_column('W:W', 14)
        worksheet.set_column('AK:AK', 14)
        worksheet.set_column('AY:AY', 14)
        worksheet.set_column('BM:BM', 14)
        worksheet.set_column('CA:CA', 14)
        worksheet.set_column('CO:CO', 14)
        worksheet.set_column('DC:DC', 14)

        worksheet.write(0, 14, 'Analysis information', self.grey_info)
        worksheet.write(0, 15, '', self.grey_fill)
        worksheet.write(0, 16, '', self.grey_fill)
        worksheet.write(0, 17, '', self.grey_fill)
        worksheet.write(0, 18, '', self.grey_fill)
        worksheet.write(0, 19, '', self.grey_fill)

        worksheet.write(0, 22, budget._version)

        worksheet.write(1, 14, 'method')
        worksheet.write(1, 15, budget.method)
        worksheet.write(2, 14, 'irradiation')
        worksheet.write(2, 15, budget.info_data['irr_code'])
        worksheet.write(3, 14, 'channel')
        worksheet.write(3, 15, budget.info_data['irr_channel'])
        worksheet.write(4, 14, 'detector')
        worksheet.write(4, 15, budget.info_data['detector'])

        worksheet.write(6, 14, 'measurement sample')
        worksheet.write(6, 15, budget.sample_id)
        worksheet.write(7, 14, 'mass / g')
        worksheet.write(7, 15, budget.MSS.m_a.value, self.font_datum)
        worksheet.write(8, 14, 'spectrum sample')
        worksheet.write(8, 15, budget.sample_code)
        worksheet.write(9, 14, 'counting position')
        worksheet.write(9, 15, budget.counting_position_sm)
        worksheet.write(10, 14, 'files')
        worksheet.write(10, 15, budget.info_data['sample_path'])
        worksheet.write(10, 16, ' ')
        
        worksheet.write(1, 17, 'comparator')
        worksheet.write(1, 18, budget.monitor)
        worksheet.write(2, 17, 'end date')
        worksheet.write(2, 18, budget.info_data['irr_datetime'], self.font_dateandtime)
        worksheet.write(3, 17, 'time / s')
        worksheet.write(3, 18, budget.CS.irr_time.value, self.font_integer)

        worksheet.write(6, 17, 'standard sample')
        worksheet.write(6, 18, budget.standard_id)
        worksheet.write(7, 17, 'mass / g')
        worksheet.write(7, 18, budget.MSS.m_m.value, self.font_datum)
        worksheet.write(8, 17, 'spectrum standard')
        worksheet.write(8, 18, budget.standard_code)
        worksheet.write(9, 17, 'counting position')
        worksheet.write(9, 18, budget.counting_position_std)
        worksheet.write(10, 17, 'files')
        worksheet.write(10, 18, budget.info_data['standard_path'])
        worksheet.write(10, 19, ' ')


        worksheet.write(2, 0, 'Quantity')
        worksheet.write(2, 2, 'Unit')
        worksheet.write(2, 3, 'Value')
        worksheet.write(2, 4, 'Std unc')
        worksheet.write(2, 5, 'Rel unc')
        worksheet.write(2, 8, 'Sensitivity coeff.')
        worksheet.write(2, 9, 'contribution to variance')

        worksheet.write_rich_string(3, 0, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(3, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(3, 3, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(3, 4, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(3, 5, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(3, 6, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(3, 7, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(3, 8, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(3, 9, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(3, 10, self.font_ital, 'I', ' (bar)')
        worksheet.write(3, 11, 'DoF')

        worksheet.write(4, 0, 'net area ratio')
        worksheet.write(4, 2, '1')
        worksheet.write(4, 3, budget.NAP.x, self.font_datum)
        worksheet.write(4, 4, budget.NAP.ux, self.font_datum)
        fml = f'=D6*D7*D8*D9*D10'
        worksheet.write(4, 8, fml, self.font_datum)
        worksheet.write(4, 11, budget.NAP._dof, self.font_integer)
        worksheet.write(5, 0, 'decay ratio')
        worksheet.write(5, 2, '1')
        worksheet.write(5, 3, budget.CS.x, self.font_datum)
        worksheet.write(5, 4, budget.CS.ux, self.font_datum)
        fml = f'=D5*D7*D8*D9*D10'
        worksheet.write(5, 8, fml, self.font_datum)
        worksheet.write(5, 11, budget.CS._dof, self.font_integer)
        worksheet.write(6, 0, 'k0 ratio')
        worksheet.write(6, 2, '1')
        worksheet.write(6, 3, budget.SC.x, self.font_datum)
        worksheet.write(6, 4, budget.SC.ux, self.font_datum)
        fml = f'=D5*D6*D8*D9*D10'
        worksheet.write(6, 8, fml, self.font_datum)
        worksheet.write(6, 11, budget.SC._dof, self.font_integer)
        worksheet.write(7, 0, 'neutron flux ratio')
        worksheet.write(7, 2, '1')
        worksheet.write(7, 3, budget.NF.x, self.font_datum)
        worksheet.write(7, 4, budget.NF.ux, self.font_datum)
        fml = f'=D5*D6*D7*D9*D10'
        worksheet.write(7, 8, fml, self.font_datum)
        worksheet.write(7, 11, budget.NF._dof, self.font_integer)
        worksheet.write(8, 0, 'efficiency ratio')
        worksheet.write(8, 2, '1')
        worksheet.write(8, 3, budget.EF.x, self.font_datum)
        worksheet.write(8, 4, budget.EF.ux, self.font_datum)
        fml = f'=D5*D6*D7*D8*D10'
        worksheet.write(8, 8, fml, self.font_datum)
        worksheet.write(8, 11, budget.EF._dof, self.font_integer)
        worksheet.write(9, 0, 'mass ratio')
        worksheet.write_rich_string(9, 2, 'g g', self.font_sups, '-1')
        worksheet.write(9, 3, budget.MSS.x, self.font_datum)
        worksheet.write(9, 4, budget.MSS.ux, self.font_datum)
        fml = f'=D5*D6*D7*D8*D9'
        worksheet.write(9, 8, fml, self.font_datum)
        worksheet.write(9, 11, budget.MSS._dof, self.font_integer)
        worksheet.write(10, 0, 'blank correction')
        worksheet.write_rich_string(10, 2, 'g g', self.font_sups, '-1')
        worksheet.write(10, 3, budget.BNK.x, self.font_datum)
        worksheet.write(10, 4, budget.BNK.ux, self.font_datum)
        fml = f'=1'
        worksheet.write(10, 8, fml, self.font_datum)
        worksheet.write(10, 11, budget.BNK._dof, self.font_integer)
        worksheet.write(11, 0, 'U fission correction')
        worksheet.write_rich_string(11, 2, 'g g', self.font_sups, '-1')
        worksheet.write(11, 3, budget.FSS.x, self.font_datum)
        worksheet.write(11, 4, budget.FSS.ux, self.font_datum)
        fml = f'=1'
        worksheet.write(11, 8, fml, self.font_datum)
        worksheet.write(11, 11, budget.FSS._dof, self.font_integer)

        for nn in range(8):
            fml = f'=IFERROR(ABS(E{4+nn+1}/D{4+nn+1}),"-")'
            worksheet.write(4+nn, 5, fml, self.font_pct)

            fml = f'=(I{4+nn+1}*E{4+nn+1}/E16)^2'
            worksheet.write(4+nn, 9, fml, self.font_pct)

            fml = f'=J{4+nn+1}'
            worksheet.write(4+nn, 10, fml, self.limit_cut)

        worksheet.conditional_format('K5:K12', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#c9291a', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(13, 0, 'Quantity')
        worksheet.write(13, 2, 'Unit')
        worksheet.write(13, 3, 'Value')
        worksheet.write(13, 4, 'Std unc')
        worksheet.write(13, 5, 'Rel unc')
        worksheet.write(13, 8, 'Exp unc (95%)')
        worksheet.write(13, 9, 'contribution to variance')
        worksheet.write(14, 0, 'Y', self.font_ital)
        worksheet.write_rich_string(14, 2, '[', self.font_ital, 'Y', ']')
        worksheet.write(14, 3, 'y', self.font_ital)
        worksheet.write_rich_string(14, 4, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(14, 5, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(14, 8, self.font_ital, 'U', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(14, 9, self.font_ital, 'I', ' / %')
        worksheet.write(14, 11, 'DoF')

        worksheet.write_rich_string(15, 0, self.font_ital, 'w', self.font_subs, 'smp i')
        worksheet.write_rich_string(15, 2, 'g g', self.font_sups, '-1')

        fml = '=D5*D6*D7*D8*D9*D10-D11-D12'
        worksheet.write(15, 3, fml, self.font_result)

        fml = '{=sqrt(MMULT(MMULT(TRANSPOSE(I5:I12),TRANSPOSE(E5:E12)*{1,0,0,0,0,0,0,0;0,1,0,0,0,0,0,0;0,0,1,0,0,0,0,0;0,0,0,1,0,0,0,0;0,0,0,0,1,0,0,0;0,0,0,0,0,1,0,0;0,0,0,0,0,0,1,0;0,0,0,0,0,0,0,1}*E5:E12),I5:I12))}'
        worksheet.write(15, 4, fml, self.font_uncresult)

        fml = '=IFERROR(ABS(E16/D16),"-")'
        worksheet.write(15, 5, fml, self.font_pct)

        fml = '=E16*TINV(1-0.95,L16)'
        worksheet.write(15, 8, fml, self.font_datum)

        fml = '=SUM(J5:J12)'
        worksheet.write(15, 9, fml, self.font_pct)

        fml = '=INT(E16^4/((E5*I5)^4/L5+(E6*I6)^4/L6+(E7*I7)^4/L7+(E8*I8)^4/L8+(E9*I9)^4/L9+(E10*I10)^4/L10+(E11*I11)^4/L11+(E12*I12)^4/L12))'
        worksheet.write(15, 11, fml, self.font_integer)

        worksheet.write(16, 0, 'ref value', self.font_grayit)
        worksheet.write_rich_string(16, 2, 'g g', self.font_sups, '-1')

        #condition
        if budget.cert_x > 0.0:
            worksheet.write(16, 3, budget.cert_x, self.font_greyresult)
            worksheet.write(16, 4, budget.cert_ux, self.font_greyuncresult)
        else:
            worksheet.write(16, 3, '-', self.font_greyresult)
            worksheet.write(16, 4, '-', self.font_greyuncresult)

        worksheet.write(17, 0, 'Z score', self.font_grayit)
        worksheet.write(17, 2, '1')

        fml = '=IFERROR((D16-D17)/SQRT(E16^2+E17^2),"-")'
        worksheet.write(17, 3, fml, self.font_zscore)

        #MINI BUDGETS

        #NET AREA RATIO
        worksheet.write(21, 0, '=A5', self.grey_info)
        worksheet.write(21, 1, '', self.grey_fill)
        worksheet.write(21, 2, '', self.grey_fill)
        worksheet.write(21, 3, '', self.grey_fill)
        worksheet.write(21, 4, '', self.grey_fill)
        worksheet.write(21, 5, '', self.grey_fill)
        worksheet.write(21, 8, '', self.grey_fill)
        worksheet.write(21, 9, '', self.grey_fill)
        worksheet.write(21, 10, '', self.grey_fill)
        worksheet.write(21, 11, '', self.grey_fill)

        worksheet.write(22, 0, 'Quantity')
        worksheet.write(22, 2, 'Unit')
        worksheet.write(22, 3, 'Value')
        worksheet.write(22, 4, 'Std unc')
        worksheet.write(22, 5, 'Rel unc')
        worksheet.write(22, 8, 'Sensitivity coeff.')
        worksheet.write(22, 9, 'contribution to variance')

        worksheet.write_rich_string(23, 0, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11, 'DoF')

        #parameters
        worksheet.write_rich_string(24, 0, self.font_ital, 'n', self.font_subs, 'p smp')
        worksheet.write(24, 2, '1')
        worksheet.write(24, 8, '=1/(D28-D29-D30)', self.font_datum)

        worksheet.write_rich_string(25, 0, self.font_ital, 'n', self.font_subs, 'bkg smp')
        worksheet.write(25, 2, '1')
        worksheet.write(25, 8, '=-1/(D28-D29-D30)', self.font_datum)

        worksheet.write_rich_string(26, 0, self.font_ital, 'n', self.font_subs, 'intrf smp')
        worksheet.write(26, 2, '1')
        worksheet.write(26, 8, '=-1/(D28-D29-D30)', self.font_datum)

        worksheet.write_rich_string(27, 0, self.font_ital, 'n', self.font_subs, 'p std')
        worksheet.write(27, 2, '1')
        worksheet.write(27, 8, '=-(D25-D26-D27)/(D28-D29-D30)^2', self.font_datum)

        worksheet.write_rich_string(28, 0, self.font_ital, 'n', self.font_subs, 'bkg std')
        worksheet.write(28, 2, '1')
        worksheet.write(28, 8, '=(D25-D26-D27)/(D28-D29-D30)^2', self.font_datum)

        worksheet.write_rich_string(29, 0, self.font_ital, 'n', self.font_subs, 'intrf std')
        worksheet.write(29, 2, '1')
        worksheet.write(29, 8, '=(D25-D26-D27)/(D28-D29-D30)^2', self.font_datum)

        for nni, param in enumerate(budget.NAP.parameters):
            worksheet.write(24+nni, 3, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(E{24+nni+1}/D{24+nni+1}),"-")'
            worksheet.write(24+nni, 5, fml, self.font_pct)

            fml = f'=(I{24+nni+1}*E{24+nni+1}/E34)^2'
            worksheet.write(24+nni, 9, fml, self.font_pct)
            fml = f'=J{24+nni+1}'
            worksheet.write(24+nni, 10, fml, self.limit_cut)
            worksheet.write(24+nni, 11, param._dof, self.font_inputdof)

        worksheet.conditional_format('K25:K30', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(31, 0, 'Quantity')
        worksheet.write(31, 2, 'Unit')
        worksheet.write(31, 3, 'Value')
        worksheet.write(31, 4, 'Std unc')
        worksheet.write(31, 5, 'Rel unc')
        worksheet.write(31, 9, 'contribution to variance')
        worksheet.write(32, 0, 'Y', self.font_ital)
        worksheet.write_rich_string(32, 2, '[', self.font_ital, 'Y', ']')
        worksheet.write(32, 3, 'y', self.font_ital)
        worksheet.write_rich_string(32, 4, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(32, 5, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(32, 9, self.font_ital, 'I', ' / %')
        worksheet.write(32, 11, 'DoF')

        worksheet.write(33, 0, '=A5')
        worksheet.write(33, 2, '=C5')
        fml = '=(D25-D26-D27)/(D28-D29-D30)'
        worksheet.write(33, 3, fml, self.font_datum)

        fml = '{=sqrt(MMULT(MMULT(TRANSPOSE(I25:I30),TRANSPOSE(E25:E30)*'+budget.NAP._corr_matrix()+'*E25:E30),I25:I30))}'
        worksheet.write(33, 4, fml, self.font_datum)

        fml = '=IFERROR(ABS(E34/D34),"-")'
        worksheet.write(33, 5, fml, self.font_pct)

        fml = '=SUM(J25:J30)'
        worksheet.write(33, 9, fml, self.font_pct)

        fml = '=INT(E34^4/((E25*I25)^4/L25+(E26*I26)^4/L26+(E27*I27)^4/L27+(E28*I28)^4/L28+(E29*I29)^4/L29+(E30*I30)^4/L30))'
        worksheet.write(33, 11, fml, self.font_integer)

        #DECAY RATIO
        worksheet.write(21, 0+14, '=A6', self.grey_info)
        worksheet.write(21, 1+14, '', self.grey_fill)
        worksheet.write(21, 2+14, '', self.grey_fill)
        worksheet.write(21, 3+14, '', self.grey_fill)
        worksheet.write(21, 4+14, '', self.grey_fill)
        worksheet.write(21, 5+14, '', self.grey_fill)
        worksheet.write(21, 8+14, '', self.grey_fill)
        worksheet.write(21, 9+14, '', self.grey_fill)
        worksheet.write(21, 10+14, '', self.grey_fill)
        worksheet.write(21, 11+14, '', self.grey_fill)

        worksheet.write(22, 0+14, 'Quantity')
        worksheet.write(22, 2+14, 'Unit')
        worksheet.write(22, 3+14, 'Value')
        worksheet.write(22, 4+14, 'Std unc')
        worksheet.write(22, 5+14, 'Rel unc')
        worksheet.write(22, 8+14, 'Sensitivity coeff.')
        worksheet.write(22, 9+14, 'contribution to variance')

        worksheet.write_rich_string(23, 0+14, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+14, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+14, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+14, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+14, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+14, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+14, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+14, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+14, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+14, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+14, 'DoF')

        #parameters
        worksheet.write_rich_string(24, 0+14, self.font_ital, 't', self.font_subs, 'irr')
        worksheet.write(24, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*(R25+S25)))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*(R25+S25)))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R25+S25)','(R25-S25)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=0'
            fmlm = '=0'
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(24, 6+14, fmlp)
        worksheet.write(24, 7+14, fmlm)
        
        worksheet.write_rich_string(25, 0+14, self.font_sym, 'l', self.font_subs, 'smp (a)')
        worksheet.write_rich_string(25, 2+14, 's', self.font_sups, '-1')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=((R26+S26)*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-(R26+S26)*R25))*(1-EXP(-(R26+S26)*R27))*R28)*EXP(((R26+S26)-R34)*R32+(R26+S26)*R29)'
            fmlm = fmlp.replace('(R26+S26)','(R26-S26)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*R31*(1-EXP(-(R26+S26)*R30)))/(R30*R28*(1-EXP(-(R26+S26)*R27)))*EXP(R33*(R31/R30-R28/R27))*EXP((R26+S26)*R29)'
            fmlm = fmlp.replace('(R26+S26)','(R26-S26)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(25, 6+14, fmlp)
        worksheet.write(25, 7+14, fmlm)

        worksheet.write_rich_string(26, 0+14, self.font_ital, 't', self.font_subs, 'c smp')
        worksheet.write(26, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*(R27+S27)*EXP(R33*(1-R28/(R27+S27)))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*(R27+S27)))*R28)*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R27+S27)','(R27-S27)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=((R27+S27)*R31*(1-EXP(-R26*R30)))/(R30*R28*(1-EXP(-R26*(R27+S27))))*EXP(R33*(R31/R30-R28/(R27+S27)))*EXP(R26*R29)'
            fmlm = fmlp.replace('(R27+S27)','(R27-S27)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(26, 6+14, fmlp)
        worksheet.write(26, 7+14, fmlm)
        
        worksheet.write_rich_string(27, 0+14, self.font_ital, 't', self.font_subs, 'l smp')
        worksheet.write(27, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-(R28+S28)/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*(R28+S28))*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R28+S28)','(R28-S28)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*R31*(1-EXP(-R26*R30)))/(R30*(R28+S28)*(1-EXP(-R26*R27)))*EXP(R33*(R31/R30-(R28+S28)/R27))*EXP(R26*R29)'
            fmlm = fmlp.replace('(R28+S28)','(R28-S28)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(27, 6+14, fmlp)
        worksheet.write(27, 7+14, fmlm)

        worksheet.write_rich_string(28, 0+14, self.font_sym, 'D', self.font_ital, 't', self.font_subs, 'd')
        worksheet.write(28, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*(R29+S29))'
            fmlm = fmlp.replace('(R29+S29)','(R29-S29)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*R31*(1-EXP(-R26*R30)))/(R30*R28*(1-EXP(-R26*R27)))*EXP(R33*(R31/R30-R28/R27))*EXP(R26*(R29+S29))'
            fmlm = fmlp.replace('(R29+S29)','(R29-S29)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(28, 6+14, fmlp)
        worksheet.write(28, 7+14, fmlm)

        worksheet.write_rich_string(29, 0+14, self.font_ital, 't', self.font_subs, 'c std')
        worksheet.write(29, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*(R30+S30)))*R31)/(R34*(R30+S30)*EXP(R33*(1-R31/(R30+S30)))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R30+S30)','(R30-S30)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*R31*(1-EXP(-R26*(R30+S30))))/((R30+S30)*R28*(1-EXP(-R26*R27)))*EXP(R33*(R31/(R30+S30)-R28/R27))*EXP(R26*R29)'
            fmlm = fmlp.replace('(R30+S30)','(R30-S30)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(29, 6+14, fmlp)
        worksheet.write(29, 7+14, fmlm)

        worksheet.write_rich_string(30, 0+14, self.font_ital, 't', self.font_subs, 'l std')
        worksheet.write(30, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*(R31+S31))/(R34*R30*EXP(R33*(1-(R31+S31)/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R31+S31)','(R31-S31)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*(R31+S31)*(1-EXP(-R26*R30)))/(R30*R28*(1-EXP(-R26*R27)))*EXP(R33*((R31+S31)/R30-R28/R27))*EXP(R26*R29)'
            fmlm = fmlp.replace('(R31+S31)','(R31-S31)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(30, 6+14, fmlp)
        worksheet.write(30, 7+14, fmlm)

        worksheet.write_rich_string(31, 0+14, self.font_ital, 't', self.font_subs, 'd std')
        worksheet.write(31, 2+14, 's')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*(R32+S32)+R26*R29)'
            fmlm = fmlp.replace('(R32+S32)','(R32-S32)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=0'
            fmlm = fmlp.replace('(R32+S32)','(R32-S32)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(31, 6+14, fmlp)
        worksheet.write(31, 7+14, fmlm)

        worksheet.write(32, 0+14, 'm', self.font_sym)
        worksheet.write(32, 2+14, '1')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP((R33+S33)*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP((R33+S33)*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*R29)'
            fmlm = fmlp.replace('(R33+S33)','(R33-S33)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=(R27*R31*(1-EXP(-R26*R30)))/(R30*R28*(1-EXP(-R26*R27)))*EXP((R33+S33)*(R31/R30-R28/R27))*EXP(R26*R29)'
            fmlm = fmlp.replace('(R33+S33)','(R33-S33)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(32, 6+14, fmlp)
        worksheet.write(32, 7+14, fmlm)

        worksheet.write_rich_string(33, 0+14, self.font_sym, 'l', self.font_subs, 'std (m)')
        worksheet.write_rich_string(33, 2+14, 's', self.font_sups, '-1')
        if budget.CS._model() == 'k0_direct':
            fmlp = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-(R34+S34)*R25))*(1-EXP(-(R34+S34)*R30))*R31)/((R34+S34)*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-(R34+S34))*R32+R26*R29)'
            fmlm = fmlp.replace('(R34+S34)','(R34-S34)')
        elif budget.CS._model() == 'relative_direct':
            fmlp = '=0'
            fmlm = fmlp.replace('(R34+S34)','(R34-S34)')
        else:
            fmlp = '=0'
            fmlm = '=0'
        worksheet.write(33, 6+14, fmlp)
        worksheet.write(33, 7+14, fmlm)

        for nni, param in enumerate(budget.CS.parameters):
            worksheet.write(24+nni, 3+14, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+14, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(S{24+nni+1}/R{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+14, fml, self.font_pct)

            fml = f'=(U{24+nni+1}-V{24+nni+1})/(2*S{24+nni+1}+1E-24)'
            worksheet.write(24+nni, 8+14, fml, self.font_datum)

            fml = f'=(W{24+nni+1}*S{24+nni+1}/S38)^2'
            worksheet.write(24+nni, 9+14, fml, self.font_pct)
            fml = f'=X{24+nni+1}'
            worksheet.write(24+nni, 10+14, fml, self.limit_cut)
            worksheet.write(24+nni, 11+14, param._dof, self.font_inputdof)

        worksheet.conditional_format('Y25:Y34', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(35, 0+14, 'Quantity')
        worksheet.write(35, 2+14, 'Unit')
        worksheet.write(35, 3+14, 'Value')
        worksheet.write(35, 4+14, 'Std unc')
        worksheet.write(35, 5+14, 'Rel unc')
        worksheet.write(35, 9+14, 'contribution to variance')
        worksheet.write(36, 0+14, 'Y', self.font_ital)
        worksheet.write_rich_string(36, 2+14, '[', self.font_ital, 'Y', ']')
        worksheet.write(36, 3+14, 'y', self.font_ital)
        worksheet.write_rich_string(36, 4+14, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(36, 5+14, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(36, 9+14, self.font_ital, 'I', ' / %')
        worksheet.write(36, 11+14, 'DoF')

        worksheet.write(37, 0+14, '=A6')
        worksheet.write(37, 2+14, '=C6')
        if budget.CS._model() == 'k0_direct':
            fml = '=(R26*R27*EXP(R33*(1-R28/R27))*(1-EXP(-R34*R25))*(1-EXP(-R34*R30))*R31)/(R34*R30*EXP(R33*(1-R31/R30))*(1-EXP(-R26*R25))*(1-EXP(-R26*R27))*R28)*EXP((R26-R34)*R32+R26*R29)'
        elif budget.CS._model() == 'relative_direct':
            fml = '=(R27*EXP(R33*(1-R28/R27))*R31*(1-EXP(-R26*R30)))/(R30*EXP(R33*(1-R31/R30))*R28*(1-EXP(-R26*R27)))*EXP(R26*R29)'
        else:
            fml = 'ERROR'
        worksheet.write(37, 3+14, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(W25:W34),TRANSPOSE(S25:S34)*{budget.CS._corr_matrix()}*S25:S34),W25:W34)){cpth}'
        worksheet.write(37, 4+14, fml, self.font_datum)

        fml = '=IFERROR(ABS(S38/R38),"-")'
        worksheet.write(37, 5+14, fml, self.font_pct)

        fml = '=SUM(X25:X34)'
        worksheet.write(37, 9+14, fml, self.font_pct)

        fml = '=INT(S38^4/((S25*W25)^4/Z25+(S26*W26)^4/Z26+(S27*W27)^4/Z27+(S28*W28)^4/Z28+(S29*W29)^4/Z29+(S30*W30)^4/Z30+(S31*W31)^4/Z31+(S32*W32)^4/Z32+(S33*W33)^4/Z33+(S34*W34)^4/Z34))'
        worksheet.write(37, 11+14, fml, self.font_integer)

        #K0 RATIO
        worksheet.write(21, 0+28, '=A7', self.grey_info)
        worksheet.write(21, 1+28, '', self.grey_fill)
        worksheet.write(21, 2+28, '', self.grey_fill)
        worksheet.write(21, 3+28, '', self.grey_fill)
        worksheet.write(21, 4+28, '', self.grey_fill)
        worksheet.write(21, 5+28, '', self.grey_fill)
        worksheet.write(21, 8+28, '', self.grey_fill)
        worksheet.write(21, 9+28, '', self.grey_fill)
        worksheet.write(21, 10+28, '', self.grey_fill)
        worksheet.write(21, 11+28, '', self.grey_fill)

        worksheet.write(22, 0+28, 'Quantity')
        worksheet.write(22, 2+28, 'Unit')
        worksheet.write(22, 3+28, 'Value')
        worksheet.write(22, 4+28, 'Std unc')
        worksheet.write(22, 5+28, 'Rel unc')
        worksheet.write(22, 8+28, 'Sensitivity coeff.')
        worksheet.write(22, 9+28, 'contribution to variance')

        worksheet.write_rich_string(23, 0+28, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+28, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+28, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+28, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+28, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+28, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+28, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+28, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+28, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+28, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+28, 'DoF')

        if budget.SC._model() == 'k0_direct':
            _model = '0'
        elif budget.SC._model() == 'relative_direct':
            _model = '=(AF45*(AF25*AF26+AF27*AF28+AF29*AF30+AF31*AF32+AF33*AF34+AF35*AF36+AF37*AF38+AF39*AF40+AF41*AF42+AF43*AF44))/(AF25*(AF45*AF26+AF46*AF28+AF47*AF30+AF48*AF32+AF49*AF34+AF50*AF36+AF51*AF38+AF52*AF40+AF53*AF42+AF54*AF44))'
        else:
            _model = 'ERROR'

        #parameters
        worksheet.write_rich_string(24, 0+28, self.font_sym, 'q', self.font_subs, 'i smp')
        worksheet.write_rich_string(24, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF25','(AF25+AG25)')
        fmlm = fmlp.replace('(AF25+AG25)','(AF25-AG25)')
        worksheet.write(24, 6+28, fmlp)
        worksheet.write(24, 7+28, fmlm)
        
        worksheet.write_rich_string(25, 0+28, self.font_ital, 'M', self.font_subs, 'i')
        worksheet.write_rich_string(25, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF26','(AF26+AG26)')
        fmlm = fmlp.replace('(AF26+AG26)','(AF26-AG26)')
        worksheet.write(25, 6+28, fmlp)
        worksheet.write(25, 7+28, fmlm)

        worksheet.write_rich_string(26, 0+28, self.font_sym, 'q', self.font_subs, 'i+1 smp')
        worksheet.write_rich_string(26, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF27','(AF27+AG27)')
        fmlm = fmlp.replace('(AF27+AG27)','(AF27-AG27)')
        worksheet.write(26, 6+28, fmlp)
        worksheet.write(26, 7+28, fmlm)
        
        worksheet.write_rich_string(27, 0+28, self.font_ital, 'M', self.font_subs, 'i+1')
        worksheet.write_rich_string(27, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF28','(AF28+AG28)')
        fmlm = fmlp.replace('(AF28+AG28)','(AF28-AG28)')
        worksheet.write(27, 6+28, fmlp)
        worksheet.write(27, 7+28, fmlm)

        worksheet.write_rich_string(28, 0+28, self.font_sym, 'q', self.font_subs, 'i+2 smp')
        worksheet.write_rich_string(28, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF29','(AF29+AG29)')
        fmlm = fmlp.replace('(AF29+AG29)','(AF29-AG29)')
        worksheet.write(28, 6+28, fmlp)
        worksheet.write(28, 7+28, fmlm)

        worksheet.write_rich_string(29, 0+28, self.font_ital, 'M', self.font_subs, 'i+2')
        worksheet.write_rich_string(29, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF30','(AF30+AG30)')
        fmlm = fmlp.replace('(AF30+AG30)','(AF30-AG30)')
        worksheet.write(29, 6+28, fmlp)
        worksheet.write(29, 7+28, fmlm)

        worksheet.write_rich_string(30, 0+28, self.font_sym, 'q', self.font_subs, 'i+3 smp')
        worksheet.write_rich_string(30, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF31','(AF31+AG31)')
        fmlm = fmlp.replace('(AF31+AG31)','(AF31-AG31)')
        worksheet.write(30, 6+28, fmlp)
        worksheet.write(30, 7+28, fmlm)

        worksheet.write_rich_string(31, 0+28, self.font_ital, 'M', self.font_subs, 'i+3')
        worksheet.write_rich_string(31, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF32','(AF32+AG32)')
        fmlm = fmlp.replace('(AF32+AG32)','(AF32-AG32)')
        worksheet.write(31, 6+28, fmlp)
        worksheet.write(31, 7+28, fmlm)

        worksheet.write_rich_string(32, 0+28, self.font_sym, 'q', self.font_subs, 'i+4 smp')
        worksheet.write_rich_string(32, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF33','(AF33+AG33)')
        fmlm = fmlp.replace('(AF33+AG33)','(AF33-AG33)')
        worksheet.write(32, 6+28, fmlp)
        worksheet.write(32, 7+28, fmlm)

        worksheet.write_rich_string(33, 0+28, self.font_ital, 'M', self.font_subs, 'i+4')
        worksheet.write_rich_string(33, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF34','(AF34+AG34)')
        fmlm = fmlp.replace('(AF34+AG34)','(AF34-AG34)')
        worksheet.write(33, 6+28, fmlp)
        worksheet.write(33, 7+28, fmlm)

        worksheet.write_rich_string(34, 0+28, self.font_sym, 'q', self.font_subs, 'i+5 smp')
        worksheet.write_rich_string(34, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF35','(AF35+AG35)')
        fmlm = fmlp.replace('(AF35+AG35)','(AF35-AG35)')
        worksheet.write(34, 6+28, fmlp)
        worksheet.write(34, 7+28, fmlm)

        worksheet.write_rich_string(35, 0+28, self.font_ital, 'M', self.font_subs, 'i+5')
        worksheet.write_rich_string(35, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF36','(AF36+AG36)')
        fmlm = fmlp.replace('(AF36+AG36)','(AF36-AG36)')
        worksheet.write(35, 6+28, fmlp)
        worksheet.write(35, 7+28, fmlm)

        worksheet.write_rich_string(36, 0+28, self.font_sym, 'q', self.font_subs, 'i+6 smp')
        worksheet.write_rich_string(36, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF37','(AF37+AG37)')
        fmlm = fmlp.replace('(AF37+AG37)','(AF37-AG37)')
        worksheet.write(36, 6+28, fmlp)
        worksheet.write(36, 7+28, fmlm)

        worksheet.write_rich_string(37, 0+28, self.font_ital, 'M', self.font_subs, 'i+6')
        worksheet.write_rich_string(37, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF38','(AF38+AG38)')
        fmlm = fmlp.replace('(AF38+AG38)','(AF38-AG38)')
        worksheet.write(37, 6+28, fmlp)
        worksheet.write(37, 7+28, fmlm)

        worksheet.write_rich_string(38, 0+28, self.font_sym, 'q', self.font_subs, 'i+7 smp')
        worksheet.write_rich_string(38, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF39','(AF39+AG39)')
        fmlm = fmlp.replace('(AF39+AG39)','(AF39-AG39)')
        worksheet.write(38, 6+28, fmlp)
        worksheet.write(38, 7+28, fmlm)

        worksheet.write_rich_string(39, 0+28, self.font_ital, 'M', self.font_subs, 'i+7')
        worksheet.write_rich_string(39, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF40','(AF40+AG40)')
        fmlm = fmlp.replace('(AF40+AG40)','(AF40-AG40)')
        worksheet.write(39, 6+28, fmlp)
        worksheet.write(39, 7+28, fmlm)

        worksheet.write_rich_string(40, 0+28, self.font_sym, 'q', self.font_subs, 'i+8 smp')
        worksheet.write_rich_string(40, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF41','(AF41+AG41)')
        fmlm = fmlp.replace('(AF41+AG41)','(AF41-AG41)')
        worksheet.write(40, 6+28, fmlp)
        worksheet.write(40, 7+28, fmlm)

        worksheet.write_rich_string(41, 0+28, self.font_ital, 'M', self.font_subs, 'i+8')
        worksheet.write_rich_string(41, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF42','(AF42+AG42)')
        fmlm = fmlp.replace('(AF42+AG42)','(AF42-AG42)')
        worksheet.write(41, 6+28, fmlp)
        worksheet.write(41, 7+28, fmlm)

        worksheet.write_rich_string(42, 0+28, self.font_sym, 'q', self.font_subs, 'i+9 smp')
        worksheet.write_rich_string(42, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF43','(AF43+AG43)')
        fmlm = fmlp.replace('(AF43+AG43)','(AF43-AG43)')
        worksheet.write(42, 6+28, fmlp)
        worksheet.write(42, 7+28, fmlm)

        worksheet.write_rich_string(43, 0+28, self.font_ital, 'M', self.font_subs, 'i+9')
        worksheet.write_rich_string(43, 2+28, 'g mol', self.font_sups, '-1')
        fmlp = _model.replace('AF44','(AF44+AG44)')
        fmlm = fmlp.replace('(AF44+AG44)','(AF44-AG44)')
        worksheet.write(43, 6+28, fmlp)
        worksheet.write(43, 7+28, fmlm)

        worksheet.write_rich_string(44, 0+28, self.font_sym, 'q', self.font_subs, 'i std')
        worksheet.write_rich_string(44, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF45','(AF45+AG45)')
        fmlm = fmlp.replace('(AF45+AG45)','(AF45-AG45)')
        worksheet.write(44, 6+28, fmlp)
        worksheet.write(44, 7+28, fmlm)

        worksheet.write_rich_string(45, 0+28, self.font_sym, 'q', self.font_subs, 'i+1 std')
        worksheet.write_rich_string(45, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF46','(AF46+AG46)')
        fmlm = fmlp.replace('(AF46+AG46)','(AF46-AG46)')
        worksheet.write(45, 6+28, fmlp)
        worksheet.write(45, 7+28, fmlm)

        worksheet.write_rich_string(46, 0+28, self.font_sym, 'q', self.font_subs, 'i+2 std')
        worksheet.write_rich_string(46, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF47','(AF47+AG47)')
        fmlm = fmlp.replace('(AF47+AG47)','(AF47-AG47)')
        worksheet.write(46, 6+28, fmlp)
        worksheet.write(46, 7+28, fmlm)

        worksheet.write_rich_string(47, 0+28, self.font_sym, 'q', self.font_subs, 'i+3 std')
        worksheet.write_rich_string(47, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF48','(AF48+AG48)')
        fmlm = fmlp.replace('(AF48+AG48)','(AF48-AG48)')
        worksheet.write(47, 6+28, fmlp)
        worksheet.write(47, 7+28, fmlm)

        worksheet.write_rich_string(48, 0+28, self.font_sym, 'q', self.font_subs, 'i+4 std')
        worksheet.write_rich_string(48, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF49','(AF49+AG49)')
        fmlm = fmlp.replace('(AF49+AG49)','(AF49-AG49)')
        worksheet.write(48, 6+28, fmlp)
        worksheet.write(48, 7+28, fmlm)

        worksheet.write_rich_string(49, 0+28, self.font_sym, 'q', self.font_subs, 'i+5 std')
        worksheet.write_rich_string(49, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF50','(AF50+AG50)')
        fmlm = fmlp.replace('(AF50+AG50)','(AF50-AG50)')
        worksheet.write(49, 6+28, fmlp)
        worksheet.write(49, 7+28, fmlm)

        worksheet.write_rich_string(50, 0+28, self.font_sym, 'q', self.font_subs, 'i+6 std')
        worksheet.write_rich_string(50, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF51','(AF51+AG51)')
        fmlm = fmlp.replace('(AF51+AG51)','(AF51-AG51)')
        worksheet.write(50, 6+28, fmlp)
        worksheet.write(50, 7+28, fmlm)

        worksheet.write_rich_string(51, 0+28, self.font_sym, 'q', self.font_subs, 'i+7 std')
        worksheet.write_rich_string(51, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF52','(AF52+AG52)')
        fmlm = fmlp.replace('(AF52+AG52)','(AF52-AG52)')
        worksheet.write(51, 6+28, fmlp)
        worksheet.write(51, 7+28, fmlm)

        worksheet.write_rich_string(52, 0+28, self.font_sym, 'q', self.font_subs, 'i+8 std')
        worksheet.write_rich_string(52, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF53','(AF53+AG53)')
        fmlm = fmlp.replace('(AF53+AG53)','(AF53-AG53)')
        worksheet.write(52, 6+28, fmlp)
        worksheet.write(52, 7+28, fmlm)

        worksheet.write_rich_string(53, 0+28, self.font_sym, 'q', self.font_subs, 'i+9 std')
        worksheet.write_rich_string(53, 2+28, 'mol mol', self.font_sups, '-1')
        fmlp = _model.replace('AF54','(AF54+AG54)')
        fmlm = fmlp.replace('(AF54+AG54)','(AF54-AG54)')
        worksheet.write(53, 6+28, fmlp)
        worksheet.write(53, 7+28, fmlm)

        worksheet.write_rich_string(54, 0+28, self.font_ital, 'k', self.font_subs, '0 Au', '(m)')
        worksheet.write(54, 2+28, '1')
        if budget.SC._model() == 'k0_direct':
            fml = '=1/AF56'
        elif budget.SC._model() == 'relative_direct':
            fml = '=0'
        else:
            fml = '=0'
        worksheet.write(54, 8+28, fml)
        
        worksheet.write_rich_string(55, 0+28, self.font_ital, 'k', self.font_subs, '0 Au', '(a)')
        worksheet.write(55, 2+28, '1')
        if budget.SC._model() == 'k0_direct':
            fml = '=-AF55/AF56^2'
        elif budget.SC._model() == 'relative_direct':
            fml = '=0'
        else:
            fml = '=0'
        worksheet.write(55, 8+28, fml)

        for nni, param in enumerate(budget.SC.parameters):
            worksheet.write(24+nni, 3+28, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+28, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(AG{24+nni+1}/AF{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+28, fml, self.font_pct)

            if nni + 2 < len(budget.SC.parameters):
                fml = f'=(AI{24+nni+1}-AJ{24+nni+1})/(2*AG{24+nni+1}+1E-24)'
                worksheet.write(24+nni, 8+28, fml, self.font_datum)

            fml = f'=(AK{24+nni+1}*AG{24+nni+1}/AG60)^2'
            worksheet.write(24+nni, 9+28, fml, self.font_pct)
            fml = f'=AL{24+nni+1}'
            worksheet.write(24+nni, 10+28, fml, self.limit_cut)
            worksheet.write(24+nni, 11+28, param._dof, self.font_inputdof)

        worksheet.conditional_format('AM25:AM56', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(57, 0+28, 'Quantity')
        worksheet.write(57, 2+28, 'Unit')
        worksheet.write(57, 3+28, 'Value')
        worksheet.write(57, 4+28, 'Std unc')
        worksheet.write(57, 5+28, 'Rel unc')
        worksheet.write(57, 9+28, 'contribution to variance')
        worksheet.write(58, 0+28, 'Y', self.font_ital)
        worksheet.write_rich_string(58, 2+28, '[', self.font_ital, 'Y', ']')
        worksheet.write(58, 3+28, 'y', self.font_ital)
        worksheet.write_rich_string(58, 4+28, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(58, 5+28, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(58, 9+28, self.font_ital, 'I', ' / %')
        worksheet.write(58, 11+28, 'DoF')

        worksheet.write(59, 0+28, '=A7')
        worksheet.write(59, 2+28, '=C7')
        if budget.SC._model() == 'k0_direct':
            fml = '=AF55/AF56'
        elif budget.SC._model() == 'relative_direct':
            fml = '=(AF45*(AF25*AF26+AF27*AF28+AF29*AF30+AF31*AF32+AF33*AF34+AF35*AF36+AF37*AF38+AF39*AF40+AF41*AF42+AF43*AF44))/(AF25*(AF45*AF26+AF46*AF28+AF47*AF30+AF48*AF32+AF49*AF34+AF50*AF36+AF51*AF38+AF52*AF40+AF53*AF42+AF54*AF44))'
        else:
            fml = 'ERROR'
        worksheet.write(59, 3+28, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(AK25:AK56),TRANSPOSE(AG25:AG56)*{budget.SC._corr_matrix()}*AG25:AG56),AK25:AK56)){cpth}'
        worksheet.write(59, 4+28, fml, self.font_datum)

        fml = '=IFERROR(ABS(AG60/AF60),"-")'
        worksheet.write(59, 5+28, fml, self.font_pct)

        fml = '=SUM(AL25:AL56)'
        worksheet.write(59, 9+28, fml, self.font_pct)

        fml = '=INT(AG60^4/((AG25*AK25)^4/AN25+(AG26*AK26)^4/AN26+(AG27*AK27)^4/AN27+(AG28*AK28)^4/AN28+(AG29*AK29)^4/AN29+(AG30*AK30)^4/AN30+(AG31*AK31)^4/AN31+(AG32*AK32)^4/AN32+(AG33*AK33)^4/AN33+(AG34*AK34)^4/AN34+(AG35*AK35)^4/AN35+(AG36*AK36)^4/AN36+(AG37*AK37)^4/AN37+(AG38*AK38)^4/AN38+(AG39*AK39)^4/AN39+(AG40*AK40)^4/AN40+(AG41*AK41)^4/AN41+(AG42*AK42)^4/AN42+(AG43*AK43)^4/AN43+(AG44*AK44)^4/AN44+(AG45*AK45)^4/AN45+(AG46*AK46)^4/AN46+(AG47*AK47)^4/AN47+(AG48*AK48)^4/AN48+(AG49*AK49)^4/AN49+(AG50*AK50)^4/AN50+(AG51*AK51)^4/AN51+(AG52*AK52)^4/AN52+(AG53*AK53)^4/AN53+(AG54*AK54)^4/AN54+(AG55*AK55)^4/AN55+(AG56*AK56)^4/AN56))'
        worksheet.write(59, 11+28, fml, self.font_integer)

        #NEUTRON ACTIVATION RATIO
        worksheet.write(21, 0+42, '=A8', self.grey_info)
        worksheet.write(21, 1+42, '', self.grey_fill)
        worksheet.write(21, 2+42, '', self.grey_fill)
        worksheet.write(21, 3+42, '', self.grey_fill)
        worksheet.write(21, 4+42, '', self.grey_fill)
        worksheet.write(21, 5+42, '', self.grey_fill)
        worksheet.write(21, 8+42, '', self.grey_fill)
        worksheet.write(21, 9+42, '', self.grey_fill)
        worksheet.write(21, 10+42, '', self.grey_fill)
        worksheet.write(21, 11+42, '', self.grey_fill)

        worksheet.write(22, 0+42, 'Quantity')
        worksheet.write(22, 2+42, 'Unit')
        worksheet.write(22, 3+42, 'Value')
        worksheet.write(22, 4+42, 'Std unc')
        worksheet.write(22, 5+42, 'Rel unc')
        worksheet.write(22, 8+42, 'Sensitivity coeff.')
        worksheet.write(22, 9+42, 'contribution to variance')

        worksheet.write_rich_string(23, 0+42, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+42, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+42, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+42, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+42, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+42, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+42, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+42, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+42, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+42, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+42, 'DoF')

        if budget.NF._model() == 'not-relative_direct':
            _model = '=(1/(1+AT25*AT26))*(AT29+AT30/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))/(AT27+AT28/AT31*((AT33-0.429)/AT34^AT32+0.429/(0.55^AT32*(1+2*AT32))))'
        elif budget.NF._model() == 'relative_direct':
            _model = '=(1/(1+AT25*AT26))*(AT29+AT30/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))/(AT27+AT28/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))'
        else:
            _model = 'ERROR'

        #parameters
        worksheet.write(24, 0+42, 'b', self.font_sym)
        worksheet.write_rich_string(24, 2+42, 'mm', self.font_sups, '-1')
        fmlp = _model.replace('AT25','(AT25+AU25)')
        fmlm = fmlp.replace('(AT25+AU25)','(AT25-AU25)')
        worksheet.write(24, 6+42, fmlp)
        worksheet.write(24, 7+42, fmlm)

        worksheet.write_rich_string(25, 0+42, self.font_sym, 'D', self.font_subs, 'l')
        worksheet.write(25, 2+42, 'mm')
        fmlp = _model.replace('AT26','(AT26+AU26)')
        fmlm = fmlp.replace('(AT26+AU26)','(AT26-AU26)')
        worksheet.write(25, 6+42, fmlp)
        worksheet.write(25, 7+42, fmlm)

        worksheet.write_rich_string(26, 0+42, 'G', self.font_subs, 'th smp')
        worksheet.write(26, 2+42, '1')
        fmlp = _model.replace('AT27','(AT27+AU27)')
        fmlm = fmlp.replace('(AT27+AU27)','(AT27-AU27)')
        worksheet.write(26, 6+42, fmlp)
        worksheet.write(26, 7+42, fmlm)

        worksheet.write_rich_string(27, 0+42, 'G', self.font_subs, 'e smp')
        worksheet.write(27, 2+42, '1')
        fmlp = _model.replace('AT28','(AT28+AU28)')
        fmlm = fmlp.replace('(AT28+AU28)','(AT28-AU28)')
        worksheet.write(27, 6+42, fmlp)
        worksheet.write(27, 7+42, fmlm)

        worksheet.write_rich_string(28, 0+42, 'G', self.font_subs, 'th std')
        worksheet.write(28, 2+42, '1')
        fmlp = _model.replace('AT29','(AT29+AU29)')
        fmlm = fmlp.replace('(AT29+AU29)','(AT29-AU29)')
        worksheet.write(28, 6+42, fmlp)
        worksheet.write(28, 7+42, fmlm)

        worksheet.write_rich_string(29, 0+42, 'G', self.font_subs, 'e std')
        worksheet.write(29, 2+42, '1')
        fmlp = _model.replace('AT30','(AT30+AU30)')
        fmlm = fmlp.replace('(AT30+AU30)','(AT30-AU30)')
        worksheet.write(29, 6+42, fmlp)
        worksheet.write(29, 7+42, fmlm)

        worksheet.write(30, 0+42, 'f', self.font_ital)
        worksheet.write(30, 2+42, '1')
        fmlp = _model.replace('AT31','(AT31+AU31)')
        fmlm = fmlp.replace('(AT31+AU31)','(AT31-AU31)')
        worksheet.write(30, 6+42, fmlp)
        worksheet.write(30, 7+42, fmlm)

        worksheet.write(31, 0+42, 'a', self.font_sym)
        worksheet.write(31, 2+42, '1')
        fmlp = _model.replace('AT32','(AT32+AU32)')
        fmlm = fmlp.replace('(AT32+AU32)','(AT32-AU32)')
        worksheet.write(31, 6+42, fmlp)
        worksheet.write(31, 7+42, fmlm)

        worksheet.write_rich_string(32, 0+42, 'Q', self.font_subs, '0 a')
        worksheet.write(32, 2+42, '1')
        fmlp = _model.replace('AT33','(AT33+AU33)')
        fmlm = fmlp.replace('(AT33+AU33)','(AT33-AU33)')
        worksheet.write(32, 6+42, fmlp)
        worksheet.write(32, 7+42, fmlm)

        worksheet.write_rich_string(33, 0+42, 'E', self.font_subs, 'r a')
        worksheet.write(33, 2+42, 'eV')
        fmlp = _model.replace('AT34','(AT34+AU34)')
        fmlm = fmlp.replace('(AT34+AU34)','(AT34-AU34)')
        worksheet.write(33, 6+42, fmlp)
        worksheet.write(33, 7+42, fmlm)

        worksheet.write_rich_string(34, 0+42, 'Q', self.font_subs, '0 m')
        worksheet.write(34, 2+42, '1')
        fmlp = _model.replace('AT35','(AT35+AU35)')
        fmlm = fmlp.replace('(AT35+AU35)','(AT35-AU35)')
        worksheet.write(34, 6+42, fmlp)
        worksheet.write(34, 7+42, fmlm)

        worksheet.write_rich_string(35, 0+42, 'E', self.font_subs, 'r m')
        worksheet.write(35, 2+42, 'eV')
        fmlp = _model.replace('AT36','(AT36+AU36)')
        fmlm = fmlp.replace('(AT36+AU36)','(AT36-AU36)')
        worksheet.write(35, 6+42, fmlp)
        worksheet.write(35, 7+42, fmlm)

        for nni, param in enumerate(budget.NF.parameters):
            worksheet.write(24+nni, 3+42, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+42, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(AU{24+nni+1}/AT{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+42, fml, self.font_pct)

            fml = f'=(AW{24+nni+1}-AX{24+nni+1})/(2*AU{24+nni+1}+1E-24)'
            worksheet.write(24+nni, 8+42, fml, self.font_datum)

            fml = f'=(AY{24+nni+1}*AU{24+nni+1}/AU40)^2'
            worksheet.write(24+nni, 9+42, fml, self.font_pct)
            fml = f'=AZ{24+nni+1}'
            worksheet.write(24+nni, 10+42, fml, self.limit_cut)
            worksheet.write(24+nni, 11+42, param._dof, self.font_inputdof)

        worksheet.conditional_format('BA25:BA36', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(37, 0+42, 'Quantity')
        worksheet.write(37, 2+42, 'Unit')
        worksheet.write(37, 3+42, 'Value')
        worksheet.write(37, 4+42, 'Std unc')
        worksheet.write(37, 5+42, 'Rel unc')
        worksheet.write(37, 9+42, 'contribution to variance')
        worksheet.write(38, 0+42, 'Y', self.font_ital)
        worksheet.write_rich_string(38, 2+42, '[', self.font_ital, 'Y', ']')
        worksheet.write(38, 3+42, 'y', self.font_ital)
        worksheet.write_rich_string(38, 4+42, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(38, 5+42, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(38, 9+42, self.font_ital, 'I', ' / %')
        worksheet.write(38, 11+42, 'DoF')

        worksheet.write(39, 0+42, '=A8')
        worksheet.write(39, 2+42, '=C8')
        if budget.NF._model() == 'not-relative_direct':
            fml = '=(1/(1+AT25*AT26))*(AT29+AT30/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))/(AT27+AT28/AT31*((AT33-0.429)/AT34^AT32+0.429/(0.55^AT32*(1+2*AT32))))'
        elif budget.NF._model() == 'relative_direct':
            fml = '=(1/(1+AT25*AT26))*(AT29+AT30/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))/(AT27+AT28/AT31*((AT35-0.429)/AT36^AT32+0.429/(0.55^AT32*(1+2*AT32))))'
        else:
            fml = 'ERROR'
        worksheet.write(39, 3+42, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(AY25:AY36),TRANSPOSE(AU25:AU36)*{budget.NF._corr_matrix()}*AU25:AU36),AY25:AY36)){cpth}'
        worksheet.write(39, 4+42, fml, self.font_datum)

        fml = '=IFERROR(ABS(AU40/AT40),"-")'
        worksheet.write(39, 5+42, fml, self.font_pct)

        fml = '=SUM(AZ25:AZ36)'
        worksheet.write(39, 9+42, fml, self.font_pct)

        fml = '=INT(AU40^4/((AU25*AY25)^4/BB25+(AU26*AY26)^4/BB26+(AU27*AY27)^4/BB27+(AU28*AY28)^4/BB28+(AU29*AY29)^4/BB29+(AU30*AY30)^4/BB30+(AU31*AY31)^4/BB31+(AU32*AY32)^4/BB32+(AU33*AY33)^4/BB33+(AU34*AY34)^4/BB34+(AU35*AY35)^4/BB35+(AU36*AY36)^4/BB36))'
        worksheet.write(39, 11+42, fml, self.font_integer)

        #EFFICIENCY RATIO
        worksheet.write(21, 0+56, '=A9', self.grey_info)
        worksheet.write(21, 1+56, '', self.grey_fill)
        worksheet.write(21, 2+56, '', self.grey_fill)
        worksheet.write(21, 3+56, '', self.grey_fill)
        worksheet.write(21, 4+56, '', self.grey_fill)
        worksheet.write(21, 5+56, '', self.grey_fill)
        worksheet.write(21, 8+56, '', self.grey_fill)
        worksheet.write(21, 9+56, '', self.grey_fill)
        worksheet.write(21, 10+56, '', self.grey_fill)
        worksheet.write(21, 11+56, '', self.grey_fill)

        worksheet.write(22, 0+56, 'Quantity')
        worksheet.write(22, 2+56, 'Unit')
        worksheet.write(22, 3+56, 'Value')
        worksheet.write(22, 4+56, 'Std unc')
        worksheet.write(22, 5+56, 'Rel unc')
        worksheet.write(22, 8+56, 'Sensitivity coeff.')
        worksheet.write(22, 9+56, 'contribution to variance')

        worksheet.write_rich_string(23, 0+56, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+56, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+56, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+56, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+56, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+56, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+56, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+56, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+56, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+56, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+56, 'DoF')

        if budget.EF._model() == 'all_relative_direct':
            _model = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH27-BH29))) * ((1 + (BH31+BH34)/(BH27-BH29)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        elif budget.EF._model() == 'same_distance':
            _model = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH27-BH32))) * ((1 + (BH31+BH34)/(BH27-BH32)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        elif budget.EF._model() == 'different_distance':
            _model = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH30-BH32))) * ((1 + (BH31+BH34)/(BH30-BH32)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        else:
            _model = 'ERROR'

        #parameters
        worksheet.write_rich_string(24, 0+56, 'k', self.font_sym, 'eD', self.font_subs, 'E')
        worksheet.write(24, 2+56, '1')
        fmlp = _model.replace('BH25','(BH25+BI25)')
        fmlm = fmlp.replace('(BH25+BI25)','(BH25-BI25)')
        worksheet.write(24, 6+56, fmlp)
        worksheet.write(24, 7+56, fmlm)

        worksheet.write_rich_string(25, 0+56, 'k', self.font_sym, 'eD', self.font_subs, 'd')
        worksheet.write(25, 2+56, '1')
        fmlp = _model.replace('BH26','(BH26+BI26)')
        fmlm = fmlp.replace('(BH26+BI26)','(BH26-BI26)')
        worksheet.write(25, 6+56, fmlp)
        worksheet.write(25, 7+56, fmlm)

        worksheet.write_rich_string(26, 0+56, self.font_ital, 'd', self.font_subs, 'std')
        worksheet.write(26, 2+56, 'mm')
        fmlp = _model.replace('BH27','(BH27+BI27)')
        fmlm = fmlp.replace('(BH27+BI27)','(BH27-BI27)')
        worksheet.write(26, 6+56, fmlp)
        worksheet.write(26, 7+56, fmlm)

        worksheet.write_rich_string(27, 0+56, self.font_sym, 'd', self.font_ital, 'd', self.font_subs, 'std')
        worksheet.write(27, 2+56, 'mm')
        fmlp = _model.replace('BH28','(BH28+BI28)')
        fmlm = fmlp.replace('(BH28+BI28)','(BH28-BI28)')
        worksheet.write(27, 6+56, fmlp)
        worksheet.write(27, 7+56, fmlm)

        worksheet.write_rich_string(28, 0+56, self.font_ital, "d'", self.font_subs, '0 std')
        worksheet.write(28, 2+56, 'mm')
        fmlp = _model.replace('BH29','(BH29+BI29)')
        fmlm = fmlp.replace('(BH29+BI29)','(BH29-BI29)')
        worksheet.write(28, 6+56, fmlp)
        worksheet.write(28, 7+56, fmlm)

        worksheet.write_rich_string(29, 0+56, self.font_ital, 'd', self.font_subs, 'smp')
        worksheet.write(29, 2+56, 'mm')
        fmlp = _model.replace('BH30','(BH30+BI30)')
        fmlm = fmlp.replace('(BH30+BI30)','(BH30-BI30)')
        worksheet.write(29, 6+56, fmlp)
        worksheet.write(29, 7+56, fmlm)

        worksheet.write_rich_string(30, 0+56, self.font_sym, 'd', self.font_ital, 'd', self.font_subs, 'smp')
        worksheet.write(30, 2+56, 'mm')
        fmlp = _model.replace('BH31','(BH31+BI31)')
        fmlm = fmlp.replace('(BH31+BI31)','(BH31-BI31)')
        worksheet.write(30, 6+56, fmlp)
        worksheet.write(30, 7+56, fmlm)

        worksheet.write_rich_string(31, 0+56, self.font_ital, "d'", self.font_subs, '0 smp')
        worksheet.write(31, 2+56, 'mm')
        fmlp = _model.replace('BH32','(BH32+BI32)')
        fmlm = fmlp.replace('(BH32+BI32)','(BH32-BI32)')
        worksheet.write(31, 6+56, fmlp)
        worksheet.write(31, 7+56, fmlm)

        worksheet.write_rich_string(32, 0+56, self.font_ital, 'h', self.font_subs, 'std')
        worksheet.write(32, 2+56, 'mm')
        fmlp = _model.replace('BH33','(BH33+BI33)')
        fmlm = fmlp.replace('(BH33+BI33)','(BH33-BI33)')
        worksheet.write(32, 6+56, fmlp)
        worksheet.write(32, 7+56, fmlm)

        worksheet.write_rich_string(33, 0+56, self.font_ital, 'h', self.font_subs, 'smp')
        worksheet.write(33, 2+56, 'mm')
        fmlp = _model.replace('BH34','(BH34+BI34)')
        fmlm = fmlp.replace('(BH34+BI34)','(BH34-BI34)')
        worksheet.write(33, 6+56, fmlp)
        worksheet.write(33, 7+56, fmlm)

        worksheet.write_rich_string(34, 0+56, self.font_sym, 'n', self.font_subs, 'std')
        worksheet.write_rich_string(34, 2+56, 'mm', self.font_sups, '2', 'g', self.font_sups, '-1')
        fmlp = _model.replace('BH35','(BH35+BI35)')
        fmlm = fmlp.replace('(BH35+BI35)','(BH35-BI35)')
        worksheet.write(34, 6+56, fmlp)
        worksheet.write(34, 7+56, fmlm)

        worksheet.write_rich_string(35, 0+56, self.font_sym, 'r', self.font_subs, 'std')
        worksheet.write_rich_string(35, 2+56, 'g cm', self.font_sups, '-3')
        fmlp = _model.replace('BH36','(BH36+BI36)')
        fmlm = fmlp.replace('(BH36+BI36)','(BH36-BI36)')
        worksheet.write(35, 6+56, fmlp)
        worksheet.write(35, 7+56, fmlm)

        worksheet.write_rich_string(36, 0+56, self.font_sym, 'n', self.font_subs, 'smp')
        worksheet.write_rich_string(36, 2+56, 'mm', self.font_sups, '2', 'g', self.font_sups, '-1')
        fmlp = _model.replace('BH37','(BH37+BI37)')
        fmlm = fmlp.replace('(BH37+BI37)','(BH37-BI37)')
        worksheet.write(36, 6+56, fmlp)
        worksheet.write(36, 7+56, fmlm)

        worksheet.write_rich_string(37, 0+56, self.font_sym, 'r', self.font_subs, 'smp')
        worksheet.write_rich_string(37, 2+56, 'g cm', self.font_sups, '-3')
        fmlp = _model.replace('BH38','(BH38+BI38)')
        fmlm = fmlp.replace('(BH38+BI38)','(BH38-BI38)')
        worksheet.write(37, 6+56, fmlp)
        worksheet.write(37, 7+56, fmlm)

        worksheet.write_rich_string(38, 0+56, 'r', self.font_ital, 'COI')
        worksheet.write(38, 2+56, '1')
        fmlp = _model.replace('BH39','(BH39+BI39)')
        fmlm = fmlp.replace('(BH39+BI39)','(BH39-BI39)')
        worksheet.write(38, 6+56, fmlp)
        worksheet.write(38, 7+56, fmlm)

        for nni, param in enumerate(budget.EF.parameters):
            worksheet.write(24+nni, 3+56, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+56, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(BI{24+nni+1}/BH{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+56, fml, self.font_pct)

            fml = f'=(BK{24+nni+1}-BL{24+nni+1})/(2*BI{24+nni+1}+1E-24)'
            worksheet.write(24+nni, 8+56, fml, self.font_datum)

            fml = f'=(BM{24+nni+1}*BI{24+nni+1}/BI43)^2'
            worksheet.write(24+nni, 9+56, fml, self.font_pct)
            fml = f'=BN{24+nni+1}'
            worksheet.write(24+nni, 10+56, fml, self.limit_cut)
            worksheet.write(24+nni, 11+56, param._dof, self.font_inputdof)

        worksheet.conditional_format('BO25:BO39', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(40, 0+56, 'Quantity')
        worksheet.write(40, 2+56, 'Unit')
        worksheet.write(40, 3+56, 'Value')
        worksheet.write(40, 4+56, 'Std unc')
        worksheet.write(40, 5+56, 'Rel unc')
        worksheet.write(40, 9+56, 'contribution to variance')
        worksheet.write(41, 0+56, 'Y', self.font_ital)
        worksheet.write_rich_string(41, 2+56, '[', self.font_ital, 'Y', ']')
        worksheet.write(41, 3+56, 'y', self.font_ital)
        worksheet.write_rich_string(41, 4+56, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(41, 5+56, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(41, 9+56, self.font_ital, 'I', ' / %')
        worksheet.write(41, 11+56, 'DoF')

        worksheet.write(42, 0+56, '=A9')
        worksheet.write(42, 2+56, '=C9')

        if budget.EF._model() == 'all_relative_direct':
            fml = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH27-BH29))) * ((1 + (BH31+BH34)/(BH27-BH29)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        elif budget.EF._model() == 'same_distance':
            fml = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH27-BH32))) * ((1 + (BH31+BH34)/(BH27-BH32)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        elif budget.EF._model() == 'different_distance':
            fml = '=BH25*BH26 * ((1+BH28/(BH27-BH29)) / (1+BH31/(BH30-BH32))) * ((1 + (BH31+BH34)/(BH30-BH32)) / (1 + (BH28+BH33)/(BH27-BH29))) * ((1-EXP(-BH35*BH33*BH36/1000))/(BH35*BH33*BH36)) / ((1-EXP(-BH37*BH34*BH38/1000))/(BH37*BH34*BH38)) * BH39'
        else:
            fml = 'ERROR'
        worksheet.write(42, 3+56, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(BM25:BM39),TRANSPOSE(BI25:BI39)*{budget.EF._corr_matrix()}*BI25:BI39),BM25:BM39)){cpth}'
        worksheet.write(42, 4+56, fml, self.font_datum)

        fml = '=IFERROR(ABS(BI43/BH43),"-")'
        worksheet.write(42, 5+56, fml, self.font_pct)

        fml = '=SUM(BN25:BN39)'
        worksheet.write(42, 9+56, fml, self.font_pct)

        fml = '=INT(BI43^4/((BI25*BM25)^4/BP25+(BI26*BM26)^4/BP26+(BI27*BM27)^4/BP27+(BI28*BM28)^4/BP28+(BI29*BM29)^4/BP29+(BI30*BM30)^4/BP30+(BI31*BM31)^4/BP31+(BI32*BM32)^4/BP32+(BI33*BM33)^4/BP33+(BI34*BM34)^4/BP34+(BI35*BM35)^4/BP35+(BI36*BM36)^4/BP36+(BI37*BM37)^4/BP37+(BI38*BM38)^4/BP38+(BI39*BM39)^4/BP39))'
        worksheet.write(42, 11+56, fml, self.font_integer)

        #MASS RATIO
        worksheet.write(21, 0+70, '=A10', self.grey_info)
        worksheet.write(21, 1+70, '', self.grey_fill)
        worksheet.write(21, 2+70, '', self.grey_fill)
        worksheet.write(21, 3+70, '', self.grey_fill)
        worksheet.write(21, 4+70, '', self.grey_fill)
        worksheet.write(21, 5+70, '', self.grey_fill)
        worksheet.write(21, 8+70, '', self.grey_fill)
        worksheet.write(21, 9+70, '', self.grey_fill)
        worksheet.write(21, 10+70, '', self.grey_fill)
        worksheet.write(21, 11+70, '', self.grey_fill)

        worksheet.write(22, 0+70, 'Quantity')
        worksheet.write(22, 2+70, 'Unit')
        worksheet.write(22, 3+70, 'Value')
        worksheet.write(22, 4+70, 'Std unc')
        worksheet.write(22, 5+70, 'Rel unc')
        worksheet.write(22, 8+70, 'Sensitivity coeff.')
        worksheet.write(22, 9+70, 'contribution to variance')

        worksheet.write_rich_string(23, 0+70, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+70, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+70, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+70, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+70, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+70, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+70, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+70, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+70, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+70, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+70, 'DoF')

        #parameters
        worksheet.write_rich_string(24, 0+70, self.font_ital, 'm', self.font_subs, 'smp')
        worksheet.write(24, 2+70, 'g')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / ((BV25+BW25)*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV25+BW25)','(BV25-BW25)')
        worksheet.write(24, 6+70, fmlp)
        worksheet.write(24, 7+70, fmlm)

        worksheet.write_rich_string(25, 0+70, self.font_sym, 'h', self.font_subs, 'smp')
        worksheet.write(25, 2+70, '1')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-(BV26+BW26))*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV26+BW26)','(BV26-BW26)')
        worksheet.write(25, 6+70, fmlp)
        worksheet.write(25, 7+70, fmlm)

        worksheet.write_rich_string(26, 0+70, self.font_ital, 'm', self.font_subs, 'std')
        worksheet.write(26, 2+70, 'g')
        fmlp = '=((BV27+BW27)*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV27+BW27)','(BV27-BW27)')
        worksheet.write(26, 6+70, fmlp)
        worksheet.write(26, 7+70, fmlm)

        worksheet.write_rich_string(27, 0+70, self.font_sym, 'h', self.font_subs, 'std')
        worksheet.write(27, 2+70, '1')
        fmlp = '=(BV27*(1-(BV28+BW28))*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV28+BW28)','(BV28-BW28)')
        worksheet.write(27, 6+70, fmlp)
        worksheet.write(27, 7+70, fmlm)

        worksheet.write_rich_string(28, 0+70, self.font_ital, 'w', self.font_subs, 'std')
        worksheet.write_rich_string(28, 2+70, 'g g', self.font_sups, '-1')
        fmlp = '=(BV27*(1-BV28)*(BV29+BW29)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV29+BW29)','(BV29-BW29)')
        worksheet.write(28, 6+70, fmlp)
        worksheet.write(28, 7+70, fmlm)

        worksheet.write(29, 0+70, 'p', self.font_ital)
        worksheet.write(29, 2+70, 'mbar')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*(BV30+BW30)-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*(BV30+BW30)-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV30+BW30)','(BV30-BW30)')
        worksheet.write(29, 6+70, fmlp)
        worksheet.write(29, 7+70, fmlm)

        worksheet.write(30, 0+70, 'RH', self.font_ital)
        worksheet.write(30, 2+70, '%')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*(BV31+BW31)*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*(BV31+BW31)*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV31+BW31)','(BV31-BW31)')
        worksheet.write(30, 6+70, fmlp)
        worksheet.write(30, 7+70, fmlm)

        worksheet.write(31, 0+70, 'T', self.font_ital)
        worksheet.write(31, 2+70, '°C')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*(BV32+BW32)))/(273.15*(BV32+BW32))*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*(BV32+BW32)))/(273.15*(BV32+BW32))*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV32+BW32)','(BV32-BW32)')
        worksheet.write(31, 6+70, fmlp)
        worksheet.write(31, 7+70, fmlm)

        worksheet.write_rich_string(32, 0+70, self.font_sym, 'r', self.font_subs, 'C')
        worksheet.write_rich_string(32, 2+70, 'g cm', self.font_sups, '-3')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/(BV33+BW33)))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/(BV33+BW33))))'
        fmlm = fmlp.replace('(BV33+BW33)','(BV33-BW33)')
        worksheet.write(32, 6+70, fmlp)
        worksheet.write(32, 7+70, fmlm)

        worksheet.write_rich_string(33, 0+70, self.font_sym, 'r', self.font_subs, 'm')
        worksheet.write_rich_string(33, 2+70, 'g cm', self.font_sups, '-3')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/(BV34+BW34)-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        fmlm = fmlp.replace('(BV34+BW34)','(BV34-BW34)')
        worksheet.write(33, 6+70, fmlp)
        worksheet.write(33, 7+70, fmlm)

        worksheet.write_rich_string(34, 0+70, self.font_sym, 'r', self.font_subs, 'a')
        worksheet.write_rich_string(34, 2+70, 'g cm', self.font_sups, '-3')
        fmlp = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/(BV35+BW35)-1/BV33)))'
        fmlm = fmlp.replace('(BV35+BW35)','(BV35-BW35)')
        worksheet.write(34, 6+70, fmlp)
        worksheet.write(34, 7+70, fmlm)

        for nni, param in enumerate(budget.MSS.parameters):
            worksheet.write(24+nni, 3+70, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+70, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(BW{24+nni+1}/BV{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+70, fml, self.font_pct)

            fml = f'=(BY{24+nni+1}-BZ{24+nni+1})/(2*BW{24+nni+1}+1E-24)'
            worksheet.write(24+nni, 8+70, fml, self.font_datum)

            fml = f'=(CA{24+nni+1}*BW{24+nni+1}/BW39)^2'
            worksheet.write(24+nni, 9+70, fml, self.font_pct)
            fml = f'=CB{24+nni+1}'
            worksheet.write(24+nni, 10+70, fml, self.limit_cut)
            worksheet.write(24+nni, 11+70, param._dof, self.font_inputdof)

        worksheet.conditional_format('CC25:CC35', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(36, 0+70, 'Quantity')
        worksheet.write(36, 2+70, 'Unit')
        worksheet.write(36, 3+70, 'Value')
        worksheet.write(36, 4+70, 'Std unc')
        worksheet.write(36, 5+70, 'Rel unc')
        worksheet.write(36, 9+70, 'contribution to variance')
        worksheet.write(37, 0+70, 'Y', self.font_ital)
        worksheet.write_rich_string(37, 2+70, '[', self.font_ital, 'Y', ']')
        worksheet.write(37, 3+70, 'y', self.font_ital)
        worksheet.write_rich_string(37, 4+70, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(37, 5+70, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(37, 9+70, self.font_ital, 'I', ' / %')
        worksheet.write(37, 11+70, 'DoF')

        worksheet.write(38, 0+70, '=A10')
        worksheet.write_rich_string(38, 2+70, 'g g', self.font_sups, '-1')

        fml = '=(BV27*(1-BV28)*BV29*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV34-1/BV33))) / (BV25*(1-BV26)*(1+0.001*(0.34848*BV30-0.009*BV31*EXP(0.061*BV32))/(273.15*BV32)*(1/BV35-1/BV33)))'
        worksheet.write(38, 3+70, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(CA25:CA35),TRANSPOSE(BW25:BW35)*{budget.MSS._corr_matrix()}*BW25:BW35),CA25:CA35)){cpth}'
        worksheet.write(38, 4+70, fml, self.font_datum)

        fml = '=IFERROR(ABS(BW39/BV39),"-")'
        worksheet.write(38, 5+70, fml, self.font_pct)

        fml = '=SUM(CB25:CB35)'
        worksheet.write(38, 9+70, fml, self.font_pct)

        fml = '=INT(BW39^4/((BW25*CA25)^4/CD25+(BW26*CA26)^4/CD26+(BW27*CA27)^4/CD27+(BW28*CA28)^4/CD28+(BW29*CA29)^4/CD29+(BW30*CA30)^4/CD30+(BW31*CA31)^4/CD31+(BW32*CA32)^4/CD32+(BW33*CA33)^4/CD33+(BW34*CA34)^4/CD34+(BW35*CA35)^4/CD35))'
        worksheet.write(38, 11+70, fml, self.font_integer)

        #BLANK CORRECTION
        worksheet.write(21, 0+84, '=A11', self.grey_info)
        worksheet.write(21, 1+84, '', self.grey_fill)
        worksheet.write(21, 2+84, '', self.grey_fill)
        worksheet.write(21, 3+84, '', self.grey_fill)
        worksheet.write(21, 4+84, '', self.grey_fill)
        worksheet.write(21, 5+84, '', self.grey_fill)
        worksheet.write(21, 8+84, '', self.grey_fill)
        worksheet.write(21, 9+84, '', self.grey_fill)
        worksheet.write(21, 10+84, '', self.grey_fill)
        worksheet.write(21, 11+84, '', self.grey_fill)

        worksheet.write(22, 0+84, 'Quantity')
        worksheet.write(22, 2+84, 'Unit')
        worksheet.write(22, 3+84, 'Value')
        worksheet.write(22, 4+84, 'Std unc')
        worksheet.write(22, 5+84, 'Rel unc')
        worksheet.write(22, 8+84, 'Sensitivity coeff.')
        worksheet.write(22, 9+84, 'contribution to variance')

        worksheet.write_rich_string(23, 0+84, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+84, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+84, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+84, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+84, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+84, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+84, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+84, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+84, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+84, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+84, 'DoF')

        #parameters
        worksheet.write_rich_string(24, 0+84, self.font_ital, 'm', self.font_subs, 'smp')
        worksheet.write(24, 2+84, 'g')
        fml = '=-(CJ27*CJ28)/(CJ25^2 * (1-CJ26))'
        worksheet.write(24, 8+84, fml)

        worksheet.write_rich_string(25, 0+84, self.font_sym, 'h', self.font_subs, 'smp')
        worksheet.write(25, 2+84, '1')
        fml = '=(CJ27*CJ28)/(CJ25 * (1-CJ26)^2)'
        worksheet.write(25, 8+84, fml)

        worksheet.write_rich_string(26, 0+84, self.font_ital, 'm', self.font_subs, 'blk')
        worksheet.write(26, 2+84, 'g')
        fml = '=CJ28/(CJ25 * (1-CJ26))'
        worksheet.write(26, 8+84, fml)

        worksheet.write_rich_string(27, 0+84, self.font_ital, 'w', self.font_subs, 'blk')
        worksheet.write_rich_string(27, 2+84, 'g g', self.font_sups, '-1')
        fml = '=CJ27/(CJ25 * (1-CJ26))'
        worksheet.write(27, 8+84, fml)

        for nni, param in enumerate(budget.BNK.parameters):
            worksheet.write(24+nni, 3+84, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+84, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(CK{24+nni+1}/CJ{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+84, fml, self.font_pct)

            fml = f'=(CO{24+nni+1}*CK{24+nni+1}/CK31)^2'
            worksheet.write(24+nni, 9+84, fml, self.font_pct)
            fml = f'=CP{24+nni+1}'
            worksheet.write(24+nni, 10+84, fml, self.limit_cut)
            worksheet.write(24+nni, 11+84, param._dof, self.font_inputdof)
        
        worksheet.conditional_format('CQ25:CQ28', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(29, 0+84, 'Quantity')
        worksheet.write(29, 2+84, 'Unit')
        worksheet.write(29, 3+84, 'Value')
        worksheet.write(29, 4+84, 'Std unc')
        worksheet.write(29, 5+84, 'Rel unc')
        worksheet.write(29, 9+84, 'contribution to variance')
        worksheet.write(30, 0+84, 'Y', self.font_ital)
        worksheet.write_rich_string(30, 2+84, '[', self.font_ital, 'Y', ']')
        worksheet.write(30, 3+84, 'y', self.font_ital)
        worksheet.write_rich_string(30, 4+84, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(30, 5+84, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(30, 9+84, self.font_ital, 'I', ' / %')
        worksheet.write(30, 11+84, 'DoF')

        worksheet.write(31, 0+84, '=A11')
        worksheet.write_rich_string(31, 2+84, 'g g', self.font_sups, '-1')

        fml = '=(CJ27*CJ28)/(CJ25 * (1-CJ26))'
        worksheet.write(31, 3+84, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(CO25:CO28),TRANSPOSE(CK25:CK28)*{budget.BNK._corr_matrix()}*CK25:CK28),CO25:CO28)){cpth}'
        worksheet.write(31, 4+84, fml, self.font_datum)

        fml = '=IFERROR(ABS(CK32/CJ32),"-")'
        worksheet.write(31, 5+84, fml, self.font_pct)

        fml = '=SUM(CP25:CP28)'
        worksheet.write(31, 9+84, fml, self.font_pct)

        fml = '=INT(CK32^4/((CK25*CO25)^4/CR25+(CK26*CO26)^4/CR26+(CK27*CO27)^4/CR27+(CK28*CO28)^4/CR28))'
        worksheet.write(31, 11+84, fml, self.font_integer)

        #U FISSION CORRECTION
        worksheet.write(21, 0+98, '=A12', self.grey_info)
        worksheet.write(21, 1+98, '', self.grey_fill)
        worksheet.write(21, 2+98, '', self.grey_fill)
        worksheet.write(21, 3+98, '', self.grey_fill)
        worksheet.write(21, 4+98, '', self.grey_fill)
        worksheet.write(21, 5+98, '', self.grey_fill)
        worksheet.write(21, 8+98, '', self.grey_fill)
        worksheet.write(21, 9+98, '', self.grey_fill)
        worksheet.write(21, 10+98, '', self.grey_fill)
        worksheet.write(21, 11+98, '', self.grey_fill)

        worksheet.write(22, 0+98, 'Quantity')
        worksheet.write(22, 2+98, 'Unit')
        worksheet.write(22, 3+98, 'Value')
        worksheet.write(22, 4+98, 'Std unc')
        worksheet.write(22, 5+98, 'Rel unc')
        worksheet.write(22, 8+98, 'Sensitivity coeff.')
        worksheet.write(22, 9+98, 'contribution to variance')

        worksheet.write_rich_string(23, 0+98, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(23, 2+98, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(23, 3+98, self.font_ital, 'x', self.font_subs, 'i')
        worksheet.write_rich_string(23, 4+98, self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 5+98, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(23, 6+98, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' + ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 7+98, self.font_ital, 'y', '(', self.font_ital, 'x', self.font_subs,'i', ' - ', self.font_ital, 'u', '(', self.font_ital, 'x', self.font_subs, 'i', '))')
        worksheet.write_rich_string(23, 8+98, self.font_ital, 'c', self.font_subs, 'i')
        worksheet.write_rich_string(23, 9+98, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(23, 10+98, self.font_ital, 'I', ' (bar)')
        worksheet.write(23, 11+98, 'DoF')

        #parameters
        worksheet.write_rich_string(24, 0+98, self.font_ital, 'w', self.font_subs, 'U')
        worksheet.write_rich_string(24, 2+98, 'g g', self.font_sups, '-1')
        fmlp = '=(CX25+CY25) * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX25+CY25)','(CX25-CY25)')
        worksheet.write(24, 6+98, fmlp)
        worksheet.write(24, 7+98, fmlm)

        worksheet.write_rich_string(25, 0+98, self.font_sym, 'q', self.font_subs, 'i smp')
        worksheet.write_rich_string(25, 2+98, 'mol mol', self.font_sups, '-1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*(CX26+CY26)*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX26+CY26)','(CX26-CY26)')
        worksheet.write(25, 6+98, fmlp)
        worksheet.write(25, 7+98, fmlm)

        worksheet.write_rich_string(26, 0+98, self.font_ital, 'M', self.font_subs, 'i')
        worksheet.write_rich_string(26, 2+98, 'g mol', self.font_sups, '-1')
        fmlp = '=CX25 * ((CX27+CY27)*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX27+CY27)','(CX27-CY27)')
        worksheet.write(26, 6+98, fmlp)
        worksheet.write(26, 7+98, fmlm)

        worksheet.write_rich_string(27, 0+98, self.font_ital, 'Q', self.font_subs, '0 a')
        worksheet.write(27, 2+98, '1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+(((CX28+CY28)-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX28+CY28)','(CX28-CY28)')
        worksheet.write(27, 6+98, fmlp)
        worksheet.write(27, 7+98, fmlm)

        worksheet.write_rich_string(28, 0+98, self.font_ital, 'E', self.font_subs, 'r a')
        worksheet.write(28, 2+98, 'eV')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/(CX29+CY29)^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX29+CY29)','(CX29-CY29)')
        worksheet.write(28, 6+98, fmlp)
        worksheet.write(28, 7+98, fmlm)

        worksheet.write_rich_string(29, 0+98, self.font_sym, 's', self.font_subs, 'a')
        worksheet.write_rich_string(29, 2+98, 'cm', self.font_sups, '2')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*(CX30+CY30)*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX30+CY30)','(CX30-CY30)')
        worksheet.write(29, 6+98, fmlp)
        worksheet.write(29, 7+98, fmlm)

        worksheet.write(30, 0+98, 'f', self.font_ital)
        worksheet.write(30, 2+98, '1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*((CX31+CY31)+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*((CX31+CY31)+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX31+CY31)','(CX31-CY31)')
        worksheet.write(30, 6+98, fmlp)
        worksheet.write(30, 7+98, fmlm)

        worksheet.write(31, 0+98, 'a', self.font_sym)
        worksheet.write(31, 2+98, '1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^(CX32+CY32)+0.429/((2*(CX32+CY32)+1)*0.55^(CX32+CY32))))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^(CX32+CY32)+0.429/((2*(CX32+CY32)+1)*0.55^(CX32+CY32)))))'
        fmlm = fmlp.replace('(CX32+CY32)','(CX32-CY32)')
        worksheet.write(31, 6+98, fmlp)
        worksheet.write(31, 7+98, fmlm)

        worksheet.write_rich_string(32, 0+98, self.font_sym, 'q', self.font_subs, 'U')
        worksheet.write_rich_string(32, 2+98, 'mol mol', self.font_sups, '-1')
        fmlp = '=CX25 * (CX27*(CX33+CY33)*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX33+CY33)','(CX33-CY33)')
        worksheet.write(32, 6+98, fmlp)
        worksheet.write(32, 7+98, fmlm)

        worksheet.write_rich_string(33, 0+98, self.font_ital, 'M', self.font_subs, 'U')
        worksheet.write_rich_string(33, 2+98, 'g mol', self.font_sups, '-1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / ((CX34+CY34)*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX34+CY34)','(CX34-CY34)')
        worksheet.write(33, 6+98, fmlp)
        worksheet.write(33, 7+98, fmlm)

        worksheet.write_rich_string(34, 0+98, self.font_ital, 'Q', self.font_subs, '0 U')
        worksheet.write(34, 2+98, '1')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+(((CX35+CY35)-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX35+CY35)','(CX35-CY35)')
        worksheet.write(34, 6+98, fmlp)
        worksheet.write(34, 7+98, fmlm)

        worksheet.write_rich_string(35, 0+98, self.font_ital, 'E', self.font_subs, 'r U')
        worksheet.write(35, 2+98, 'eV')
        fmlp = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/(CX36+CY36)^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX36+CY36)','(CX36-CY36)')
        worksheet.write(35, 6+98, fmlp)
        worksheet.write(35, 7+98, fmlm)

        worksheet.write_rich_string(36, 0+98, self.font_sym, 's', self.font_subs, 'U')
        worksheet.write_rich_string(36, 2+98, 'cm', self.font_sups, '2')
        fmlp = '=CX25 * (CX27*CX33*(CX37+CY37)*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX37+CY37)','(CX37-CY37)')
        worksheet.write(36, 6+98, fmlp)
        worksheet.write(36, 7+98, fmlm)

        worksheet.write_rich_string(37, 0+98, self.font_ital, 'y', self.font_subs, 'FISS')
        worksheet.write(37, 2+98, '1')
        fmlp = '=CX25 * (CX27*CX33*CX37*(CX38+CY38)*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        fmlm = fmlp.replace('(CX38+CY38)','(CX38-CY38)')
        worksheet.write(37, 6+98, fmlp)
        worksheet.write(37, 7+98, fmlm)

        for nni, param in enumerate(budget.FSS.parameters):
            worksheet.write(24+nni, 3+98, param.value, self.font_inputdatum)
            worksheet.write(24+nni, 4+98, param.uncertainty, self.font_inputdatum)
            fml = f'=IFERROR(ABS(CY{24+nni+1}/CX{24+nni+1}),"-")'
            worksheet.write(24+nni, 5+98, fml, self.font_pct)

            fml = f'=(DA{24+nni+1}-DB{24+nni+1})/(2*CY{24+nni+1}+1E-24)'
            worksheet.write(24+nni, 8+98, fml, self.font_datum)

            fml = f'=(CY{24+nni+1}*DC{24+nni+1}/CY42)^2'
            worksheet.write(24+nni, 9+98, fml, self.font_pct)
            fml = f'=DD{24+nni+1}'
            worksheet.write(24+nni, 10+98, fml, self.limit_cut)
            worksheet.write(24+nni, 11+98, param._dof, self.font_inputdof)
        
        worksheet.conditional_format('DE25:DE38', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        worksheet.write(39, 0+98, 'Quantity')
        worksheet.write(39, 2+98, 'Unit')
        worksheet.write(39, 3+98, 'Value')
        worksheet.write(39, 4+98, 'Std unc')
        worksheet.write(39, 5+98, 'Rel unc')
        worksheet.write(39, 9+98, 'contribution to variance')
        worksheet.write(40, 0+98, 'Y', self.font_ital)
        worksheet.write_rich_string(40, 2+98, '[', self.font_ital, 'Y', ']')
        worksheet.write(40, 3+98, 'y', self.font_ital)
        worksheet.write_rich_string(40, 4+98, self.font_ital, 'u', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(40, 5+98, self.font_ital, 'u', self.font_subs,'r', '(', self.font_ital, 'y', ')')
        worksheet.write_rich_string(40, 9+98, self.font_ital, 'I', ' / %')
        worksheet.write(40, 11+98, 'DoF')

        worksheet.write(41, 0+98, '=A12')
        worksheet.write_rich_string(41, 2+98, 'g g', self.font_sups, '-1')

        fml = '=CX25 * (CX27*CX33*CX37*CX38*(CX31+((CX35-0.429)/CX36^CX32+0.429/((2*CX32+1)*0.55^CX32)))) / (CX34*CX26*CX30*(CX31+((CX28-0.429)/CX29^CX32+0.429/((2*CX32+1)*0.55^CX32))))'
        worksheet.write(41, 3+98, fml, self.font_datum)

        opth, cpth = '{', '}'
        fml = f'{opth}=sqrt(MMULT(MMULT(TRANSPOSE(DC25:DC38),TRANSPOSE(CY25:CY38)*{budget.FSS._corr_matrix()}*CY25:CY38),DC25:DC38)){cpth}'
        worksheet.write(41, 4+98, fml, self.font_datum)

        fml = '=IFERROR(ABS(CY42/CX42),"-")'
        worksheet.write(41, 5+98, fml, self.font_pct)

        fml = '=SUM(DD25:DD38)'
        worksheet.write(41, 9+98, fml, self.font_pct)

        fml = '=INT(CY42^4/((CY25*DC25)^4/DF25+(CY26*DC26)^4/DF26+(CY27*DC27)^4/DF27+(CY28*DC28)^4/DF28+(CY29*DC29)^4/DF29+(CY30*DC30)^4/DF30+(CY31*DC31)^4/DF31+(CY32*DC32)^4/DF32+(CY33*DC33)^4/DF33+(CY34*DC34)^4/DF34+(CY35*DC35)^4/DF35+(CY36*DC36)^4/DF36+(CY37*DC37)^4/DF37+(CY38*DC38)^4/DF38))'
        worksheet.write(41, 11+98, fml, self.font_integer)

        worksheet.set_column('G:H', None, None, {'hidden': True})
        worksheet.set_column('U:V', None, None, {'hidden': True})
        worksheet.set_column('AI:AJ', None, None, {'hidden': True})
        worksheet.set_column('AW:AX', None, None, {'hidden': True})
        worksheet.set_column('BK:BL', None, None, {'hidden': True})
        worksheet.set_column('BY:BZ', None, None, {'hidden': True})
        worksheet.set_column('CM:CN', None, None, {'hidden': True})
        worksheet.set_column('DA:DB', None, None, {'hidden': True})

        if self.visible_models:
            worksheet.insert_image('O14', 'data/eqs/eq_main.png')
            worksheet.insert_image('A36', 'data/eqs/eq_net_area_ratio.png')
            if budget.CS._model() == 'k0_direct':
                worksheet.insert_image('O40', 'data/eqs/eq_decay_correction_k0.png')
            else:
                worksheet.insert_image('O40', 'data/eqs/eq_decay_correction_rel.png')
            if budget.SC._model() == 'k0_direct':
                worksheet.insert_image('AC62', 'data/eqs/eq_k0_ratio_k0.png')
            else:
                worksheet.insert_image('AC62', 'data/eqs/eq_k0_ratio_rel.png')
            worksheet.insert_image('AQ42', 'data/eqs/eq_neutron_activation_ratio.png')
            worksheet.insert_image('BE45', 'data/eqs/eq_efficiency_ratio.png')
            worksheet.insert_image('BS41', 'data/eqs/eq_mass_ratio.png')
            worksheet.insert_image('CG34', 'data/eqs/eq_blank_correction.png')
            worksheet.insert_image('CU44', 'data/eqs/eq_U_fission_correction.png')

        if self.set_autolinks:
            #NET AREA RATIO
            worksheet.write(4, 3, f'=IFERROR(D34,{budget.NAP.x})', self.font_datum)
            worksheet.write(4, 4, f'=IFERROR(E34,{budget.NAP.ux})', self.font_datum)
            worksheet.write(4, 11, f'=IFERROR(L34,{budget.NAP._dof})', self.font_integer)
            #DECAY RATIO
            worksheet.write(5, 3, f'=IFERROR(R38,{budget.CS.x})', self.font_datum)
            worksheet.write(5, 4, f'=IFERROR(S38,{budget.CS.ux})', self.font_datum)
            worksheet.write(5, 11, f'=IFERROR(Z38,{budget.CS._dof})', self.font_integer)
            #k0 RATIO
            worksheet.write(6, 3, f'=IFERROR(AF60,{budget.SC.x})', self.font_datum)
            worksheet.write(6, 4, f'=IFERROR(AG60,{budget.SC.ux})', self.font_datum)
            worksheet.write(6, 11, f'=IFERROR(AN60,{budget.SC._dof})', self.font_integer)
            #NEUTRON FLUX RATIO
            worksheet.write(7, 3, f'=IFERROR(AT40,{budget.NF.x})', self.font_datum)
            worksheet.write(7, 4, f'=IFERROR(AU40,{budget.NF.ux})', self.font_datum)
            worksheet.write(7, 11, f'=IFERROR(BB40,{budget.NF._dof})', self.font_integer)
            #EFFICIENCY RATIO
            worksheet.write(8, 3, f'=IFERROR(BH43,{budget.EF.x})', self.font_datum)
            worksheet.write(8, 4, f'=IFERROR(BI43,{budget.EF.ux})', self.font_datum)
            worksheet.write(8, 11, f'=IFERROR(BP43,{budget.EF._dof})', self.font_integer)
            #MASS RATIO
            worksheet.write(9, 3, f'=IFERROR(BV39,{budget.MSS.x})', self.font_datum)
            worksheet.write(9, 4, f'=IFERROR(BW39,{budget.MSS.ux})', self.font_datum)
            worksheet.write(9, 11, f'=IFERROR(CD39,{budget.MSS._dof})', self.font_integer)
            #BLANK CORRECTION
            worksheet.write(10, 3, f'=IFERROR(CJ32,{budget.BNK.x})', self.font_datum)
            worksheet.write(10, 4, f'=IFERROR(CK32,{budget.BNK.ux})', self.font_datum)
            worksheet.write(10, 11, f'=IFERROR(CR32,{budget.BNK._dof})', self.font_integer)
            #U FISSION CORRECTION
            worksheet.write(11, 3, f'=IFERROR(CX42,{budget.FSS.x})', self.font_datum)
            worksheet.write(11, 4, f'=IFERROR(CY42,{budget.FSS.ux})', self.font_datum)
            worksheet.write(11, 11, f'=IFERROR(DF42,{budget.FSS._dof})', self.font_integer) 

        worksheet.protect(self.password)


class SingleBudgetOutput(SingleBudget):
    def __init__(self, budget, filename, lock_cells=False, set_autolinks=False, visible_models=True, hide_grids=True):
        workbook  = xlsxwriter.Workbook(filename, {'nan_inf_to_errors': True})
        workbook.set_tab_ratio(80)
        
        self.password = 'unlock'
        self.lock_cells = lock_cells
        self.set_autolinks = set_autolinks
        self.visible_models = visible_models
        if hide_grids:
            self.hide_gridlines = 2
        else:
            self.hide_gridlines = 0
        self.font_bold = workbook.add_format({'bold': True})
        self.font_ital = workbook.add_format({'italic': True})
        self.font_result = workbook.add_format(
            {'bold': True, 'font_color': 'green', 'num_format': '0.000E+00'})
        self.font_uncresult = workbook.add_format(
            {'bold': True, 'font_color': 'green', 'num_format': '0.0E+00'})
        self.font_datum = workbook.add_format(
            {'num_format': '0.00E+00'})
        if self.lock_cells:
            self.font_inputdatum = workbook.add_format(
            {'num_format': '0.00E+00', 'locked': self.lock_cells})
            self.font_inputdof = workbook.add_format(
            {'num_format': '0', 'locked': self.lock_cells})
        else:
            self.font_inputdatum = workbook.add_format(
            {'num_format': '0.00E+00', 'locked': self.lock_cells, 'bottom':6, 'bottom_color': '#2AAA8A'})
            self.font_inputdof = workbook.add_format(
            {'num_format': '0', 'locked': self.lock_cells, 'bottom':6, 'bottom_color': '#2AAA8A'})
        self.font_pct = workbook.add_format({'num_format': 0x0a})
        self.font_DL = workbook.add_format(
            {'bold': True, 'font_color': '#FF6347', 'num_format': '0.0E+00'})
        self.font_zscore = workbook.add_format(
            {'bold': True, 'font_color': '#2A2CC9', 'num_format': '0.0'})
        self.font_kvalue = workbook.add_format(
            {'num_format': '0.00'})
        self.font_integer = workbook.add_format(
            {'num_format': '0'})
        self.font_sups = workbook.add_format({'font_script': 1})
        self.font_subs = workbook.add_format({'font_script': 2})
        self.font_gray = workbook.add_format({'font_color': 'gray'})
        self.font_grayit = workbook.add_format({'italic': True, 'font_color': 'gray'})
        self.font_graysub = workbook.add_format({'font_script': 2, 'font_color': 'gray'})
        self.font_graypct = workbook.add_format({'num_format': 0x0a, 'font_color': 'gray'})
        self.font_dateandtime = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})
        self.grey_header = workbook.add_format({'bg_color': '#e7e6e6', 'font_color': 'black', 'bold': True})
        self.grey_info = workbook.add_format({'bg_color': '#e7e6e6', 'font_color': 'black', 'italic': True, 'left': 3})
        self.grey_fill = workbook.add_format({'bg_color': '#e7e6e6', 'font_color': 'black'})
        self.font_greyresult = workbook.add_format(
            {'bold': False, 'font_color': 'gray', 'num_format': '0.00E+00'})
        self.font_greyuncresult = workbook.add_format(
            {'bold': False, 'font_color': 'gray', 'num_format': '0.0E+00'})
        try:
            self.font_sym = workbook.add_format({'font_name': 'Symbol'})
            self.font_graysym = workbook.add_format({'font_name': 'Symbol', 'font_color': 'gray'})
        except:
            self.font_sym = workbook.add_format({'font_name': 'Times New Roman'})
            self.font_graysym = workbook.add_format(
                {'font_name': 'Times New Roman', 'font_color': 'gray'})
        self.ital_aligned = workbook.add_format({'italic': True, 'align': 'right'})
        self.limit_cut = workbook.add_format({'right': 3})

        try:
            sample_namelist = sorted(set([_bud.sample_id for _bud in budget]))
        except TypeError:
            sample_namelist = []
        agg_budgets = self.create_aggregation(budget, sample_namelist)
            
        self.manage_sheets(budget, workbook, agg_budgets)
        workbook.close()

    def create_aggregation(self, budget, sample_namelist):
        agg_budgets = [BudgetAggregator(name) for name in sample_namelist]

        if len(agg_budgets) == 0:
            return agg_budgets

        for _bud in budget:
            for item in agg_budgets:
                if item.sample_name == _bud.sample_id:
                    item.add_B(_bud)
                    break

        return agg_budgets

    def manage_sheets(self, budget, workbook, agg_budgets):
        try:
            len(budget)
            chart_ave = workbook.add_chart({'type': 'line'})
            chart_bar = workbook.add_chart({"type": "column", "subtype": "percent_stacked"})
            chart_doe = workbook.add_chart({'type': 'line'})
            chart_pie = workbook.add_chart({"type": "pie"})
            summary_worksheet = workbook.add_worksheet('Summary')
            for agg_budget in agg_budgets:
                workbook.add_worksheet(agg_budget.code)
        except TypeError:
            super().__init__(budget, workbook)

        try:
            for budget_i in budget:
                super().__init__(budget_i, workbook)
            target = budget[0].target
            self.fill_sample_pages(agg_budgets, workbook)
            self.fill_summay_page(agg_budgets, summary_worksheet, chart_ave, chart_doe, chart_bar, chart_pie, target)
        except TypeError:
            pass

    def fill_sample_pages(self, agg_budget, workbook):
        for item in agg_budget:
            _chart_ave = workbook.add_chart({'type': 'line'})
            _chart_doe = workbook.add_chart({'type': 'line'})
            worksheet = workbook.get_worksheet_by_name(item.code)
            self.fill_sample_page(item, worksheet, _chart_ave, _chart_doe)

    def fill_sample_page(self, item, worksheet, chart_ave, chart_doe):
        worksheet.hide_gridlines(self.hide_gridlines)
        worksheet.write(0, 0, item.sample_name, self.grey_header)

        worksheet.write(1, 0, 'result', self.grey_info)
        worksheet.write(1, 1, '', self.grey_fill)
        worksheet.write(1, 2, '', self.grey_fill)
        worksheet.write(1, 3, '', self.grey_fill)
        worksheet.write(1, 4, 'info', self.grey_info)
        worksheet.write(1, 5, '', self.grey_fill)
        worksheet.write(1, 6, '', self.grey_fill)
        worksheet.write(1, 7, '', self.grey_fill)
        worksheet.write(1, 8, 'relative difference to average variance', self.grey_info)
        worksheet.write(1, 9, 'contribution to variance', self.grey_info)
        worksheet.write(1, 10, '', self.grey_fill)
        worksheet.write(1, 11, '', self.grey_fill)
        worksheet.write(1, 12, '', self.grey_fill)
        worksheet.write(1, 13, '', self.grey_fill)
        worksheet.write(1, 14, '', self.grey_fill)
        worksheet.write(1, 15, '', self.grey_fill)
        worksheet.write(1, 16, '', self.grey_fill)
        worksheet.write(1, 17, 'ID & link to budget', self.grey_info)
        worksheet.write(1, 18, '', self.grey_fill)
        worksheet.write(1, 19, '', self.grey_fill)
        worksheet.write(1, 20, '', self.grey_fill)
        worksheet.write(1, 21, 'DoE', self.grey_info)
        worksheet.write(1, 22, '', self.grey_fill)
        worksheet.write(1, 23, 'DoF', self.grey_info)
        worksheet.write(1, 24, '', self.grey_fill)
        worksheet.write(1, 25, '', self.grey_fill)
        worksheet.write(1, 26, '', self.grey_fill)
        worksheet.write(1, 27, '', self.grey_fill)
        worksheet.write(1, 28, '', self.grey_fill)
        worksheet.write(1, 29, '', self.grey_fill)
        worksheet.write(1, 30, '', self.grey_fill)

        worksheet.write_rich_string(2, 0, self.font_ital,'w',self.font_subs,'smp i',' / g g',self.font_sups,'-1')
        worksheet.write_rich_string(2, 1, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'smp i',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(2, 2, self.font_ital,'u',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'smp i',') / 1')
        worksheet.write_rich_string(2, 3, self.font_ital,'U','(',self.font_ital,'w',self.font_subs,'smp i',') / g g',self.font_sups,'-1')
        worksheet.write(2, 4, 'emitter')
        worksheet.write_rich_string(2, 5, self.font_ital,'E',' / keV')
        worksheet.write(2, 6, 'sample pos / mm')
        worksheet.write(2, 7, 'method')
        worksheet.write(2, 8, '±50%')
        worksheet.write(2, 9, 'net area ratio')
        worksheet.write(2, 10, 'decay ratio')
        worksheet.write(2, 11, 'k0 ratio')
        worksheet.write(2, 12, 'neutron flux ratio')
        worksheet.write(2, 13, 'efficiency ratio')
        worksheet.write(2, 14, 'mass ratio')
        worksheet.write(2, 15, 'blank correction')
        worksheet.write(2, 16, 'U fission correction')
        worksheet.write(2, 17, 'sample code')
        worksheet.write(2, 18, 'link to budget')
        worksheet.write(2, 21, 'DoE')
        worksheet.write(2, 22, 'U(DoE)')
        worksheet.write(2, 23, 'net area ratio')
        worksheet.write(2, 24, 'decay ratio')
        worksheet.write(2, 25, 'k0 ratio')
        worksheet.write(2, 26, 'neutron flux ratio')
        worksheet.write(2, 27, 'efficiency ratio')
        worksheet.write(2, 28, 'mass ratio')
        worksheet.write(2, 29, 'blank correction')
        worksheet.write(2, 30, 'U fission correction')

        for nn, pcode in enumerate(item.budget_links):

            link_result = f"='{pcode}'!D16"
            worksheet.write(3+nn, 0, link_result, self.font_result)
            link_result = f"='{pcode}'!E16"
            worksheet.write(3+nn, 1, link_result, self.font_uncresult)
            link_result = f"='{pcode}'!F16"
            worksheet.write(3+nn, 2, link_result, self.font_pct)
            link_result = f"='{pcode}'!I16"
            worksheet.write(3+nn, 3, link_result, self.font_datum)
            link_result = f"='{pcode}'!D1"
            worksheet.write(3+nn, 4, link_result)
            link_result = f"='{pcode}'!F1"
            worksheet.write(3+nn, 5, link_result)
            link_result = f"='{pcode}'!P10"
            worksheet.write(3+nn, 6, link_result)
            link_result = f"='{pcode}'!P2"
            worksheet.write(3+nn, 7, link_result)

            link_result = f"='{pcode}'!J5"
            worksheet.write(3+nn, 9, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J6"
            worksheet.write(3+nn, 10, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J7"
            worksheet.write(3+nn, 11, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J8"
            worksheet.write(3+nn, 12, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J9"
            worksheet.write(3+nn, 13, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J10"
            worksheet.write(3+nn, 14, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J11"
            worksheet.write(3+nn, 15, link_result, self.limit_cut)
            link_result = f"='{pcode}'!J12"
            worksheet.write(3+nn, 16, link_result, self.limit_cut)
           
            link_result = f"='{pcode}'!P7"
            worksheet.write(3+nn, 17, link_result)
            worksheet.write_url(f'S{3+nn+1}', f"internal:'{pcode}'!A1")

            link_result = f"='{pcode}'!L5"
            worksheet.write(3+nn, 23, link_result)
            link_result = f"='{pcode}'!L6"
            worksheet.write(3+nn, 24, link_result)
            link_result = f"='{pcode}'!L7"
            worksheet.write(3+nn, 25, link_result)
            link_result = f"='{pcode}'!L8"
            worksheet.write(3+nn, 26, link_result)
            link_result = f"='{pcode}'!L9"
            worksheet.write(3+nn, 27, link_result)
            link_result = f"='{pcode}'!L10"
            worksheet.write(3+nn, 28, link_result)
            link_result = f"='{pcode}'!L11"
            worksheet.write(3+nn, 29, link_result)
            link_result = f"='{pcode}'!L12"
            worksheet.write(3+nn, 30, link_result)

        worksheet.conditional_format(f'I4:I{3+nn+1}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':-0.5, 'max_value':0.5, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left', 'bar_negative_color_same':True, 'bar_negative_border_color_same':True})
        
        worksheet.conditional_format(f'J4:Q{3+nn+1}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#c9291a', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        idx_ave = 3+nn+1

        worksheet.write(idx_ave, 0, 'average', self.grey_info)
        worksheet.write(idx_ave, 1, '', self.grey_fill)
        worksheet.write(idx_ave, 2, '', self.grey_fill)
        worksheet.write(idx_ave, 3, '', self.grey_fill)
        worksheet.write(idx_ave, 4, '', self.grey_fill)
        worksheet.write(idx_ave, 5, '', self.grey_fill)
        worksheet.write(idx_ave, 6, '', self.grey_fill)

        worksheet.write_rich_string(idx_ave+1, 0, self.font_ital,'w',self.font_subs,'smp j',' / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 1, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 2, self.font_ital,'s','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 3, self.font_ital,'u*','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 4, self.font_ital,'u*',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'smp j',') / 1')
        worksheet.write_rich_string(idx_ave+1, 5, self.font_ital,'U*','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write(idx_ave+1, 6, 'suspected outliers')

        #REFERENCE FOR FUTURE USE
        item._update(6)
        how_many_budget = item.len()

        weights = ','.join([f'1/B{4+nidx}^2' for nidx in range(item.len())])
        comps = ','.join([f'A{4+nidx}/B{4+nidx}^2' for nidx in range(item.len())])

        fml = f'=SUM({comps}) / SUM({weights})'
        worksheet.write(idx_ave+2, 0, fml, self.font_result)
        fml = f'=SQRT(SUM(D{item.index_row+6}:D{item.index_row+13}))'
        worksheet.write(idx_ave+2, 1, fml, self.font_uncresult)
        if how_many_budget > 1:
            fml = f'=STDEV(A4:A{idx_ave})'
        else:
            fml = '=0'
        worksheet.write(idx_ave+2, 2, fml, self.font_uncresult)

        unc_NOCORR = f'B{idx_ave+3}'
        if how_many_budget == 1:
            fml = f'=B{idx_ave+3}'
            unc_CORR = f'B{idx_ave+3}'
        elif how_many_budget <= 3:
            fml = f'=SQRT(B{idx_ave+3}^2+({4}-1)/({4}-3)*C{idx_ave+3}^2/{how_many_budget})'
            unc_CORR = f'SQRT(B{idx_ave+3}^2+C{idx_ave+3}^2)'
        else:
            fml = f'=SQRT(B{idx_ave+3}^2+({how_many_budget}-1)/({how_many_budget}-3)*C{idx_ave+3}^2/{how_many_budget})'
            unc_CORR = f'SQRT(B{idx_ave+3}^2+({how_many_budget}-1)/({how_many_budget}-3)*C{idx_ave+3}^2/{how_many_budget})'

        fml = f'=D{idx_ave+3}/A{idx_ave+3}'
        worksheet.write(idx_ave+2, 4, fml, self.font_pct)
        fml = f'=TINV(1-0.95,D{idx_ave+4})*D{idx_ave+3}'
        worksheet.write(idx_ave+2, 5, fml, self.font_uncresult)
        conds = ','.join([f'IF(ABS(V{4+nnx})-W{4+nnx}<0,0,1)' for nnx in range(how_many_budget)])
        fml = f'=SUM({conds})'
        worksheet.write(idx_ave+2, 6, fml)

        fml = f'=IF(G{idx_ave+3}>0,{unc_CORR},{unc_NOCORR})'
        worksheet.write(idx_ave+2, 3, fml, self.font_uncresult)

        #second line
        worksheet.write(idx_ave+3, 0, 'DoF', self.ital_aligned)
        fml = f'=INT(B{item.index_row}^4/(D{item.index_row+6}^2/G{item.index_row+6}+D{item.index_row+7}^2/G{item.index_row+7}+D{item.index_row+8}^2/G{item.index_row+8}+D{item.index_row+9}^2/G{item.index_row+9}+D{item.index_row+10}^2/G{item.index_row+10}+D{item.index_row+11}^2/G{item.index_row+11}+D{item.index_row+12}^2/G{item.index_row+12}+D{item.index_row+13}^2/G{item.index_row+13}))'
        worksheet.write(idx_ave+3, 1, fml, self.font_integer)
        fml = f'={how_many_budget - 1}'
        worksheet.write(idx_ave+3, 2, fml, self.font_integer)

        #dof formula depending on sample numerosity
        dof_NOCORR = f'B{idx_ave+4}'
        if how_many_budget == 1:
            dof_CORR = f'B{idx_ave+4}'
        elif how_many_budget <=3:
            dof_CORR = f'INT(D{idx_ave+3}^4/(B{idx_ave+3}^4/B{idx_ave+4}+C{idx_ave+3}^4/C{idx_ave+4}))'
        else:
            dof_CORR = f'INT(D{idx_ave+3}^4/(B{idx_ave+3}^4/B{idx_ave+4}+(({how_many_budget}-1)/({how_many_budget}-3)*C{idx_ave+3}^2/{how_many_budget})^2/C{idx_ave+4}))'

        fml = f'=IF(G{idx_ave+3}>0,{dof_CORR},{dof_NOCORR})'
        worksheet.write(idx_ave+3, 3, fml, self.font_integer)
        worksheet.write(idx_ave+3, 4, 'k', self.ital_aligned)
        fml = f'=F{idx_ave+3}/D{idx_ave+3}'
        worksheet.write(idx_ave+3, 5, fml, self.font_kvalue)
        fml = f'=G{idx_ave+3}'
        worksheet.write(idx_ave+3, 6, fml)

        worksheet.conditional_format(f'G{idx_ave+4}:G{idx_ave+4}', {'type':'icon_set', 'icon_style': '3_symbols_circled', 'icons_only': True, 'reverse_icons': True, 'icons': [{'criteria': '>=', 'type': 'number', 'value': 1.0},
               {'criteria': '>=',  'type': 'number', 'value': 0.5},
               {'criteria': '<', 'type': 'number', 'value': 0.5}]})

        idx_tbud = idx_ave+5

        worksheet.write(idx_tbud, 0, 'detail uncertainty evaluation of average', self.grey_info)
        worksheet.write(idx_tbud, 1, '', self.grey_fill)
        worksheet.write(idx_tbud, 2, '', self.grey_fill)
        worksheet.write(idx_tbud, 3, '', self.grey_fill)
        worksheet.write(idx_tbud, 4, '', self.grey_fill)
        worksheet.write(idx_tbud, 5, '', self.grey_fill)
        worksheet.write(idx_tbud, 6, '', self.grey_fill)
        worksheet.write(idx_tbud+1, 0, 'Quantity')
        worksheet.write(idx_tbud+1, 2, 'Unit')
        worksheet.write(idx_tbud+1, 3, 'Variance')
        worksheet.write(idx_tbud+1, 4, 'contribution to variance')

        worksheet.write_rich_string(idx_tbud+2, 0, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(idx_tbud+2, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(idx_tbud+2, 3, self.font_ital, 'u', self.font_sups, '2', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(idx_tbud+2, 4, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(idx_tbud+2, 5, self.font_ital, 'I', ' (bar)')
        worksheet.write(idx_tbud+2, 6, 'DoF')

        worksheet.write(idx_tbud+3, 0, 'net area ratio')
        worksheet.write(idx_tbud+3, 2, '1')
        sequence = ','.join([f'1/(B{4+nidx}^2*J{4+nidx})' for nidx in range(item.len())])
        fml = f'=1/SUM({sequence})'
        worksheet.write(idx_tbud+3, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+6}/B{item.index_row}^2'
        worksheet.write(idx_tbud+3, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+6}'
        worksheet.write(idx_tbud+3, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(X4:X{idx_ave}))'
        worksheet.write(idx_tbud+3, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+4, 0, 'decay ratio')
        worksheet.write(idx_tbud+4, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*K{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+4, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+7}/B{item.index_row}^2'
        worksheet.write(idx_tbud+4, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+7}'
        worksheet.write(idx_tbud+4, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(Y4:Y{idx_ave}))'
        worksheet.write(idx_tbud+4, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+5, 0, 'k0 ratio')
        worksheet.write(idx_tbud+5, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*L{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+5, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+8}/B{item.index_row}^2'
        worksheet.write(idx_tbud+5, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+8}'
        worksheet.write(idx_tbud+5, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(Z4:Z{idx_ave}))'
        worksheet.write(idx_tbud+5, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+6, 0, 'neutron flux ratio')
        worksheet.write(idx_tbud+6, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*M{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+6, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+9}/B{item.index_row}^2'
        worksheet.write(idx_tbud+6, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+9}'
        worksheet.write(idx_tbud+6, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AA4:AA{idx_ave}))'
        worksheet.write(idx_tbud+6, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+7, 0, 'efficiency ratio')
        worksheet.write(idx_tbud+7, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*N{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+7, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+10}/B{item.index_row}^2'
        worksheet.write(idx_tbud+7, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+10}'
        worksheet.write(idx_tbud+7, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AB4:AB{idx_ave}))'
        worksheet.write(idx_tbud+7, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+8, 0, 'mass ratio')
        worksheet.write_rich_string(idx_tbud+8, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*O{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+8, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+11}/B{item.index_row}^2'
        worksheet.write(idx_tbud+8, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+11}'
        worksheet.write(idx_tbud+8, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AC4:AC{idx_ave}))'
        worksheet.write(idx_tbud+8, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+9, 0, 'blank correction')
        worksheet.write_rich_string(idx_tbud+9, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*P{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+9, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+12}/B{item.index_row}^2'
        worksheet.write(idx_tbud+9, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+12}'
        worksheet.write(idx_tbud+9, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AD4:AD{idx_ave}))'
        worksheet.write(idx_tbud+9, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+10, 0, 'U fission correction')
        worksheet.write_rich_string(idx_tbud+10, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*Q{4+nidx}' for nidx in range(item.len())])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+10, 3, fml, self.font_datum)
        fml = f'=D{item.index_row+13}/B{item.index_row}^2'
        worksheet.write(idx_tbud+10, 4, fml, self.font_pct)
        fml = f'=E{item.index_row+13}'
        worksheet.write(idx_tbud+10, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AE4:AE{idx_ave}))'
        worksheet.write(idx_tbud+10, 6, fml, self.font_integer)

        for nn in range(item.len()):
            cells = ",".join([f"B{4+nidx}^2" for nidx in range(item.len())])
            _aver = f'AVERAGE({cells})'
            fml = f'=(B{4+nn}^2-{_aver}) / {_aver}'
            worksheet.write(3+nn, 8, fml)
            fml = f'=A{4+nn}-A{idx_ave+3}'
            worksheet.write(3+nn, 21, fml, self.font_datum)
            fml = f'=2*SQRT(B{4+nn}^2*J{4+nn} + B{item.index_row}^2*F{item.index_row+6})'
            worksheet.write(3+nn, 22, fml, self.font_datum)

        worksheet.conditional_format(f'F{item.index_row+6}:F{item.index_row+13}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#c9291a', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        #hidden values for graph
        worksheet.write(idx_ave+2, 8, f'=A{idx_ave+3}+F{idx_ave+3}')
        worksheet.write(idx_ave+2, 9, f'=A{idx_ave+3}-F{idx_ave+3}')

        if item.max_value > 1:
            ymax = 1
        else:
            ymax = item.max_value

        if item.min_value < 0:
            ymin = 0
        else:
            ymin = item.min_value

        x_size = 7
        y_size = 11
        chart_ave.add_series({'values': f"='{item.code}'!A4:A{idx_ave}",'marker': {'type': 'circle', 'size': 5, 'border': {'color': 'black'}, 'fill': {'color': 'black'}}, 'line': {'none': True}, 'y_error_bars': {'type' : 'custom', 'plus_values': f"='{item.code}'!D4:D{idx_ave}", 'minus_values': f"='{item.code}'!D4:D{idx_ave}"}})

        #average
        ave_ref = ','.join([f"'{item.code}'!A{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_ref}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'solid'}})
        ave_U = ','.join([f"'{item.code}'!I{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_U}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'dash'}})
        ave_U = ','.join([f"'{item.code}'!J{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_U}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'dash'}})
        chart_ave.set_y_axis({'name': 'w / g g-1', 'name_font': {'size': 11}, 'num_format': '0.00E+00', 'min': ymin, 'max': ymax})
        chart_ave.set_legend({'none': True})
        chart_ave.set_title({'name': f"='{item.code}'!A1", 'name_font': {'size': 14}})
        chart_ave.set_size({'width': x_size*64, 'height': y_size*20})
        worksheet.insert_chart(idx_ave+2, 8, chart_ave)

        chart_doe.add_series({'values': f"='{item.code}'!V4:V{idx_ave}",'marker': {'type': 'circle', 'size': 5, 'border': {'color': 'black'}, 'fill': {'color': 'black'}}, 'line': {'none': True}, 'y_error_bars': {'type' : 'custom', 'plus_values': f"='{item.code}'!W4:W{idx_ave}", 'minus_values': f"='{item.code}'!W4:W{idx_ave}"}})
        ave0_ref = '{'+','.join([f"{0}"]*how_many_budget)+'}'
        chart_doe.add_series({'values': f'={ave0_ref}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'solid'}})
        chart_doe.set_x_axis({'label_position': 'low'})
        chart_doe.set_y_axis({'name': 'w / g g-1', 'name_font': {'size': 11}, 'num_format': '0.00E+00'})
        chart_doe.set_legend({'none': True})
        chart_doe.set_title({'name': f"='{item.code}'!V3", 'name_font': {'size': 14}})
        chart_doe.set_size({'width': x_size*64, 'height': y_size*20})
        worksheet.insert_chart(idx_ave+13, 8, chart_doe)

        worksheet.protect(self.password)

    def fill_summay_page(self, agg_budget, worksheet, chart_ave, chart_doe, chart_bar, chart_pie, target):
        worksheet.hide_gridlines(self.hide_gridlines)
        worksheet.write(0, 0, target, self.grey_header)

        worksheet.write(1, 0, 'result', self.grey_info)
        worksheet.write(1, 1, '', self.grey_fill)
        worksheet.write(1, 2, '', self.grey_fill)
        worksheet.write(1, 3, '', self.grey_fill)
        worksheet.write(1, 4, 'info', self.grey_info)
        worksheet.write(1, 5, '', self.grey_fill)
        worksheet.write(1, 6, '', self.grey_fill)
        worksheet.write(1, 7, '', self.grey_fill)
        worksheet.write(1, 8, 'relative difference to average variance', self.grey_info)
        worksheet.write(1, 9, 'contribution to variance', self.grey_info)
        worksheet.write(1, 10, '', self.grey_fill)
        worksheet.write(1, 11, '', self.grey_fill)
        worksheet.write(1, 12, '', self.grey_fill)
        worksheet.write(1, 13, '', self.grey_fill)
        worksheet.write(1, 14, '', self.grey_fill)
        worksheet.write(1, 15, '', self.grey_fill)
        worksheet.write(1, 16, '', self.grey_fill)
        worksheet.write(1, 17, 'ID & link to budget', self.grey_info)
        worksheet.write(1, 18, '', self.grey_fill)
        worksheet.write(1, 19, '', self.grey_fill)
        worksheet.write(1, 20, '', self.grey_fill)
        worksheet.write(1, 21, 'DoE', self.grey_info)
        worksheet.write(1, 22, '', self.grey_fill)
        worksheet.write(1, 23, 'DoF', self.grey_info)
        worksheet.write(1, 24, '', self.grey_fill)
        worksheet.write(1, 25, '', self.grey_fill)
        worksheet.write(1, 26, '', self.grey_fill)
        worksheet.write(1, 27, '', self.grey_fill)
        worksheet.write(1, 28, '', self.grey_fill)
        worksheet.write(1, 29, '', self.grey_fill)
        worksheet.write(1, 30, '', self.grey_fill)

        worksheet.write_rich_string(2, 0, self.font_ital,'w',self.font_subs,'smp j',' / g g',self.font_sups,'-1')
        worksheet.write_rich_string(2, 1, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(2, 2, self.font_ital,'u',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'smp j',') / 1')
        worksheet.write_rich_string(2, 3, self.font_ital,'U','(',self.font_ital,'w',self.font_subs,'smp j',') / g g',self.font_sups,'-1')
        worksheet.write(2, 4, 'k')
        worksheet.write(2, 5, 'n')
        worksheet.write(2, 6, 'suspected outliers')
        worksheet.write(2, 8, '±50%')
        worksheet.write(2, 9, 'net area ratio')
        worksheet.write(2, 10, 'decay ratio')
        worksheet.write(2, 11, 'k0 ratio')
        worksheet.write(2, 12, 'neutron flux ratio')
        worksheet.write(2, 13, 'efficiency ratio')
        worksheet.write(2, 14, 'mass ratio')
        worksheet.write(2, 15, 'blank correction')
        worksheet.write(2, 16, 'U fission correction')
        worksheet.write(2, 17, 'sample code')
        worksheet.write(2, 18, 'link to budget')
        worksheet.write(2, 21, 'DoE')
        worksheet.write(2, 22, 'U(DoE)')
        worksheet.write(2, 23, 'net area ratio')
        worksheet.write(2, 24, 'decay ratio')
        worksheet.write(2, 25, 'k0 ratio')
        worksheet.write(2, 26, 'neutron flux ratio')
        worksheet.write(2, 27, 'efficiency ratio')
        worksheet.write(2, 28, 'mass ratio')
        worksheet.write(2, 29, 'blank correction')
        worksheet.write(2, 30, 'U fission correction')
        worksheet.write(2, 31, '# working datum')

        for nn, budget_i in enumerate(agg_budget):
            pcode = budget_i.code

            link_result = f"='{pcode}'!A{budget_i.index_row}"
            worksheet.write(3+nn, 0, link_result, self.font_result)
            link_result = f"='{pcode}'!D{budget_i.index_row}"
            worksheet.write(3+nn, 1, link_result, self.font_uncresult)
            link_result = f"='{pcode}'!E{budget_i.index_row}"
            worksheet.write(3+nn, 2, link_result, self.font_pct)
            link_result = f"='{pcode}'!F{budget_i.index_row}"
            worksheet.write(3+nn, 3, link_result, self.font_datum)
            link_result = f"='{pcode}'!F{budget_i.index_row+1}"
            worksheet.write(3+nn, 4, link_result, self.font_kvalue)
            link_result = f"={budget_i.len()}"
            worksheet.write(3+nn, 5, link_result, self.font_integer)
            link_result = f"='{pcode}'!G{budget_i.index_row}"
            worksheet.write(3+nn, 6, link_result)
            fml = f'=G{4+nn}'
            worksheet.write(3+nn, 7, fml)

            link_result = f"='{pcode}'!F{budget_i.index_row+6}"
            worksheet.write(3+nn, 9, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+7}"
            worksheet.write(3+nn, 10, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+8}"
            worksheet.write(3+nn, 11, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+9}"
            worksheet.write(3+nn, 12, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+10}"
            worksheet.write(3+nn, 13, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+11}"
            worksheet.write(3+nn, 14, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+12}"
            worksheet.write(3+nn, 15, link_result, self.limit_cut)
            link_result = f"='{pcode}'!F{budget_i.index_row+13}"
            worksheet.write(3+nn, 16, link_result, self.limit_cut)
           
            link_result = f"='{pcode}'!A1"
            worksheet.write(3+nn, 17, link_result)
            worksheet.write_url(f'S{3+nn+1}', f"internal:'{pcode}'!A1")

            link_result = f"='{pcode}'!G{budget_i.index_row+6}"
            worksheet.write(3+nn, 23, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+7}"
            worksheet.write(3+nn, 24, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+8}"
            worksheet.write(3+nn, 25, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+9}"
            worksheet.write(3+nn, 26, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+10}"
            worksheet.write(3+nn, 27, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+11}"
            worksheet.write(3+nn, 28, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+12}"
            worksheet.write(3+nn, 29, link_result)
            link_result = f"='{pcode}'!G{budget_i.index_row+13}"
            worksheet.write(3+nn, 30, link_result)

            fml = f'=1-(J{3+nn+1}+N{3+nn+1})'
            worksheet.write(3+nn, 31, fml, self.font_datum)

        worksheet.conditional_format(f'H4:H{3+nn+1}', {'type':'icon_set', 'icon_style': '3_symbols_circled', 'icons_only': True, 'reverse_icons': True, 'icons': [{'criteria': '>=', 'type': 'number', 'value': 1.0},
               {'criteria': '>=',  'type': 'number', 'value': 0.5},
               {'criteria': '<', 'type': 'number',    'value': 0.5}]})

        worksheet.conditional_format(f'I4:I{3+nn+1}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#173c78', 'bar_only':True, 'min_value':-0.5, 'max_value':0.5, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left', 'bar_negative_color_same':True, 'bar_negative_border_color_same':True})
        
        worksheet.conditional_format(f'J4:Q{3+nn+1}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#c9291a', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        idx_ave = 3+nn+1

        worksheet.write(idx_ave, 0, 'average', self.grey_info)
        worksheet.write(idx_ave, 1, '', self.grey_fill)
        worksheet.write(idx_ave, 2, '', self.grey_fill)
        worksheet.write(idx_ave, 3, '', self.grey_fill)
        worksheet.write(idx_ave, 4, '', self.grey_fill)
        worksheet.write(idx_ave, 5, '', self.grey_fill)
        worksheet.write(idx_ave, 6, '', self.grey_fill)

        worksheet.write_rich_string(idx_ave+1, 0, self.font_ital,'w',self.font_subs,'smp',' / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 1, self.font_ital,'u','(',self.font_ital,'w',self.font_subs,'smp',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 2, self.font_ital,'s','(',self.font_ital,'w',self.font_subs,'smp',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 3, self.font_ital,'u*','(',self.font_ital,'w',self.font_subs,'smp',') / g g',self.font_sups,'-1')
        worksheet.write_rich_string(idx_ave+1, 4, self.font_ital,'u*',self.font_subs,'r','(',self.font_ital,'w',self.font_subs,'smp',') / 1')
        worksheet.write_rich_string(idx_ave+1, 5, self.font_ital,'U*','(',self.font_ital,'w',self.font_subs,'smp',') / g g',self.font_sups,'-1')
        worksheet.write(idx_ave+1, 6, 'inhomogeneities')

        how_many_budget = len(agg_budget)

        fml = f'=AVERAGE(A4:A{idx_ave})'
        worksheet.write(idx_ave+2, 0, fml, self.font_result)

        #regular (meaning all contributions are similar) the easy way
        fml = f'=SQRT(SUM(D{idx_ave+9}:D{idx_ave+16}))'
        worksheet.write(idx_ave+2, 1, fml, self.font_uncresult)

        if how_many_budget > 1:
            fml = f'=STDEV(A4:A{idx_ave})'
        else:
            fml = '=0'
        worksheet.write(idx_ave+2, 2, fml, self.font_uncresult)

        #uncertainty formula depending on sample numerosity
        unc_NOCORR = f'B{idx_ave+3}'
        if how_many_budget == 1:
            unc_CORR = f'B{idx_ave+3}'
        elif how_many_budget <= 3:
            unc_CORR = f'SQRT(B{idx_ave+3}^2+C{idx_ave+3}^2)'
        else:
            unc_CORR = f'SQRT(B{idx_ave+3}^2+({how_many_budget}-1)/({how_many_budget}-3)*C{idx_ave+3}^2/{how_many_budget})'

        fml = f'=D{idx_ave+3}/A{idx_ave+3}'
        worksheet.write(idx_ave+2, 4, fml, self.font_pct)
        fml = f'=TINV(1-0.95,D{idx_ave+4})*D{idx_ave+3}'
        worksheet.write(idx_ave+2, 5, fml, self.font_uncresult)
        conds = ','.join([f'IF(ABS(V{4+nnx})-W{4+nnx}<0,0,1)' for nnx in range(how_many_budget)])
        fml = f'=SUM({conds})'
        worksheet.write(idx_ave+2, 6, fml)

        #second line
        worksheet.write(idx_ave+3, 0, 'DoF', self.ital_aligned)
        fml = f'=INT(B{idx_ave+3}^4/SUM(D{idx_ave+9}^2/G{idx_ave+9},D{idx_ave+10}^2/G{idx_ave+10},D{idx_ave+11}^2/G{idx_ave+11},D{idx_ave+12}^2/G{idx_ave+12},D{idx_ave+13}^2/G{idx_ave+13},D{idx_ave+14}^2/G{idx_ave+14},D{idx_ave+15}^2/G{idx_ave+15},D{idx_ave+16}^2/G{idx_ave+16}))'
        worksheet.write(idx_ave+3, 1, fml, self.font_integer)
        
        fml = f'={how_many_budget - 1}'
        worksheet.write(idx_ave+3, 2, fml, self.font_integer)

        #dof formula depending on sample numerosity
        dof_NOCORR = f'B{idx_ave+4}'
        if how_many_budget == 1:
            dof_CORR = f'B{idx_ave+4}'
        elif how_many_budget <=3:
            dof_CORR = f'INT(D{idx_ave+3}^4/(B{idx_ave+3}^4/B{idx_ave+4}+C{idx_ave+3}^4/C{idx_ave+4}))'
        else:
            dof_CORR = f'INT(D{idx_ave+3}^4/(B{idx_ave+3}^4/B{idx_ave+4}+(({how_many_budget}-1)/({how_many_budget}-3)*C{idx_ave+3}^2/{how_many_budget})^2/C{idx_ave+4}))'

        worksheet.write(idx_ave+3, 4, 'k', self.ital_aligned)
        fml = f'=F{idx_ave+3}/D{idx_ave+3}'
        worksheet.write(idx_ave+3, 5, fml, self.font_kvalue)
        fml = f'=G{idx_ave+3}'
        worksheet.write(idx_ave+3, 6, fml)

        fml = f'=IF(G{idx_ave+3}>0,{unc_CORR},{unc_NOCORR})'
        worksheet.write(idx_ave+2, 3, fml, self.font_uncresult)
        fml = f'=IF(G{idx_ave+3}>0,{dof_CORR},{dof_NOCORR})'
        worksheet.write(idx_ave+3, 3, fml, self.font_integer)

        worksheet.conditional_format(f'G{idx_ave+4}:G{idx_ave+4}', {'type':'icon_set', 'icon_style': '3_symbols_circled', 'icons_only': True, 'reverse_icons': True, 'icons': [{'criteria': '>=', 'type': 'number', 'value': 1.0},
               {'criteria': '>=',  'type': 'number', 'value': 0.5},
               {'criteria': '<', 'type': 'number', 'value': 0.5}]})

        for nn, budget_i in enumerate(agg_budget):
            cells = ",".join([f"B{4+nidx}^2" for nidx in range(len(agg_budget))])
            _aver = f'AVERAGE({cells})'
            fml = f'=(B{3+nn+1}^2-{_aver}) / {_aver}'
            worksheet.write(3+nn, 8, fml)

            fml = f'=A{3+nn+1}-A{idx_ave+3}'
            worksheet.write(3+nn, 21, fml, self.font_datum)
            fml = f'=2*SQRT(B{4+nn}^2*J{4+nn} + B{idx_ave+3}^2*F{idx_ave+9})'
            worksheet.write(3+nn, 22, fml, self.font_datum)

        idx_tbud = idx_ave+5
        worksheet.write(idx_tbud, 0, 'detail uncertainty evaluation of average', self.grey_info)
        worksheet.write(idx_tbud, 1, '', self.grey_fill)
        worksheet.write(idx_tbud, 2, '', self.grey_fill)
        worksheet.write(idx_tbud, 3, '', self.grey_fill)
        worksheet.write(idx_tbud, 4, '', self.grey_fill)
        worksheet.write(idx_tbud, 5, '', self.grey_fill)
        worksheet.write(idx_tbud, 6, '', self.grey_fill)
        worksheet.write(idx_tbud+1, 0, 'Quantity')
        worksheet.write(idx_tbud+1, 2, 'Unit')
        worksheet.write(idx_tbud+1, 3, 'Variance')
        worksheet.write(idx_tbud+1, 4, 'contribution to variance')

        worksheet.write_rich_string(idx_tbud+2, 0, self.font_ital, 'X', self.font_subs, 'i')
        worksheet.write_rich_string(idx_tbud+2, 2, '[', self.font_ital, 'X', self.font_subs, 'i', ']')
        worksheet.write_rich_string(idx_tbud+2, 3, self.font_ital, 'u', self.font_sups, '2', '(', self.font_ital, 'x', self.font_subs, 'i', ')')
        worksheet.write_rich_string(idx_tbud+2, 4, self.font_ital, 'I', ' / %')
        worksheet.write_rich_string(idx_tbud+2, 5, self.font_ital, 'I', ' (bar)')
        worksheet.write(idx_tbud+2, 6, 'DoF')

        worksheet.write(idx_tbud+3, 0, 'net area ratio')
        worksheet.write(idx_tbud+3, 2, '1')
        #aritmetic
        sequence = ','.join([f'B{4+nidx}^2*J{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})/{how_many_budget}'
        worksheet.write(idx_tbud+3, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+9}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+3, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+9}'
        worksheet.write(idx_tbud+3, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(X4:X{idx_ave}))'
        worksheet.write(idx_tbud+3, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+4, 0, 'decay ratio')
        worksheet.write(idx_tbud+4, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*K{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+4, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+10}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+4, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+10}'
        worksheet.write(idx_tbud+4, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(Y4:Y{idx_ave}))'
        worksheet.write(idx_tbud+4, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+5, 0, 'k0 ratio')
        worksheet.write(idx_tbud+5, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*L{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+5, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+11}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+5, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+11}'
        worksheet.write(idx_tbud+5, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(Z4:Z{idx_ave}))'
        worksheet.write(idx_tbud+5, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+6, 0, 'neutron flux ratio')
        worksheet.write(idx_tbud+6, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*M{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+6, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+12}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+6, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+12}'
        worksheet.write(idx_tbud+6, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AA4:AA{idx_ave}))'
        worksheet.write(idx_tbud+6, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+7, 0, 'efficiency ratio')
        worksheet.write(idx_tbud+7, 2, '1')
        sequence = ','.join([f'B{4+nidx}^2*N{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+7, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+13}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+7, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+13}'
        worksheet.write(idx_tbud+7, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AB4:AB{idx_ave}))'
        worksheet.write(idx_tbud+7, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+8, 0, 'mass ratio')
        worksheet.write_rich_string(idx_tbud+8, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*O{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+8, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+14}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+8, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+14}'
        worksheet.write(idx_tbud+8, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AC4:AC{idx_ave}))'
        worksheet.write(idx_tbud+8, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+9, 0, 'blank correction')
        worksheet.write_rich_string(idx_tbud+9, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*P{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+9, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+15}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+9, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+15}'
        worksheet.write(idx_tbud+9, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AD4:AD{idx_ave}))'
        worksheet.write(idx_tbud+9, 6, fml, self.font_integer)

        worksheet.write(idx_tbud+10, 0, 'U fission correction')
        worksheet.write_rich_string(idx_tbud+10, 2, 'g g', self.font_sups, '-1')
        sequence = ','.join([f'B{4+nidx}^2*Q{4+nidx}' for nidx in range(how_many_budget)])
        fml = f'=AVERAGE({sequence})'
        worksheet.write(idx_tbud+10, 3, fml, self.font_datum)
        fml = f'=D{idx_ave+3+13}/B{idx_ave+3}^2'
        worksheet.write(idx_tbud+10, 4, fml, self.font_pct)
        fml = f'=E{idx_ave+3+13}'
        worksheet.write(idx_tbud+10, 5, fml, self.limit_cut)
        fml = f'=INT(AVERAGE(AE4:AE{idx_ave}))'
        worksheet.write(idx_tbud+10, 6, fml, self.font_integer)

        worksheet.conditional_format(f'F{idx_ave+9}:F{idx_ave+16}', {'type':'data_bar', 'min_type':'num', 'max_type':'num', 'bar_color':'#c9291a', 'bar_only':True, 'min_value':0, 'max_value':1, 'bar_border_color':'#0a0a0a', 'bar_solid': True, 'bar_direction': 'left'})

        #hidden values for graph
        worksheet.write(idx_ave+2, 8, f'=A{idx_ave+3}+F{idx_ave+3}')
        worksheet.write(idx_ave+2, 9, f'=A{idx_ave+3}-F{idx_ave+3}')

        max_values = [aggB.max_value for aggB in agg_budget]
        min_values = [aggB.min_value for aggB in agg_budget]

        ymin, ymax = self.alllimits(max_values, min_values)

        x_size = 7
        y_size = 11
        chart_ave.add_series({'values': f"='Summary'!A4:A{4+how_many_budget-1}",'marker': {'type': 'circle', 'size': 5, 'border': {'color': 'black'}, 'fill': {'color': 'black'}}, 'line': {'none': True}, 'y_error_bars': {'type' : 'custom', 'plus_values': f"='Summary'!D4:D{4+how_many_budget-1}", 'minus_values': f"='Summary'!D4:D{4+how_many_budget-1}"}})

        #average
        ave_ref = ','.join([f"'Summary'!A{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_ref}', 'categories': f"='Summary'!R4:R{4+how_many_budget-1}", 'line': {'color': 'red', 'width': 1.5, 'dash_type':'solid'}})
        ave_U = ','.join([f"'Summary'!I{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_U}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'dash'}})
        ave_U = ','.join([f"'Summary'!J{idx_ave+3}"]*how_many_budget)
        chart_ave.add_series({'values': f'={ave_U}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'dash'}})
        chart_ave.set_y_axis({'name': 'w / g g-1', 'name_font': {'size': 11}, 'num_format': '0.00E+00', 'min': ymin, 'max': ymax})
        chart_ave.set_legend({'none': True})
        chart_ave.set_title({'name': "='Summary'!A1", 'name_font': {'size': 14}})
        chart_ave.set_plotarea({'layout': {'x':0.22, 'y':0.23, 'width':1-0.22-0.05, 'height':1-0.23-0.15}})
        chart_ave.set_size({'width': x_size*64, 'height': y_size*20})
        worksheet.insert_chart(idx_ave+2, 8, chart_ave)

        chart_bar.add_series({
        "name": "statistics", "categories": f"='Summary'!R4:R{4+how_many_budget-1}", "values": f"='Summary'!J4:J{4+how_many_budget-1}", 'fill': {'color': '#FFD500'}})
        chart_bar.add_series({
        "name": "efficiency", "categories": f"='Summary'!R4:R{4+how_many_budget-1}", "values": f"='Summary'!N4:N{4+how_many_budget-1}", 'fill': {'color': '#D31E25'}})
        chart_bar.add_series({
        "name": "other", "categories": f"='Summary'!R4:R{4+how_many_budget-1}", "values": f"='Summary'!AF4:AF{4+how_many_budget-1}", 'fill': {'color': 'black'}})
        chart_bar.set_y_axis({"name": "Index / 1", 'name_font': {'size': 11}, 'min': 0, 'max': 1})
        chart_bar.set_legend({'position': 'top'})
        chart_bar.set_plotarea({'layout': {'x':0.22, 'y':0.23, 'width':1-0.22-0.05, 'height':1-0.23-0.2}})
        chart_bar.set_size({'width': x_size*64, 'height': y_size/11*7*20})
        worksheet.insert_chart(idx_ave+13, 8, chart_bar)

        chart_doe.add_series({'values': f"='Summary'!V4:V{4+how_many_budget-1}", 'categories': f"='Summary'!R4:R{4+how_many_budget-1}", 'marker': {'type': 'circle', 'size': 5, 'border': {'color': 'black'}, 'fill': {'color': 'black'}}, 'line': {'none': True}, 'y_error_bars': {'type' : 'custom', 'plus_values': f"='Summary'!W4:W{4+how_many_budget-1}", 'minus_values': f"='Summary'!W4:W{4+how_many_budget-1}"}})
        ave0_ref = '{'+','.join([f"{0}"]*how_many_budget)+'}'
        chart_doe.add_series({'values': f'={ave0_ref}', 'line': {'color': 'red', 'width': 1.5, 'dash_type':'solid'}})
        chart_doe.set_x_axis({'label_position': 'low'})
        chart_doe.set_y_axis({'name': 'w / g g-1', 'name_font': {'size': 11}, 'num_format': '0.00E+00'})
        chart_doe.set_legend({'none': True})
        chart_doe.set_title({'name': "='Summary'!V3", 'name_font': {'size': 14}})
        chart_doe.set_plotarea({'layout': {'x':0.22, 'y':0.23, 'width':1-0.22-0.05, 'height':1-0.23-0.15}})
        chart_doe.set_size({'width': x_size*64, 'height': y_size*20})
        worksheet.insert_chart(idx_ave+20, 8, chart_doe)

        chart_pie.add_series({"name": "", "categories": f"='Summary'!A{idx_ave+9}:A{idx_ave+17}", "values": f"='Summary'!E{idx_ave+9}:E{idx_ave+17}", 'data_labels':{'value':True, 'category':True, 'leader_lines': True, 'position': 'best_fit'}, "points": [
            {"fill": {"color": "#FFD500"}},
            {"fill": {"color": "#369E4B"}},
            {"fill": {"color": "#5DB5B7"}},
            {"fill": {"color": "#31407B"}},
            {"fill": {"color": "#D31E25"}},
            {"fill": {"color": "#8A3F64"}},
            {"fill": {"color": "#4F2E39"}},
            {"fill": {"color": "#A29C98"}}]})
        chart_pie.set_legend({'none': True})
        chart_pie.set_size({'width': 5*64, 'height': 16*20})
        worksheet.insert_chart(idx_ave+18, 0, chart_pie)

        worksheet.protect(self.password)

    def alllimits(self, values_max, values_min):
        tmin, tmax = 1, 0
        for valmax, valmin in zip(values_max, values_min):
            if valmax > tmax:
                tmax = valmax
            if valmin < tmin:
                tmin = valmin
        if tmax > 1:
            ymax = 1
        else:
            ymax = tmax
        
        if tmin < 0:
            ymin = 0
        else:
            ymin = tmin

        if ymin > ymax:
            ymin, ymax = ymax, ymin

        return ymin, ymax

    def _supermax_value(self, values):
        outcome = -1
        average = 0
        for item in values:
            average += item
        average = average / len(values)

        for item in values:
            new_value = abs(item - average)
            if new_value > outcome:
                outcome = new_value
        return outcome


def analysisoutput(result, namefile):
    with open(namefile, 'wb') as filesave:
        pickle.dump(result, filesave)