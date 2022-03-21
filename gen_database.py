from pathlib import Path
import sqlite3
import os


def set_database():
    """Parse all database and select data with unique constraint"""

    for path in Path("Q:/Production/Clients/").rglob("*.db"):
        if "Thumbs" not in path.name:

            conn = sqlite3.connect(str(path))
            cur = conn.cursor()
            try:
                data = cur.execute("SELECT * FROM chip_lib;").fetchall()
            except sqlite3.OperationalError as e:
                print(e)
                continue
            conn.close()

            if len(data) > 0:
                if "Ligne 2" in str(path):
                    print("Ligne 2", path.name)
                    conn = sqlite3.connect("line2.db")
                else:
                    print("Ligne 1", path.name)
                    conn = sqlite3.connect("line1.db")

                cur = conn.cursor()
                for d in data:
                    if d[2][:6].isdecimal():
                        try:
                            cur.execute(f"INSERT INTO chip_lib VALUES {d};")
                        except sqlite3.IntegrityError as e:
                            print(e)

                conn.commit()
                conn.close()


def create_database(name):
    """Create database table"""

    conn = sqlite3.connect(name)
    cur = conn.cursor()
    cur.execute("""
               CREATE TABLE chip_lib(
                   id INT,
                   chip_group CHAR,
                   chip_name CHAR UNIQUE,
                   chip_param CHAR,
                   vision_param CHAR,
                   nozzle_param CHAR,
                   feeder_param CHAR,
                   action_param CHAR,
                   mark1 CHAR,
                   mark2 CHAR,
                   nozzle_param2 CHAR
               );""")
    conn.commit()
    conn.close()

    print("done")


# Remove previous table
if os.path.exists("line1.db"):
    os.remove("line1.db")
if os.path.exists("line2.db"):
    os.remove("line2.db")


create_database("line1.db")
create_database("line2.db")

set_database()

print("\nDatabase successfully created\n")
os.system("PAUSE")
