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


connection = sqlite3.connect("mydata.db")
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS species (
    specie TEXT PRIMARY KEY,
    id_specie INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS genes (
    accession TEXT PRIMARY KEY,
    sequence TEXT,
    chromosome TEXT,
    start INTEGER,
    end INTEGER,
    specie TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS exon_structure (
    exon_id TEXT PRIMARY KEY,
    begin_position INTEGER,
    begin_status TEXT,
    end_position INTEGER,
    end_status TEXT,
    accession TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS mutations (
    mutation_id INTEGER PRIMARY KEY,
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

cursor.executemany("INSERT INTO species VALUES (?, ?)", list_species_and_id())

connection.commit()
connection.close()