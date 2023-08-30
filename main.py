import argparse
from src.osemosys.preprocessing import OSeMOSYS
from src.utils.functions import mergeParams, convertResultsToVisualization
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, default='db/Ecuador_FF_SAND.xlsm', help="Define the parameter spreadsheet")
    parser.add_argument("--change_regions", type=bool, default=True, help="Define new regions")
    parser.add_argument("--list_regions", type=list, default=['RE_N', 'RE_NE', 'RE_SE', 'RE_S'], help="Define new regions")
    parser.add_argument("--save_json", type=bool, default=False)

    args = parser.parse_args()

    osemosys = OSeMOSYS(args=args)
    # mergeParams(path='GlobalJuly/BrazAgo/Version1/', file_type='txt')
    # convertResultsToVisualization("GlobalJuly/BrazAgo/Version2/", file_type='csv')

if __name__ == "__main__":
    main()