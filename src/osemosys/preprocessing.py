import pandas as pd
import json
import numpy as np
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
    def __init__(self, df, args, start_year=2015, end_year=2070, year_rate=1):
        self.df = df
        self.args = args
        self.base_years = list(range(start_year, end_year, year_rate))
        self.sets = {
            'EMISSION': [],
            'REGION': self.args.list_regions,
            'MODE_OF_OPERATION': [],
            'FUEL': [],
            'STORAGE': None,
            'TECHNOLOGY': [],
            'YEAR': self.base_years,
            'TIMESLICE': [],
        }

        self.default_values = [0, 99999, 0, 1, 1, 0, 0, 0.0001, 1, 0.05, 0, 0, 0, 0, 99999, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                               0, 0, 0, 99999, 99999, 0, 0, 0, 99999, 0, 99999, 0, 0.0001, 0]

        self.preprocess()
        self.create_set_block()

        self.parameters = self.create_default_param_dics(df=self.df, default_values=self.default_values)
        self.create_params_blocks(self.parameters, self.base_years)


    def preprocess(self):
        self.parameter = {}
        value_default = list(zip(self.df['Parameter'].unique(), self.default_values))
        for param, default_value in tqdm(value_default, total=len(self.df['Parameter'].unique())):
            param_selection = self.df[self.df['Parameter'] == param]
            param_selection.dropna(axis=1, how='all', inplace=True)
            if self.args.change_regions:
                self.parameter[param] = []
                for region in self.args.list_regions:
                    region_df = param_selection.copy()
                    region_df.replace('RE1', region, inplace=True)
                    for col in region_df.columns[2: -1-len(self.base_years)]:
                        if col in ['TECHNOLOGY', 'EMISSION', 'FUEL']:
                            region_df[col] = region_df[col].astype(str) + f"_{region}"
                    self.parameter[param] += json.loads(region_df.to_json(orient='records'))

            else:
                self.parameter[param] = json.loads(param_selection.to_json(orient='records'))
        # TODO: {Ver a lógica para colocar as tecnologias de conexão e limitação de distribuição e transmissão}

        mkdir_if_not_exists('etc/')
        mkdir_if_not_exists('etc/logs')
        if self.args.save_json:
            with open(f'etc/logs/parameters.json', "w") as outfile:
                json.dump(self.parameter, outfile)
        self.df_updated = []
        for param, def_value in zip(self.parameter.keys(), self.default_values):
            temp = pd.DataFrame(self.parameter[param])
            temp = temp.replace(def_value, np.nan)
            temp.dropna(axis=0, how='any', inplace=True)
            set_columns = temp.columns[1: -1-len(self.base_years)]
            for col in set_columns:
                for value in temp[col].unique():
                    if value not in self.sets[col]:
                        self.sets[col].append(value)
            temp.to_csv(f'etc/logs/{param}.csv', index=False)
            self.df_updated += self.parameter[param]
        self.df_updated = pd.DataFrame(self.df_updated)
        self.df_updated.to_csv(f'db/file_updated.csv', index=False)


    @staticmethod
    def create_default_param_dics(df, default_values):
        parameters = {}
        for par, default in zip(df['Parameter'].unique(), default_values):
            temp = df[df['Parameter'] == par].iloc[:, 1:]
            temp.dropna(axis=1, how='all', inplace=True)
            parameters[par] = {'data': temp, 'default_value': default}
        return parameters

    def create_set_block(self):
        set_str = ''
        for set in self.sets.keys():
            txt = ''
            try:
                for value in self.sets[set]:
                    txt += value + ' '
            except:
                pass
            txt += ';'
            set_str += f'set {set.upper()} := {txt}\n'

        mkdir_if_not_exists("etc/")
        with open("etc/sets_block.txt", 'w') as file:
            file.write(set_str)
            file.close()
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
        super().__init__(df=self.original_df, args=args)


