import sqlite3

class Database():
	def __init__(self,dbPath):
		self.dbPath = dbPath
	def connect(self):
		self.db = sqlite3.connect(self.dbPath)
		print("connect")
	def execute(self,sql):
		print(sql)
		c = self.db.cursor()
		c.execute(sql)
		self.db.commit()
	def close(self):
		self.db.close()
		print("close")

def getUserSchema():
	return """id INTEGER PRIMARY KEY,
			   username TEXT UNIQUE,
			   password TEXT"""

