import sqlite3

class Database():
	def __init__(self,dbPath):
		self.dbPath = dbPath
	def connect(self):
		self.db = sqlite3.connect(self.dbPath)
		print("connect")
	def close(self):
		self.db.close()
		print("close")