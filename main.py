from bin.disposables import main_vars as mv
from bin.disposables import main_functions as mf
from bin.disposables import constructor as c
from bin.optimization import constrains as cons
from bin.optimization import p_func as p

import time

"""NOTES -> The gray imports must be made to load the variables from those modules into RAM"""

# ================================================================================================================
# EXECUTION VARIABLES
# ================================================================================================================

general_logger = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
z_func_logger = 3  # 1 = print // 2 = print + log // 3 = log // 0 = nothing

iterations = 5

# ================================================================================================================
# ISOLATED FUNCTION CALLS
# ================================================================================================================
mf.info()
# ================================================================================================================
# DEFINITIVE LOOP WORKFLOW
# ================================================================================================================
'''
NOTES

1. Z_func inherits the following variables, which can be manually altered:
    . Logger 
    · Current iteration number
    · Total number of iterations
    · Psi1, phi, chi, psi2, delta, omega [ 1 = Activate p_func // 0 = Deactivate p_func ]
'''

start_time = time.time()  # The timer starts after the database setup

mf.create_readable_files()

for i in range(iterations):
    print(f"\n///// ITERATION {i+1}\n///// STARTING CONSTRUCTOR")
    c.main(general_logger, i + 1)
    print("///// CONSTRUCTOR FINISHED")
    mf.unsuitable_workers_cleaner()
    mf.z_func(z_func_logger, i+1, iterations, 1, 1, 1, 1, 1, 1)
    mf.clearer()

mf.Logger(general_logger, "\nEXECUTION TIME -> --- %s seconds ---" % (time.time() - start_time), 'results')
