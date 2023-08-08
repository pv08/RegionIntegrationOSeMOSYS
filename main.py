import argparse
from src.osemosys.preprocessing import OSeMOSYS
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, default='db/Ecuador_FF_SAND.xlsm', help="Define the parameter spreadsheet")

    args = parser.parse_args()

    osemosys = OSeMOSYS(args=args)

if __name__ == "__main__":
    main()