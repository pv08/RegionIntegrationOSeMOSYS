import argparse
from src.osemosys.preprocessing import OSeMOSYS
from src.utils.functions import mergeParams, convertResultsToVisualization
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, default='db/Ecuador_FF_SAND.xlsm', help="Define the parameter spreadsheet")

    args = parser.parse_args()

    # osemosys = OSeMOSYS(args=args)
    # mergeParams(path='GlobalJuly/BrazAgo/Version1/', file_type='txt')
    convertResultsToVisualization("GlobalJuly/BrazAgo/Version2/", file_type='csv')

if __name__ == "__main__":
    main()