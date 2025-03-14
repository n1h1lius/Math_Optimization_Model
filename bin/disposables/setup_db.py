import pandas

encoding = 'UTF-8'


class InfoSorter:

	@staticmethod
	def white_spaces(line):  # White Space = "_"
		line = list(line)
		for i in range(len(line)):
			if line.index(line[i]) == (len(line) - 1) and line[i] == ' ':
				line.remove(line[i])
			elif line[i] == ' ':
				line[i] = '_'
		return "".join(line)

	@staticmethod
	def del_dots(line):  # Delete Dots
		line = list(line)
		for i in range(len(line)):
			try:
				if line[i] == '.':
					line.remove(line[i])
			except IndexError:
				pass
		return "".join(line)

	@staticmethod
	def del_dashes(line):  # Delete dashes
		line = list(line)
		for i in range(len(line)):
			if line[i] == '-':
				line[i] = '_'
		return "".join(line)


# ================================================================================================================
# FILES PATHS FOR SETUP
# ================================================================================================================

employees_csv = {
	"name": "tbEmployee",
	"path": "Data/DB/csv/tbEmployee.csv",
	"db": "Data/DB/db_py/Employees/employees.py"}

afin_employees_csv = {
	"name": "tbAfinWW",
	"path": "Data/DB/csv/tbAfinWW.csv",
	"db": "Data/DB/db_py/Employees/afin_emp.py"}

LaborEnclaves_csv = {
	"name": "tbLaborEnclaves",
	"path": "Data/DB/csv/tbLaborEnclaves.csv",
	"db": "Data/DB/db_py/Enclaves/enclaves.py"}

afin_enclaves_csv = {
	"name": "tbAfinWJ",
	"path": "Data/DB/csv/tbAfinWJ.csv",
	"db": "Data/DB/db_py/Enclaves/afin_encl.py"}

tbdemand_csv = {
	"name": "tbDemand",
	"path": "Data/DB/csv/tbDemand.csv",
	"db": "Data/DB/db_py/Demand/demand_raw.py"}

csv_list = [employees_csv, LaborEnclaves_csv, afin_employees_csv, afin_enclaves_csv, tbdemand_csv]

# ================================================================================================================
# LOAD XLSX
# ================================================================================================================


def load(file):
	excel = pandas.ExcelFile(file)
	for i in range(len(excel.sheet_names)):
		df = pandas.DataFrame(pandas.read_excel(excel, f'{excel.sheet_names[i]}', index_col=None))
		df.to_csv(f'Data/DB/csv/{excel.sheet_names[i]}.csv', encoding=encoding, index=False)
		# print(f'{excel.sheet_names[i]}.csv has been saved!')


# ================================================================================================================
# READ CSV
# ================================================================================================================

class ReadCSV:

	def __init__(self):
		for i in range(len(csv_list)):
			# print(f"Sorting {mv.csv_list[i]['name']} data")
			data = self.read_csv(csv_list[i]['path'])
			self.write(data, csv_list[i]['name'], csv_list[i]['db'])
			# print(f"{mv.csv_list[i]['name']} Sorted")

	@staticmethod
	def read_csv(file):
		with open(file, "r", encoding=encoding) as f:
			csv = f.readlines()
			f.close()
		return csv

	@staticmethod
	def sorter(info, index, index2):
		if index2 == 1:  # Workers
			alias = InfoSorter.white_spaces(info[1])
			alias = InfoSorter.del_dots(alias)
			alias = InfoSorter.del_dashes(alias)
			worker = f'''
worker_{index} = {"{"}
	"id": "{info[0]}",
	"alias": "{alias}",
	"role": "{info[2]}",
	"tipo": "{info[3]}",
	"state": "0",
	"formacion": [],
	"horas": 0
	{"}"}'''
			return worker

		if index2 == 2:  # Enclaves
			alias = InfoSorter.white_spaces(info[1])
			alias = InfoSorter.del_dots(alias)
			alias = InfoSorter.del_dashes(alias)
			enclave = f'''
enclave_{index} = {"{"}
	"id": "{info[0]}",
	"alias": "{alias}",
	"demanda_h": {float(info[2])},
	"ratio": {float(info[3])}
	{"}"}'''
			return enclave

		if index2 == 3:  # Afinities: Worker-Worker + Enclave-Worker
			if index == 0:
				return ""
			elif index > 0:
				var = InfoSorter.white_spaces(info[1])
				var = InfoSorter.del_dots(var)
				afinidad = f'''{var} = {list(info[2:])}
'''
				return afinidad

		if index2 == 4:  # Enclaves Demand
			var = InfoSorter.white_spaces(info[0])
			var = InfoSorter.del_dashes(var)
			demanda = f"{var} = {list(info[1:])}\n"
			return demanda

	@staticmethod
	def write_db(item, db):
		with open(db, "a", encoding=encoding) as f:
			f.write(item)
			f.close()

	def write(self, txt, name, db):  # py to csv

		try:

			for j in range(len(txt)):
				line = txt[j+1].split(",")
				for l in range(len(line)):
					line[l] = str(line[l].replace("\n", ""))

				if name == employees_csv['name']:
					worker = self.sorter(line, j, 1)
					self.write_db(worker, db)
				if name == LaborEnclaves_csv['name']:
					enclave = self.sorter(line, j, 2)
					self.write_db(enclave, db)
				if name == afin_employees_csv['name']:
					afin_emp = self.sorter(line, j, 3)
					self.write_db(afin_emp, db)
					if j == len(txt)-2:
						afin_emp = "null = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']"
						self.write_db(afin_emp, db)
				if name == afin_enclaves_csv['name']:
					afin_enc = self.sorter(line, j, 3)
					self.write_db(afin_enc, db)
					if j == len(txt)-2:
						afin_enc = "null = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']"
						self.write_db(afin_enc, db)
				if name == tbdemand_csv['name']:
					enclave = self.sorter(line, j, 4)
					self.write_db(enclave, db)

		except IndexError:
			pass


def start_setup(fia):
	print('''Saving CSVs \n''')
	load(fia)
	print('''\n Finished Saving CSV \n Sorting data \n''')
	ReadCSV()


def reset():

	print("///// EXECUTING RESET")
	data = ["Data/DB/db_py/Demand/demand_raw.py",
			"Data/DB/db_py/Employees/afin_emp.py",
			"Data/DB/db_py/Employees/employees.py",
			"Data/DB/db_py/Enclaves/afin_encl.py",
			"Data/DB/db_py/Enclaves/enclaves.py"]

	for i in range(len(data)):
		with open(data[i], "w", encoding=encoding) as f:
			f.write("")
