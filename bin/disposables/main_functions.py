from Data.DB.db_py.Employees import employees as em
from Data.DB.db_py.Enclaves import enclaves as en
from Data.DB.db_py.Demand import demand_raw as dr

from Data.Assignation import data
from bin.optimization import p_func as p
from bin.disposables import main_vars as mv

import random


# ================================================================================================================
# GENERAL FUNCTIONS
# ================================================================================================================

def info():
    print(f"ENCLAVES ({len(mv.enclaves)}) // -> {mv.enclaves}")
    print(f"WORKERS ({len(mv.workers)}) // -> {mv.workers}")
    print(f"COACHES ({len(mv.coaches)}) // -> {mv.coaches}")
    print(f"PLANTILLA ({len(mv.plantilla)}) // -> {mv.plantilla}\n")


def randomize_worker(opt, logger):
    if opt == 1:  # Worker Randomizer
        Logger(logger, f"##### ASSIGNED LEN -> {len(mv.assigned)} // TOTAL WC LEN -> {len(mv.work_coach)} // ASIGNED -> {mv.assigned}", 'log')
        while True:
            index = random.randint(0, len(mv.work_coach)-1)
            e = mv.work_coach[index]
            if e not in mv.assigned:
                mv.assigned.append(e)
                return index

    elif opt == 2:  # Clear Assigned Workers List at the end of the day
        mv.assigned.clear()

    elif type(opt) == list:  # When we pass a list, it means that the ratio has not been met, and we remove the workers from this list from the assigned list.
        for i in range(len(opt)):
            mv.assigned.remove(opt[i])
        Logger(logger, f"//// RATIO NOT FULFILLED!!! -> RENEWED ASSING LEN -> {len(mv.assigned)} // TOTAL WC LEN -> {len(mv.work_coach)}", 'log')


def writer():
    x = list(data.__dict__.items())

    with open("Data/Assignation/data2.py", "w") as r:
        r.write("")
        for i in range(len(x)):
            if type(x[i]) == tuple and str(x[i][0]).startswith('day_'):
                if type(x[i]) == tuple and str(x[i][0]).startswith('day_3'):
                    print(x[i])
                r.write(f"\n{x[i][0]} = {'{'}")
                for key in x[i][1]:
                    r.write(f"\n    '{key}': {x[i][1][key]},")
                r.write("\n     }")


class Logger:  # 1 = print // 2 = print + log // 3 = log // 0 = nothing

    def __init__(self, opt, msg, title):
        if opt == 1:  # Print
            self.print(msg)
        elif opt == 2:  # Print + Log
            self.print(msg)
            self.write_log(msg, title)
        elif opt == 3:  # Log
            self.write_log(msg, title)
        elif opt == 0:  # Nothing
            pass

    @staticmethod
    def print(msg):
        print(msg)

    @staticmethod
    def write_log(msg, title):
        with open(f"Data/Logs/{title}.txt", "a", encoding="UTF-8") as f:
            f.write(f"{msg}\n")


def get_unassigned_list():  # Returns Unassigned Workers List
    unassigned = []
    for e in range(len(mv.work_coach)):
        if mv.work_coach[e] not in mv.assigned:
            unassigned.append(mv.work_coach[e])

    return unassigned


def create_readable_files():
    opt = ['log.txt', 'results.txt', 'p_func_log.txt']
    for i in range(len(opt)):
        with open(f"Data/Logs/{opt[i]}", "w", encoding="UTF-8") as f:
            f.write("")


def clearer():
    for i in range(mv.days):
        getattr(data, f"day_{i + 1}")["descanso_forzado"].clear()
        for j in range(len(mv.enclaves)):
            getattr(data, f"day_{i + 1}")[mv.enclaves[j]].clear()


def unsuitable_workers_cleaner():
    enclave = ""
    for t in range(mv.days):
        for e in range(len(mv.work_coach)):
            for j in range(len(mv.enclaves)):
                if mv.work_coach[e] in getattr(data, f"day_{t + 1}")[mv.enclaves[j]]:
                    enclave = mv.enclaves[j]
                    break
            if enclave == "" or mv.work_coach[e] not in getattr(data, f"day_{t + 1}")["descanso_forzado"]:
                getattr(data, f"day_{t + 1}")["descanso_forzado"].append(mv.work_coach[e])


# ================================================================================================================
# CHECKERS
# ================================================================================================================


def check_users_left():
    workers, coaches = 0, 0
    for i in range(len(mv.workers)):
        if mv.workers[i] not in mv.assigned:
            workers += 1
    for i in range(len(mv.coaches)):
        if mv.coaches[i] not in mv.assigned:
            coaches += 1

    return [workers, coaches]


def afinity_checker(tipe, source, opt1, opt2):
""" WJ -> opt2 must always be the location // WW -> opt2 must always be the worker WITH WHOM 
the affinity is to be checked, with opt1 being the main one // WC -> opt2 must always be the coach"""

    x = list(source.__dict__.items())
    afinities = {'-': 1, 'A': 1, 'B': 1, 'X': 0}

    for i in range(len(x)):
        if x[i][0] == opt1:
            if tipe == "WJ":  # PHI sub W, sub J
                id_index = mv.enclaves.index(opt2)
                phi = afinities[x[i][1][id_index]]
                return phi
            elif tipe == "WW":  # PSI sub w1, sub w2
                id_index = mv.plantilla.index(opt2)
                psi = afinities[x[i][1][id_index]]
                return psi
            elif tipe == "WC":  # CHI sub w, sub c
                id_index = mv.plantilla.index(opt2)
                chi = afinities[x[i][1][id_index]]
                return chi


def demand_checker(enclave):
    x = list(dr.__dict__.items())
    for i in range(len(x)):
        if x[i][0] == enclave:
            return x[i][1]


def total_demand_checker(t, posicion_referida):
    total_demand = 0
    for j in range(len(mv.enclaves)):
        total_demand += int(demand_checker(mv.enclaves[j])[t + posicion_referida])

    return total_demand


def unassigned_worker_checker(lista):
    unassigned = 0
    for i in range(len(lista)):
        if lista[i] not in mv.assigned:
            unassigned += 1

    return unassigned


def fullfilled_demand_checker(day):
    DELTA_jt = 0
    for j in range(len(mv.enclaves)):
        DELTA_jt += len(day[mv.enclaves[j]])

    return DELTA_jt


def A_ejt(e, j, t):
    if e in getattr(data, f"day_{t+1}")[j]:
        return 0  # Return 0 because this location would not be available, as it is already assigned
    else:
        return 1  # If it is not assigned to this location, then it is available


def B_ejt(e, j, t, referred_position):
    demand = int(demand_checker(j)[t + referred_position])

    if e not in getattr(data, f"day_{t+1}")[j] and len(getattr(data, f"day_{t+1}")) < demand:
        return 1  # J is available for E at T since E has not been assigned to J, and the group is not full
    else:
        return 0  # Cannot associate because it is already associated and/or the group is full


def worker_coach_checker(lista):
    results = [0, 0]  # coaches , workers

    for i in range(len(lista)):
        if getattr(em, f"worker_{mv.plantilla.index(lista[i])}")["role"] == "0":
            results[1] += 1
        elif getattr(em, f"worker_{mv.plantilla.index(lista[i])}")["role"] == "1":
            results[0] += 1

    return results


def H_j(e, t):  # Calculates the total hours worked by E over a period of 7 days
    H_j = 0

    if t > 6:
        t = 6
    elif t <= 6:
        t = 1

    for i in range(8):
        for j in range(len(mv.enclaves)):
            if e in getattr(data, f"day_{t+i}")[mv.enclaves[j]]:
                H_j += getattr(en, f"enclave_{mv.enclaves.index(mv.enclaves[j])}")["demanda_h"]

    return H_j


# ================================================================================================================
# OBJECTIVE FUNCTION
# ================================================================================================================


def z_func(logger, index, vueltas, a, b, c, d, e, f):

    PSI1, PHI, CHI, PSI2, DE, OMEGA = p.p_psi_1(a), p.p_phi(b), p.p_chi(c), p.p_psi_2(d), p.p_de(e), p.p_omega(f)
    z = PSI1 + PHI + CHI + PSI2 + DE - OMEGA

    mv.values.append([index, PSI1, PHI, CHI, PSI2, DE, OMEGA])
    mv.z_values.append(z)

    if index == 1:
        Logger(logger, f'''\n=============================================================================================
     VUELTA       PSI1      PHI     CHI     PSI2       DELTA       OMEGA       Z
=============================================================================================
       {index}          {PSI1}       {PHI}     {CHI}     {PSI2}       {DE}       {OMEGA}       {z}''', 'results')
    if index > 1 and index < 10:
        Logger(logger, f"       {index}          {PSI1}       {PHI}     {CHI}     {PSI2}       {DE}       {OMEGA}       {z}", 'results')

    if index >= 10 and index not in range(9):
        Logger(logger, f"       {index}         {PSI1}       {PHI}     {CHI}     {PSI2}       {DE}       {OMEGA}       {z}", 'results')

    if index == vueltas:
        Logger(logger, f"=============================================================================================", 'results')
        max_z = mv.z_values.index(max(mv.z_values))
        print(f"VALOR MAXIMO = {max(mv.z_values)}")
        Logger(logger, f"""\n=============================================================================================
|||                             OPTIMIZED MAXIMUM VALUE                                   |||
=============================================================================================
     VUELTA       PSI1      PHI     CHI     PSI2       DELTA       OMEGA       Z
=============================================================================================
       {mv.values[max_z][0]}          {mv.values[max_z][1]}       {mv.values[max_z][2]}     {mv.values[max_z][3]}     {mv.values[max_z][4]}       {mv.values[max_z][5]}       {mv.values[max_z][6]}       {mv.z_values[max_z]}
=============================================================================================""", 'results')
