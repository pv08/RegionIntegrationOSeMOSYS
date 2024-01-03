from typing import List
from src.utils.functions import mkdir_if_not_exists
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_variable_by_region(xlabel: str, ylabel: str, title: str, regions: List[str], variable: List[str],
                            variable_name: str, df: pd.DataFrame, img_title: str, img_types: List[str]=['.png', 'eps', '.svg']):
    mkdir_if_not_exists('etc/')
    mkdir_if_not_exists('etc/imgs/')
    data = {region: [] for region in regions}
    for region in regions:
        temp_data = []
        for tech in variable:
            temp = df.loc[(df['REGION'] == region) & (df[variable_name] == tech)]
            if not temp.empty:
                temp_data.append(sum(temp['VALUE']))
            else:
                temp_data.append(0)
        data[region] += temp_data

    bottom = np.zeros(len(variable))
    for region, values in data.items():
        plt.bar(variable, np.array(values), .75, label=region, bottom=bottom)
        bottom += np.array(values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.xticks(rotation=90)
    plt.legend()
    for ty in img_types:
        plt.savefig(f'etc/imgs/{img_title}{ty}')
    plt.show()
    plt.close()

def plot_region_grouped_by_year(img_title: str, ylabel: str, title: str, regions: List[str], years: List[str], df: pd.DataFrame, img_types: List[str]=['.png', 'eps', '.svg']):
    data = {region: [] for region in regions}
    for region in regions:
        temp_data = []
        for year in years:
            temp = df.loc[(df['YEAR'] == year) & (df['REGION'] == region)]
            temp_data.append(sum(temp['VALUE']))
        data[region] += temp_data
    bottom = np.zeros(len(years))
    for region, values in data.items():
        plt.bar(years, np.array(values), .75, label=region, bottom=bottom)
        bottom += np.array(values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel('Year')
    plt.xticks(rotation=90)
    plt.legend()
    for ty in img_types:
        plt.savefig(f'etc/imgs/{img_title}{ty}')
    plt.show()
    plt.close()

def plot_pie_participation_of_region(img_title: str, title: str, regions: List[str], df: pd.DataFrame, img_types: List[str]=['.png', 'eps', '.svg']):
    region_values = np.array([sum(df.loc[df['REGION'] == region]['VALUE']) for region in regions])
    plt.title(title)
    plt.pie(region_values, labels=regions, autopct='%1.1f%%')
    plt.legend()
    for ty in img_types:
        plt.savefig(f'etc/imgs/{img_title}{ty}')
    plt.show()
    plt.close()

