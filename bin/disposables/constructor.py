from bin.disposables import main_vars as mv
from bin.disposables import main_functions as mf
from bin.optimization import constrains as cons
from Data.Assignation import data

referred_position = 0  # This is used to change the starting point of the demand.


class CreateGroups:

    overflow = bool(False)
    party = []

    def __init__(self, logger, iteration):
        self.logger = logger
        for t in range(mv.days):
            for j in range(len(mv.enclaves)):
                while True:
                    for e in range(len(mv.work_coach)):
                        users = mf.check_users_left()
                        delta_ejt = cons.r03(mv.enclaves[j], t, referred_position)
                        mf.Logger(self.logger, f"///// WORKERS [{users[0]}] || COACHES [{users[1]}]", 'log')
                        mf.Logger(self.logger, f"///////////// -> NEW ITERATION [{iteration}]", 'log')
                        mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW A.1.1 // DELTA -> {delta_ejt} // R03 // 1 = Demand Met", 'log')
                        if delta_ejt == 0:  # DATAFLOW A.1.1
                            delta_ejt = cons.r12(t, referred_position)
                            mf.Logger(self.logger, f"// R12 // DEMAND EXCEEDS SUPPLY - ADDING NULLS", 'log')
                            if delta_ejt == 0:  # BREAKPOINT
                                e = mf.randomize_worker(1, self.logger)
                                delta_ejt = cons.r02(mv.work_coach[e], t)  # 0 to IF
                                mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW A.1.2 // DELTA -> {delta_ejt} // R02 // 1 = Worker has worked +5 days", 'log')
                                if delta_ejt == 0:  # DATAFLOW A.1.2
                                    delta_ejt = cons.r01(mv.work_coach[e], t)
                                    mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW D.1.1 // DELTA -> {delta_ejt} // R01 // 1 = Worker has had 2 breaks in 9 days / 9 days have not passed", 'log')
                                    if delta_ejt == 1:  # INCURSION2 D.1.1
                                        delta_ejt = cons.r06(mv.work_coach[e], t, self.logger)  # 0 to IF
                                        mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW C.1.1 // DELTA -> {delta_ejt} // R06 // 1 = Worker has worked the maximum allowed hours in 7 days", 'log')
                                        if delta_ejt == 0:  # INCURSION C.1.1
                                            delta_ejt = cons.r00(mv.work_coach[e], t)  # 0 to IF
                                            mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t})// DATAFLOW A.1.3 // DELTA -> {delta_ejt} // R00 // 1 = Assigned Worker", 'log')
                                            if delta_ejt == 0:  # DATAFLOW A.1.3
                                                delta_ejt = cons.r07(delta_ejt, mv.work_coach[e], mv.enclaves[j], t, referred_position)  # 1 to IF
                                                mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW A.1.4 // DELTA -> {delta_ejt} // R07 // 1 = Location Availability", 'log')
                                                if delta_ejt == 1:  # DATAFLOW A.1.5
                                                    delta_ejt = cons.r05(mv.work_coach[e], mv.enclaves[j], t)
                                                    mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // DATAFLOW A.1.5 // DELTA -> {delta_ejt} // R05 // 1 = WW Affinity", 'log')
                                                    if delta_ejt == 1:  # DATAFLOW A.1.6
                                                        # This only occurs if the worker has passed all filters
                                                        self.party.append(mv.work_coach[e])
                                                        getattr(data, f"day_{t + 1}")[mv.enclaves[j]] = list(self.party)  # We save the party in J at T
                                                        mf.Logger(self.logger, f"##### PARTY SO FAR -> {self.party}", 'log ```python
                            else:  # [BREAKPOINT] -> Fill the null group until demand is met
                                mf.Logger(self.logger, f"ITERATION [{iteration}] E({e})J({j})T({t}) // [BREAKPOINT] // R16 // DEMAND EXCEEDS SUPPLY", 'log')
                                self.create_nulls(mv.enclaves[j], t)
                        else:  # If the demand is met, stop iterating through workers, move to the next location
                            break
                    # //////////  End of the worker loop
                    # //////////  START OF THE RATIO CONSTRAINTS
                    if cons.r03(mv.enclaves[j], t, referred_position) == 1 and len(self.party) > 0 and self.overflow is False:  # If the demand is met because it is greater than 0
                        delta_ejt = cons.r09(mv.enclaves[j], t, referred_position, self.logger)
                        mf.Logger(self.logger, f"||||| ITERATION [{iteration}] E(NONE)J({j})T({t}) // DATAFLOW A.2.1 // DELTA -> {delta_ejt} // R09 // 1 = Ratio is met = 0", 'log')
                        if delta_ejt == 0:  # DATAFLOW A.2.1
                            # This only occurs if the ratio = 0 is not met
                            delta_ejt = cons.r04(mv.enclaves[j], t, referred_position, self.logger)
                            mf.Logger(self.logger, f"||||| ITERATION [{iteration}] E(NONE)J({j})T({t}) // DATAFLOW A.2.2 // DELTA -> {delta_ejt} // R04 // 1 = Ratio > 0 is met", 'log')
                            if delta_ejt == 0:  # DATAFLOW A.2.2
                                # This only occurs if the ratio > 0 is not met
                                delta_ejt = cons.r10(mv.enclaves[j], t, referred_position, self.logger)
                                mf.Logger(self.logger, f"|||||| ITERATION [{iteration}] E(NONE)J({j})T({t}) // DATAFLOW A.2.3 // DELTA -> {delta_ejt} // R10 // 1 = Ratio > Demand is met", 'log')
                                if delta_ejt == 0:  # DATAFLOW A.2.3
                                    # This only occurs if the ratio > Demand is not met
                                    delta_ejt = cons.r11(t, referred_position)
                                    mf.Logger(self.logger, f"|||||| ITERATION [{iteration}] E(NONE)J({j})T({t}) // DATAFLOW A.2.4 // DELTA -> {delta_ejt} // R11 // 1 = No Workers left, Forcing Coaches", 'log')
                                    if delta_ejt == 0:
                                        # This only occurs if the ratio is not met and there are still workers to assign
                                        mf.randomize_worker(self.party, self.logger)
                                        self.party.clear()
                                        getattr(data, f"day_{t + 1}")[mv.enclaves[j]].clear()
                                    else:  # The ratio is not met because there are no workers left, but we have forced coaches
                                        self.clear_party_break(j, t)
                                        break
                                else:  # If the ratio is met, break the while loop to move to the next location
                                    self.clear_party_break(j, t)
                                    break
                            else:  # If the ratio is met, break the while loop to move to the next location
                                self.clear_party_break(j, t)
                                break
                        else:  # If the ratio is met, break the while loop to move to the next location
                            self.clear_party_break(j, t)
                            break
                    elif cons.r03(mv.enclaves[j], t, referred_position) == 1 and len(self.party) == 0 and self.overflow is False:  # If the demand is met because it is 0
                        break
                    elif self.overflow:  # [BREAKPOINT] -> In case demand exceeds the supply of workers and coaches
                        self.overflow = bool(False)
                        break
                # //////////  End of the While loop of workers
            # //////////  End of the enclaves loop

            if cons.r13(t, referred_position) == 0:  # FUNCTION FOR CONSTRAINT THAT PUTS UNASSIGNED WORKERS ON FORCED REST
                unasigned = list(mf.get_unassigned_list())
                getattr(data, f"day_{t + 1}")['forced_rest'] = unasigned
                mf.Logger(self.logger, f"|||||| UNASSIGNED WORKERS DETECTED // DATAFLOW A.3.1 // R13 // FORCING REST", ```python
                mf.Logger(self.logger, f"|||||| WORKERS ON FORCED REST -> {unasigned}", 'log')
                mf.Logger(self.logger, f"|||||| ASSIGNED WORKERS ({len(mv.assigned)}-> {list(mv.assigned)}", 'log')

            mf.randomize_worker(2, self.logger)  # Clear the list of workers who have already been assigned in T
        # //////////  End of the Days loop

    def clear_party_break(self, j, t):
        mf.Logger(self.logger, f"##### LOCATION {mv.enclaves[j]} // DAY {t + 1} // ASSIGNED GROUP -> {self.party}", 'log')
        self.party.clear()

    def create_nulls(self, j, t):
        D_jt = int(mf.demand_checker(j)[t + referred_position])

        for i in range(D_jt - len(self.party)):
            self.party.append("null")

        getattr(data, f"day_{t + 1}")[j] = list(self.party)  # We save the party in J at T
        mf.Logger(self.logger, f"##### LOCATION {j} // DAY {t + 1} // ASSIGNED GROUP -> {self.party}", 'log')
        self.party.clear()
        self.overflow = bool(True)


def main(logger, iteration):
    CreateGroups(logger, iteration)
