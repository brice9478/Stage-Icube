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
    print("accession : display all the informations in the database that corresponds to the given gene's accession")

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
    cursor.execute("SELECT * FROM human_genes_to_orthologs")
    print(cursor.fetchall()[0])
    cursor.execute("SELECT * FROM orthologs")
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

def accession():
    response = input("Please enter a gene's accession to get informations about it: ")
    print("- - - - - - - - - -")
    try:
        cursor.execute("SELECT * FROM genes WHERE accession = ?", (response,))
        result = cursor.fetchall()
        specie = result[0][1]
        print(f"Accession: {result[0][0]}\nSpecie: {result[0][1]}\nSequence: {result[0][2]}\nChromosome: {result[0][3]}\nStart: {result[0][4]}\nEnd: {result[0][5]}")
    except:
        print(f"{response} doesn't correspond to any data in the table \"genes\"")
    print()
    try:
        cursor.execute("SELECT * FROM exon_structure WHERE accession = ?", (response,))
        result = cursor.fetchall()
        print("- - Exon structure - -")
        print(f"Number of exons: {len(result)}")
        for i in range(len(result)):
            print(f"- {i + 1} -\nExon id: {result[i][1]}")
            print(f"Begin position: {result[i][2]} and begin status: {result[i][3]}")
            print(f"End position: {result[i][4]} and end status: {result[i][5]}")
    except:
        print(f"{response} doesn't correspond to any data in the table \"exon_structure\"")
    print()
    try:
        cursor.execute("SELECT * FROM mutations WHERE accession = ?", (response,))
        result = cursor.fetchall()
        print("- - Mutations - -")
        print(f"Number of possible mutations: {len(result)}")
        for i in range(len(result)):
            print(f"\nMutation id: {result[i][1]}\nPathogenicity: {result[i][2]}")
            try:
                cursor.execute("SELECT * FROM pdi WHERE mutation_id = ?", (result[i][1],))
                pdi = cursor.fetchall()
                print("- Chromosome's modifications -")
                for k in range(len(pdi)):
                    print(f"\tPosition: {pdi[k][1]}\n\tDeletion: {pdi[k][2]}\n\tInsertion: {pdi[k][3]}")
            except:
                print(f"No data for the chromosome's modifications of the mutation {result[i][1]}")
    except:
        print(f"{response} doesn't correspond to any data in the table \"mutations\"")
        print("Note: the table \"mutations\" only contains informations on human genes.")
    print()
    try:
        cursor.execute("SELECT * FROM human_genes_to_orthologs JOIN orthologs ON human_genes_to_orthologs.group_id = orthologs.group_id")
        result = cursor.fetchall()
        if specie == "Homo sapiens":
            print("- - Orthologs - -")
            for i in range(len(result)):
                if result[i][1] == response:
                    print(f"{result[i][4]} - ", end='')
        else:
            print("- - Ortholog of - -")
            for i in range(len(result)):
                if result[i][4] == response:
                    print(f"{result[i][1]} - ", end='')
        print()
    except:
        print(f"{response} doesn't correspond to any data in the tables \"orthologs\" and \"human_genes_to_orthologs\"")
    print("- - - - - - - - - -")




print("Welcome in the database interface. Here, you can do some operations on the database.")
print("If you want to know all the possible operations, please enter \"help\".")
commands = ["help", "data example", "sql", "structure", "accession"]
functions = [help, data_example, sql, structure, accession]
# tables = ["species", "genes", "exon_structure", "mutations", "pdi"]
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
