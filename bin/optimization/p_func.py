from Data.DB.db_py.Enclaves import enclaves as en
from Data.DB.db_py.Employees import afin_emp as ap
from Data.DB.db_py.Enclaves import afin_encl as ae

from bin.disposables import main_vars as mv
from bin.disposables import main_functions as mf

from bin.optimization import constrains as cons

from Data.Assignation import data
# ================================================================================================================
# P FUNCTIONS
# ================================================================================================================


def p_psi_1(opt):  # 1st Function -> Calculates the total number of rests
    if opt != 0:
        logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
        chi_et = 0
        counter = 0
        for e in range(len(mv.work_coach)):
            for t in range(mv.days):
                if mv.work_coach[e] in getattr(data, f"day_{t+1}")["forced_rest"]:
                    counter += 1
            mf.Logger(logger2, f"Total rests of {mv.work_coach[e]} -> {counter}", 'p_func_log')
            chi_et += int(counter)
            counter = 0
        mf.Logger(logger2, f"\nTotal Rests = {chi_et}", 'p_func_log')

        return chi_et
    else:
        return 0


def p_phi(opt):  # 2nd Function P in the list. Checks if there is affinity between worker and location in t
    if opt != 0:
        phi_wj = 0
        counter = 0
        logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
        for t in range(mv.days):  # For each day of the week
            for w in range(len(mv.workers)):  # For each worker
                for j in range(len(mv.enclaves)):  # For each location
                    if mv.workers[w] in getattr(data, f"day_{t+1}")[mv.enclaves[j]]:
                        delta_wjt = mv.workers[w]
                        counter2 = mf.afinity_checker("WJ", ae, delta_wjt, mv.enclaves[j])
                        mf.Logger(logger2, f"WORKER ({mv.workers[w]}) // LOCATION ({mv.enclaves[j]}) // DAY ({t+1}) // AFFINITY -> {counter2}", 'p_func_log')
                        phi_wj += (counter2 * 1)   # Multiply by 1 because if delta_wjt has a str value it means it has been assigned, hence 1
                        counter += 1

        mf.Logger(logger2, f"\nTOTAL WJ AFFINITIES = {phi_wj}", 'p_func_log')
        mf.Logger(logger2, f"TOTAL OPERATIONS PERFORMED = {counter}", 'p_func_log')
        return phi_wj
    else:
        return 0


def p_chi(opt):  # 3rd Function -> Calculates if a WC pair assigned to J in T is affine.
    if opt != 0:
        chi_cw = 0
        counter = 0
        logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
        for t in range(mv.days):
            for c in range(len(mv.coaches)):
                for w in range(len(mv.workers)):
                    for j in range(len(mv.enclaves)):
                        if mv.coaches[c] in getattr(data, f"day_{t+1}")[mv.enclaves[j]] and mv.workers[w] in getattr(data, f"day_{t+1}")[mv.enclaves[j]]:
                            epsilon_cwjt = 1  # Epsilon is 1 because if we reach this point, both workers must have been assigned to J in T
                            counter2 = mf.afinity_checker("WC", ap, mv.workers[w], mv.coaches[c])
                            chi_cw += (counter2 * epsilon_cwjt)
                            counter += 1
                            mf.Logger(logger2, f"COACH ({mv.coaches[c]}) // WORKER ({mv.workers[w]}) // LOCATION ({mv.enclaves[j]}) // DAY ({t+1}) // AFFINITY -> {counter2}", 'p_func_log')

        mf.Logger(logger2, f"\nTOTAL WC AFFINITIES = {chi_cw}", 'p_func_log')
        mf.Logger(logger2, f"TOTAL OPERATIONS PERFORMED = {counter}", 'p_func_log')
        return chi_cw
    else:
        return 0


def p_psi_2(opt):  # 4th Function -> Calculates the affinities of one Worker with another Worker
    if opt != 0:
        psi_w1 w2 = 0
        counter = 0
        logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
        for t in range(mv.days):
            for w1 in range(len(mv.workers)):
                for w2 in range(len(mv.workers)):
                    for j in range(len(mv.enclaves)):
                        if mv.workers[w1] != mv.workers[w2] and mv.workers[w1] in getattr(data, f"day_{t+1}")[mv.enclaves[j]] and mv.workers[w2] in getattr(data, f"day_{t+1}")[mv.enclaves[j]]:
                            epsilon_e1e2jt = 1  # Epsilon is 1 because if we reach this point, both workers must have been assigned to J in T
                            counter2 = mf.afinity_checker("WW", ap, mv.workers[w2], mv.workers[w1])
                            psi_w1w2 += (counter2 * epsilon_e1e2jt)
                            counter += 1
                            mf.Logger(logger2, f"WORKER [1] ({mv.workers[w1]}) // WORKER [2] ({mv.workers[w2]}) // LOCATION {mv.enclaves[j]} // DAY ({t+1}) // AFFINITY -> {counter2}", 'p_func_log')

        mf.Logger(logger2, f"\nTOTAL WW AFFINITIES = {psi_w1w2}", 'p_func_log')
        mf.Logger(logger2, f"TOTAL OPERATIONS PERFORMED = {counter}", 'p_func_log')
        return psi_w1w2
    else:
        return 0


def p_de(opt):  # 5th Function -> Calculates if the total hours worked meet or exceed the total demand in hours
    if opt != 0:
        p_de_data = 0
        logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing
        for t in range(mv.days):
            for j in range(len(mv.enclaves)):
                delta_ejt = 0
                for e in range(len(mv.work_coach)):
                    if mv.work_coach[e] in getattr(data, f"day_{t + 1}")[mv.enclaves[j]]:
                        delta_ejt += 1  # Equals 1 because worker E is assigned to J in T

                D_jt = int(mf.demand_checker(mv.enclaves[j])[t + 4])  # Check demand in workers
                H_j = getattr(en, f"enclave_{mv.enclaves.index(mv.enclaves[j])}")["demand_h"]  # Demand in hours
                p_de_data += (H_j * delta_ejt) - (H_j * D_jt)

                mf.Logger(logger2, f"WORKERS ({delta_ejt}) // LOCATION ({mv.enclaves[j]}) // DAY ({t+1}) // DEMAND HOURS ({H_j}) // DEMAND LOCATION ({D_jt})", 'p_func_log')
                mf.Logger(logger2, f"H_j ({H_j}) * {delta_ejt} - H_j ({H_j}) * D_jt ({D_jt}) = {(H_j * delta_ejt) - (H_j * D_jt)}", 'p_func_log')

        mf.Logger(logger2, f"\nTHE TOTAL VALUE OF DEMAND GIVEN MINUS REQUIRED DEMAND IS = {p_de_data}", 'p_func_log')
        return p_de_data
    else:
        return 0


def p_omega(opt):  # 6th Function -> Counts how many times a worker is assigned to J and the next day to another J
    if opt != 0:
        logger2 = 0
        omega_et = 0
        for t in range(mv.days):
            for e in range(len(mv.work_coach)):
                omega_et += cons.r08(mv.work_coach[e], t)

        mf.Logger(logger2, f"\nTOTAL NUMBER OF TIMES A WORKER HAS BEEN ASSIGNED TO A DIFFERENT LOCATION -> {omega_et}", 'p_func_log')
        return omega_et
    else:
        return 0
