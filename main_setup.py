from bin.disposables import setup_db as setup

'''
Run this script only once to generate the database that the program will read to create the database
from the information in the Excel file. This should only be executed if we do not have the data dumped in Python format.
'''

path = 'Data/Excel/Excel.xlsx'

setup.reset()
setup.start_setup(path)

from bin.disposables import main_vars as mv


def create_db_raw(file):
    with open(file, "w", encoding="UTF-8") as f:
        f.write("")
        for t in range(mv.days):
            f.write(f"day_{t+1} = {{")
            for j in range(len(mv.enclaves)):
                f.write(f"\n    '{mv.enclaves[j]}': [],")
            f.write(f"\n    'forced_rest': [],")
            f.write("\n     }\n\n")


create_db_raw("Data/Assignation/data.py")
create_db_raw("Data/Assignation/data2.py")
