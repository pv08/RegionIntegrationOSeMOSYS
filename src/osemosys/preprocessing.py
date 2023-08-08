import pandas as pd
from src.utils.functions import mkdir_if_not_exists
from tqdm import tqdm
def CatchUniVariateData(region, data):
    """
        Applied on: AccumulatedAnnualDemand, AnnualEmissionLimit, AnnualExogenousEmission, AvailabilityFactor

    :param region:
    :param data:
    :return:
    """
    header = f'[{region},*,*]'
    df = data[data['REGION'] == region]
    df.drop('REGION', axis=1, inplace=True)
    content = ''
    for _, row in df.iterrows():
        if sum(row.values[1:]) > 0:
            content += f"{' '.join(str(e) for e in row.values)}\n"
    return header, content

def CatchBiVariateData(region, param_column, param_value, data):
    header = f'[{region},{param_value},*,*]'
    df = data[(data['REGION'] == region) & (data[param_column] == param_value)]
    df.drop(['REGION', param_column], axis=1, inplace=True)
    content = ''
    for _, row in df.iterrows():
        content += f"{' '.join(str(e) for e in row.values)}\n"
    return header, content

def CatchTriVariateData(region, param_column, param_value, param2_column, param2_value, data):
    header = f'[{region},{param_value},{param2_value},*,*]'
    df = data[(data['REGION'] == region) & (data[param_column] == param_value)& (data[param2_column] == param2_value)]
    df.drop(['REGION', param_column, param2_column], axis=1, inplace=True)
    content = ''
    for _, row in df.iterrows():
        content += f"{' '.join(str(e) for e in row.values)}\n"
    return header, content

def CapacityToActivityUnit(region, data):
    df = data[(data['REGION'] == region)]
    df.drop('REGION', axis=1, inplace=True)

    if len(df.columns) > 1:
        header = f"{' '.join(str(e) for e in df[df.columns[0]].values)} := \n"
        value = f"{region} {' '.join(str(e) for e in df[df.columns[1]].values)} \n"
        return header + value
    elif len(df.columns) == 1:
        value = f"{region} {' '.join(str(e) for e in df[df.columns[0]].values)} \n"
        return value
class SpreadSheetProcessing:
    def __init__(self, df, start_year=2015, end_year=2070, year_rate=1):
        self.df = df
        self.sets = self.create_set_block(df=self.df)
        self.base_years = list(range(start_year, end_year, year_rate))
        self.default_values = [0, 99999, 0, 1, 1, 0, 0, 0.0001, 1, 0.05, 0, 0, 0, 0, 99999, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                               0, 0, 0, 99999, 99999, 0, 0, 0, 99999, 0, 99999, 0, 0.0001, 0]
        self.parameters = self.create_default_param_dics(df=self.df, default_values=self.default_values)
        self.create_params_blocks(self.parameters, self.base_years)


    @staticmethod
    def create_default_param_dics(df, default_values):
        parameters = {}
        for par, default in zip(df['Parameter'].unique(), default_values):
            temp = df[df['Parameter'] == par].iloc[:, 1:]
            temp.dropna(axis=1, how='all', inplace=True)
            parameters[par] = {'data': temp, 'default_value': default}
        return parameters
    @staticmethod
    def create_set_block(df):
        sets = {
            'emission': [value for value in df['EMISSION'].unique() if type(value) != float],
            'region': [value for value in df['REGION'].unique() if type(value) != float],
            'mode_of_operation': [value for value in df['MODE_OF_OPERATION'].unique() if str(value) != 'nan'],
            'fuel': [value for value in df['FUEL'].unique() if type(value) != float],
            'storage': None,
            'technology': [value for value in df['TECHNOLOGY'].unique() if type(value) != float],
            'year': list(df.columns[10:]),
            'timeslice': [value for value in df['TIMESLICE'].unique() if type(value) != float],
        }
        set_str = ''
        for set in sets.keys():
            txt = ''
            try:
                for value in sets[set]:
                    txt += value + ' '
            except:
                pass
            txt += ';'
            set_str += f'set {set.upper()} := {txt}\n'

        mkdir_if_not_exists("etc/")
        with open("etc/sets_block.txt", 'w') as file:
            file.write(set_str)
            file.close()
        return sets
    @classmethod
    def create_params_blocks(self, parameters, years_range):
        param_str = ""

        for param in tqdm(parameters.keys(), total=len(parameters.keys())):
            param_data = parameters[param]['data']
            param_columns = param_data.columns
            pivot_columns = list(param_columns[:len(param_columns)-len(years_range)-1])
            ref_columns = list(param_columns[len(param_columns)-len(years_range)-1:])
            param_default_value = parameters[param]['default_value']
            txt_temp = f"param {param} default {param_default_value} := \n"
            parameters[param]['txt'] = txt_temp
            for region in param_data['REGION'].unique():
                if len(pivot_columns) == 2:
                    header, content = CatchUniVariateData(region, param_data)
                    parameters[param]['txt'] += f"{header}:\n"
                    parameters[param]['txt'] += f"{' '.join(ref_columns)}:=\n"
                    parameters[param]['txt'] += f"{content}"
                elif len(pivot_columns) == 3:
                    if 'MODE_OF_OPERATION' in pivot_columns:
                        pivot_columns.remove('MODE_OF_OPERATION')
                    if 'TIMESLICE' in pivot_columns:
                        pivot_columns.remove('TIMESLICE')
                    for value in param_data[pivot_columns[1]].unique():
                        header, content = CatchBiVariateData(region=region, param_column=pivot_columns[1], param_value=value, data=param_data)
                        parameters[param]['txt'] += f"{header}:\n"
                        parameters[param]['txt'] += f"{' '.join(ref_columns)}:=\n"
                        parameters[param]['txt'] += f"{content}\n"
                elif len(pivot_columns) == 4:
                    if 'MODE_OF_OPERATION' in pivot_columns:
                        pivot_columns.remove('MODE_OF_OPERATION')
                    if 'TIMESLICE' in pivot_columns:
                        pivot_columns.remove('TIMESLICE')
                    for value1 in param_data[pivot_columns[1]].unique():
                        for value2 in param_data[pivot_columns[2]].unique():
                            header, content = CatchTriVariateData(region=region, param_column=pivot_columns[1],
                                                                 param_value=value1, param2_column=pivot_columns[2],
                                                                 param2_value=value2, data=param_data)
                elif len(pivot_columns) < 2:
                    value = CapacityToActivityUnit(region=region, data=param_data)
                parameters[param]['txt'] += f";\n"
                with open(f'etc/{param}.txt', 'w') as file:
                    file.write(parameters[param]['txt'])
                    file.close()





    @staticmethod
    def return_data_by_ref(pivot:list, ref:list, data):
        pass


class OSeMOSYS(SpreadSheetProcessing):
    def __init__(self, args):
        self.args = args
        print(f'[*] - Loading parameters')
        self.original_df = pd.read_excel(self.args.db, sheet_name='Parameters')
        print(f'[!] - Parameters loaded successfully')
        super().__init__(df=self.original_df)


