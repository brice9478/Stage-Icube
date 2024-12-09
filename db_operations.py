import mysql.connector
from sshtunnel import SSHTunnelForwarder
from sys import argv
import sqlite3
import pickle
from rich.console import Console
from rich.table import Table

connection = sqlite3.connect("mydata.db")
cursor = connection.cursor()

def help():
    print("Here is a list of the commands you can execute.")
    print("help : you're here")
    print("exit : stop the program")
    print("data example : print the first row of each table")
    print("sql : enter a sql code to be executed")
    print("structure : display the organisation of the db")

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

def structure():
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        console = Console()
        if not tables:
            console.print("[bold red]Db don't have any tables. Please follow the instructions in help.txt.[/bold red]")
            return
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            rich_table = Table(title=f"Table: [cyan]{table_name}[/cyan]", show_header=True, header_style="bold magenta")
            rich_table.add_column("Column name", style="yellow")
            rich_table.add_column("Type", style="green")
            rich_table.add_column("Primary key", style="blue")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                primary_key = "Yes" if col[5] == 1 else "No"
                rich_table.add_row(col_name, col_type, primary_key)
            console.print(rich_table)
    except sqlite3.Error as e:
        console.print(f"[bold red]Erreur : {e}[/bold red]")


print("Welcome in the database interface. Here, you can do some operations on the database.")
print("If you want to know all the possible operations, please enter \"help\".")
commands = ["help", "data example", "sql", "structure"]
functions = [help, data_example, sql, structure]
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
