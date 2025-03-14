from Data.DB.db_py.Enclaves import enclaves as en
from Data.DB.db_py.Employees import afin_emp as ap

from bin.disposables import main_vars as mv
from bin.disposables import main_functions as mf

from Data.Assignation import data
# from Data.Assignation import data2

import math

# ================================================================================================================
# LOCAL VARS
# ================================================================================================================

days_counter = 0
days9_passed = bool(False)

# ================================================================================================================
# RESTRICTIONS - CONSTRAINTS
# ================================================================================================================


def r00(e, t):  # Check if the worker has been assigned to any location
    for j in range(len(mv.enclaves)):
        if e in getattr(data, f"day_{t+1}")[mv.enclaves[j]]:
            return 1  # Delta
    return 0


def r01(e, t):  # Ensures that every 9 days the worker has 1 rest day
    global days9_passed, days_counter

    if t+1 % 9 == 0 or days9_passed:  # Here we ensure that 9 days have passed
        days9_passed = bool(True)  # This allows us to always call this function after 9 days have passed
        chi_et = 0
        days_counter += 1  # Increase the counter value each time we call it, to increment the starting day by 1
        for i in range(t+1):
            if e in getattr(data, f"day_{days_counter+i}")["forced_rest"]:  # previously it was data2
                chi_et += 1  # Add 1 each time the worker has had a rest in a 9-day period
        if chi_et >= 2:
            return 1  # If the number of rests is 2 or more, return 1
        else:
            return 0  # Otherwise return 0, and that worker will rest that day

    else:
        return 1  # Return 1 even if they haven't rested in 9 days because 9 days have not yet passed


def r02(e, t):  # Checks that the worker does not exceed 5 working days per week
    delta_ejt = 0
    t_index = 0
    if t >= 7:
        t_index = 7
    for t in range(7):
        delta_ejt += r00(e, (t_index+t))
    if delta_ejt >= 5:
        return 1  # Returns 1 if they have worked 5 days or more and that day rests
    else:
        return 0  # Returns 0 if it is met and the worker can work


def r03(j, t, referred_position):  # Checks if the demand of location J on day T has been met
    delta_ejt = len(getattr(data, f"day_{t+1}")[j])  # The size of the list is the total number of workers associated with that j on that T
    D_jt = int(mf.demand_checker(j)[t+referred_position])

    if delta_ejt >= D_jt:
        return 1  # The demand has been met
    else:
        return 0  # The demand has not been met


def r04(j, t, referred_position, logger):  # Checks if the ratio is met
    delta_ejt = mf.worker_coach_checker(getattr(data, f"day_{t + 1}")[j])[1]  # Number of workers
    delta_cjt = mf.worker_coach_checker(getattr(data, f"day_{t + 1}")[j])[0]  # Number of coaches
    gamma_jt = getattr(en, f"enclave_{mv.enclaves.index(j)}")["ratio"]  # Ratio
    D_jt = int(mf.demand_checker(j)[t + referred_position])  # Demand

    mf.Logger(logger, f"##### [R06] -> RATIO ({gamma_jt}) || DEMAND ({D_jt}) || WORKERS ({delta_ejt}) || COACHES ({delta_cjt})", 'log')

    try:
        A = math.trunc(((D_jt/gamma_jt)/delta_cjt))  # (Demand / Ratio) / Coaches
        B = math.trunc((D_jt/(delta_ejt + delta_cjt)))  # Demand / (workers + coaches)
        C = math.trunc(((delta_ejt + delta_cjt)/D_jt))  # (workers + coaches) / demand
        mf.Logger(logger, f"##### RATIO || A ({A}) ||| B ({B}) ||| C ({C})", 'log')

        if A * B * C == 1:
            return 1
        else:
            return 0

    except ZeroDivisionError:
        return 0


def r05(e, j, t): # Checks if there is affinity between 1 worker and the immediately previous one
    try:
        d1_ejt = getattr(data, f"day_{t+1}")[j][len(getattr(data, f"day_{t+1}")[j])-1]  # Immediately previous worker
        d2_ejt = e

        Ie1e2 = mf.afinity_checker("WW", ap, d2_ejt, d1_ejt)

        if Ie1e2 == 1:  # This line can be summarized in a return Ie1e2
            return 1
        else:
            return 0

    except IndexError:
        return 1


def r06(e, t, logger):  # Check that every 7 days, the hours worked do not exceed the legal maximum
    if (t+1) % 7 == 0:  # Check if we have called it after 7 days have passed
        H_e = 50
        H_j = mf.H_j(e, t)
        mf.Logger(logger, f"##### [R06] -> WORKER {e} HAS WORKED THIS WEEK -> {H_j}", 'log')
        if 1 * H_j <= H_e:  # Forcing delta to 1 here because this way we check if it can be assigned or not
            return 0  # Return 0 if the hours worked exceed the maximum to force a rest
        else:
            return 1

    else:  # Return 0 if 7 days have not passed
        return 0


def r07(delta_ejt, e, j, t, referred_position):  # Check if worker e can be assigned to location J based on availability
    A_ejt = mf.A_ejt(e, j, t)  # Check if E is available for J at T (Always by default)
    B_ej = mf.B_ejt(e, j, t, referred_position)  # Check if J is available for E at T (Redundant)

    if delta_ejt <= A_ejt * B_ej:
        return 1
    else:
        return 0


def r08(e, t):  # Calculates if E has been assigned to different J on t and t+1
    delta_ej1t, delta_ej2t1 = 0, 0
    enclave = ""
    logger2 = 0  # 1 = print // 2 = print + log // 3 = log // 0 = nothing

    if t != 14:  # This prevents calculating changes on the last day with a supposed next non-existent day

        for j in range(len(mv.enclaves)):  # Check where the worker has been associated
            if e in getattr(data, f"day_{t + 1}")[mv.enclaves[j]]:
                delta_ej1t = 1
                enclave = mv.enclaves[j]
                break
        if enclave == "" and e in getattr(data, f"day_{t + 1}")["forced_rest"]:
            enclave = "forced_rest"

        mf.Logger(logger2, f"WORKER ({e}) /// LOCATION ({enclave}) /// DAY ({t + 1})", 'p_func_log')

        if e not in getattr(data, f"day_{t+2}")[enclave]:  # Check if the next day they were assigned to another place
            delta_ej2t1 = 1

        if delta_ej1t + delta_ej2t1 == 1:
            return 0  # This means there has been no change
        else:
            mf.Logger(logger2, f"WORKER ({e}) // OMEGA -> 1", 'p_func_log')
            return 1  # This means there has been a change

    else:
        return 0  # Return 0 if it is the last day of the period to avoid counting false data


def r09(j, t, referred_position, logger):  # Check that, in case the ratio is 0, there are no coaches
    delta_cjt = mf.worker_coach_checker(getattr(data, f"day_{t + 1}")[j])[0]  # Number of coaches
    gamma_jt = getattr(en, f"enclave_{mv.enclaves.index(j)}")["ratio"]  # Ratio
    D_jt = int(mf.demand_checker(j)[t + referred_position])  # Demand

    mf.Logger(logger, f"##### [R13] -> RATIO ({gamma_jt}) || DEMAND ({D_jt}) || COACHES ({delta_cjt})", 'log')

    if (D_jt*gamma_jt) + delta_cjt == 0:
        return 1  # If the demand is > 0 but the ratio is 0, there are no coaches
    else:
        return 0  # Returns 0 if any of the previous elements are not met


def r10(j, t, referred_position, logger):  # Calculates if the ratio is greater than the demand, to ensure that of all the associates, one is a coach
    delta_ejt = mf.worker_coach_checker(getattr(data, f"day_{t + 1}")[j])[1]  # Number of workers
    delta_cjt = mf.worker_coach_checker(getattr(data, f"day_{t + 1}")[j])[0]  # Number of coaches
    gamma_jt = getattr(en, f"enclave_{mv.enclaves.index(j)}")["ratio"]  # Ratio
    D_jt = int(mf.demand_checker(j)[t + referred_position])  # Demand

    mf.Logger(logger, f"##### [R06] -> RATIO ({gamma_jt}) || DEMAND ({D_jt}) || WORKERS ({delta_ejt}) || COACHES ({delta_cjt})", 'log')

    try:
        A = math.trunc(D_jt/gamma_jt)
        B = (D_jt - 1) / delta_ejt

        if A + (B / 1) == 1:
            return 1  # This indicates that the ratio is greater than the demand and that there is 1 coach for the current workers
        else:
            return 0

    except ZeroDivisionError:
        return 0  # This in case the ratio is 0


def r11(t, referred_position):  # Calculates if the demand has not yet been met and only coaches remain to associate with the group
    D_t = mf.total_demand_checker(t, referred_position)
    alpha_wt = mf.unassigned_worker_checker(mv.workers)

    if D_t * alpha_wt == 0:
        return 1  # Return 1 if we confirm that we have no available workers left to assign
    else:
        return 0  # Return 0 if there are still workers


def r12(t, referred_position):  # Calculates if the demand has exceeded the supply of workers, to indicate that the group should be filled with nulls
    D_t = mf.total_demand_checker(t, referred_position)
    alpha_wt = mf.unassigned_worker_checker(mv.workers)
    alpha_ct = mf.unassigned_worker_checker(mv.coaches)

    if D_t * (alpha_wt + alpha_ct) == 0:
        return 1  # Return 1 if we confirm that no one is available to assign
    else:
        return 0  # Return 0 if there is still someone to assign


def r13(t, referred_position):  # Checks if there are unassigned workers, and if so, returns 1 to put them on forced rest
    DELTA_jt = mf.fullfilled_demand_checker(getattr(data, f"day_{t + 1}"))  # Total Demand Met for each J in T
    D_t = mf.total_demand_checker(t, referred_position)
    alpha_wt = mf.unassigned_worker_checker(mv.workers)
    alpha_ct = mf.unassigned_worker_checker(mv.coaches)
    alpha_et = alpha_wt + alpha_ct

    if D_t > 0:  # If the demand is greater than 0
        if math.trunc(DELTA_jt/D_t) * alpha_et == 0:  # Return 1 when the demand is not met and/or there are loose workers
            return 1
        else:  # Return 0 if we find that there are unassigned workers
            return 0

    elif D_t <= 0:  # In case the demand is 0
        '''It is possible that on some days there is no demand. In that case, DELTA_jt and D_t will always be 0, which will 
        trigger this error. In that case, it would be considered that all workers have the day off and therefore all must go to forced rest'''
        return 0
