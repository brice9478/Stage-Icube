from sys import argv
import sqlite3
import pickle

def list_species_and_id():
    with open("orthologues.pickle", "rb") as file:
        total_data = pickle.load(file)
    list_specie = []
    counter = 0
    for h_gene in range(0, len(total_data["genes"])):
        for ortho in range(0, len(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]])):
            list_specie.append([total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][0]])
            list_specie[counter].append(total_data["genes"][h_gene][list(total_data["genes"][h_gene].keys())[0]][ortho]["specie"][1])
            counter += 1
    list_specie = list({item[0]: item for item in list_specie}.values())
    return list_specie

def fill_genes():
    with open("table_genes.pickle", "rb") as file: #from the program fill_table_genes.py
        list_genes = pickle.load(file)
    return list_genes

def fill_exon_structure():
    with open("table_exon_struct.pickle", "rb") as file: #from the program fill_table_exon_struct.py
        list_exon_struct = pickle.load(file)
    return list_exon_struct

def fill_mutations():
    with open("table_mutations.pickle", "rb") as file: #from the program fill_table_mutations.py
        list_mutations = pickle.load(file)
    return list_mutations


connection = sqlite3.connect("mydata.db")
cursor = connection.cursor()
print("Executing... create tables")
cursor.execute("""
CREATE TABLE IF NOT EXISTS species (
    specie TEXT PRIMARY KEY,
    id_specie INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS genes (
    accession TEXT PRIMARY KEY,
    specie TEXT,
    sequence TEXT,
    chromosome TEXT,
    start INTEGER,
    end INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS exon_structure (
    exon_structure_random_id INTEGER PRIMARY KEY,
    exon_id TEXT,
    begin_position INTEGER,
    begin_status TEXT,
    end_position INTEGER,
    end_status TEXT,
    accession TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS mutations (
    mutations_random_id INTEGER PRIMARY KEY,
    mutation_id INTEGER,
    pathogenicity TEXT,
    accession TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS pdi (
    position INTEGER PRIMARY KEY,
    deletion TEXT,
    insertion TEXT,
    mutation_id INTEGER
)
""")

print("Executing... fill table: species")
cursor.execute(f"SELECT COUNT(*) FROM species") #on peut mettre {variable} pour inclure le contenu de la variable
row_count = cursor.fetchone()[0]
if row_count == 0:
    cursor.executemany("INSERT INTO species VALUES (?, ?)", list_species_and_id())
else:
    print("species: table already completed.")

print("Executing... fill table: genes")
cursor.execute(f"SELECT COUNT(*) FROM genes")
row_count = cursor.fetchone()[0]
if row_count == 0:
    cursor.executemany("INSERT INTO genes VALUES (?, ?, ?, ?, ?, ?)", fill_genes())
else:
    print("genes: table already completed.")

print("Executing... fill table: exon_structure")
cursor.execute(f"SELECT COUNT(*) FROM exon_structure")
row_count = cursor.fetchone()[0]
if row_count == 0:
    cursor.executemany("INSERT INTO exon_structure VALUES (?, ?, ?, ?, ?, ?, ?)", fill_exon_structure())
else:
    print("exon_structure: table already completed.")

print("Executing... fill table: mutations")
cursor.execute(f"SELECT COUNT(*) FROM mutations")
row_count = cursor.fetchone()[0]
if row_count == 0:
    cursor.executemany("INSERT INTO mutations VALUES (?, ?, ?, ?)", fill_mutations())
else:
    print("mutations: table already completed.")

connection.commit()
connection.close()