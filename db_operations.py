import mysql.connector
from sshtunnel import SSHTunnelForwarder
from sys import argv
import sqlite3
import pickle

connection = sqlite3.connect("mydata.db")
cursor = connection.cursor()

def help():
    print("Here is a list of the commands you can execute.")
    print("help : you're here")
    print("exit : stop the program")
    print("data example : print the first row of each table")
    print("sql : enter a sql code to be executed")

def data_example():
    cursor.execute("SELECT * FROM species")
    print(cursor.fetchall()[0])
    cursor.execute("SELECT * FROM genes")
    print(cursor.fetchall()[0])
    cursor.execute("SELECT * FROM exon_structure")
    print(cursor.fetchall()[0])
    cursor.execute("SELECT * FROM mutations")
    print(cursor.fetchall()[0])
    cursor.execute("SELECT * FROM pdi")
    print(cursor.fetchall()[0])

def sql():
    code = input("type in your sql code: ")
    try:
        cursor.execute(code)
        print(cursor.fetchall())
    except sqlite3.Error as e:
        print("/!\\ Error during the request's execution.")
        print(f"Detail: {e}")
        print(f"Error at: {code}")





print("Welcome in the database interface. Here, you can do some operations on the database.")
print("If you want to know all the possible operations, please enter \"help\".")
commands = ["help", "data example", "sql"]
functions = [help, data_example, sql]
tables = ["species", "genes", "exon_structure", "mutations", "pdi"]
while True:
    print(">> ", end = '')
    answer = input()
    if answer == "exit":
        break
    exists = False
    for i in range(len(commands)):
        if commands[i] == answer:
            exists = True
            functions[i]()
    if exists == False:
        print("Aknown command. Please try again with \"help\"")




connection.commit()
connection.close()
exit(0)
