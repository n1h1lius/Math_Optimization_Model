from Data.DB.db_py.Enclaves import enclaves as enc
from Data.DB.db_py.Employees import employees as emp


def create_list(tipe, source):
    x = list(source.__dict__.items())
    opt = []

    for i in range(len(x)):
        if str(str(x[i]).split())[4] != '_':
            alia = getattr(source, f'{x[i][0]}')['alias']
            if tipe == "emp" and getattr(source, f'{x[i][0]}')['role'] == "0":
                opt.append(alia)
            elif tipe == "coach" and getattr(source, f'{x[i][0]}')['role'] == "1":
                opt.append(alia)
            elif tipe == "enc":
                opt.append(alia)
            elif tipe == "all":
                opt.append(alia)

    return opt


# ================================================================================================================
# LISTS
# ================================================================================================================

h = [50, 60]  # MAX LABOUR HOUS (H sub e)
enclaves = create_list("enc", enc)  # ENCLAVES (J)
workers = create_list("emp", emp)  # WORKERS (W)
coaches = create_list("coach", emp)  # COACHES (C)
work_coach = workers + coaches
plantilla = create_list("all", emp)  # WORKERS + COACHES MERGED TOGETHER (E)

assigned = []
not_assigned = []

values = []
z_values = []

# ================================================================================================================
# VARS
# ================================================================================================================

days = 15  # TWO WEEKS TOTAL DAYS (T)
