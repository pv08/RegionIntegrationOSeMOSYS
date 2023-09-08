import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
def mkdir_if_not_exists(default_save_path: str):
    """
    Make directory if not exists by a folder path
    :param default_save_path: str() -> path to create the folder
    :return: None
    """

    if not os.path.exists(default_save_path):
        os.mkdir(default_save_path)


def saveHeatmap(x, y, data, save_path):
    plt.subplots(figsize=(15, 15))
    ax = sns.heatmap(data, linewidths=.5)
    ax.set_xticks(np.arange(len(x)), labels=x)

    ax.set_yticks(np.arange(len(y)), labels=y)
    plt.setp(ax.get_yticklabels(), rotation=90, ha="right",
             rotation_mode="anchor")
    plt.yticks(rotation=0)
    plt.savefig(f"{save_path}")
    plt.close()

def saveLinePlot(y_label, x_label, y_values, save_path):
    plt.figure(figsize=(15, 15))
    plt.plot(x_label, y_values)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.savefig(f"{save_path}")
    plt.close()
def mergeParams(path, file_type):
    str = ''
    for dir in os.listdir(path):
        files = glob.glob(f"{path}/{dir}/*.{file_type}", recursive=True)
        if len(files) != 0:
            for file in sorted(files):
                with open(file, 'r') as f:
                    str += f.read() + '\n'
                    f.close()
    with open(f'{path}/processed_file.txt', 'w') as f:
        f.write(str)
        f.close()


def convertResultsToVisualization(path, file_type):
    csvs = []
    for dir in os.listdir(path):
        files = glob.glob(f"{path}/{dir}/*.{file_type}", recursive=True)
        if len(files) != 0:
            for file in sorted(files):
                print(file)
                variable = file.split('/')[-1].replace('.csv', '')

                emission = []
                df = pd.read_csv(file)

                if 'TECHNOLOGY' in list(df.columns):
                    emission1 = df['TECHNOLOGY']
                if 'EMISSION' in list(df.columns):
                    emission2 = df['EMISSION']
                if 'FUEL' in list(df.columns):
                    emission3 = df['FUEL']
                for i in range(df.shape[0]):
                    dic = {
                        'Variable': variable,
                        'Dim1': df['REGION'].values[i],
                        'Dim2': emission.values[i],
                        'Dim3': df['YEAR'].values[i],
                        'Dim4': [],
                        'Dim5': [],
                        'Dim6': [],
                        'Dim7': [],
                        'Dim8': [],
                        'Dim9': [],
                        'Dim10': [],
                        'ResultValue': df['VALUE'].values[i]

                    }
                    csvs.append(dic)
    result = pd.DataFrame(csvs)
    result.to_csv('etc/results.csv', index=False)