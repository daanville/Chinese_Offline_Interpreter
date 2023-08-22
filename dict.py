class Dict:
	def __init__(self):
		self.words = {}
		with open("res/cedict.itp", "r", encoding="utf8") as f:
			data = f.read()
			lines = data.splitlines()
			for line in lines:
				truncate_start = line[line.find(' ')+1:]
				hanzi = truncate_start[:truncate_start.find(' ')]
				trans = line[line.find("/"):-1].replace("/", "\n")
				self.words[hanzi] = trans
		print(f"Dictionary loaded into memory with {len(self.words)} entries.")

	def translate(self, hanzi):
		if hanzi in self.words:
			return self.words[hanzi]
		return "_"
