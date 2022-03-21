import sqlite3
import shutil
import os


print("Production line converter")
print("-------------------------\n")

while 1 > int(line_nb := input("Convert to production line (1, 2): ")) > 2:
    print("Error: enter 1 or 2")

path = input("Project path: ")
print()

# Get chip lib data from project to be converted
project_conn = sqlite3.connect(path)
project_cur = project_conn.cursor()
project_data = project_cur.execute("SELECT * FROM chip_lib;").fetchall()
project_conn.close()

# Get chip lib data from dest line
line_conn = sqlite3.connect(f"line{line_nb}.db")
line_cur = line_conn.cursor()
line_data = line_cur.execute("SELECT * FROM chip_lib;").fetchall()
line_conn.close()

# Create a project copy
copy_path = path[:-3] + f" - Line {line_nb}.db"
shutil.copyfile(path, copy_path)

copy_conn = sqlite3.connect(copy_path)
copy_cur = copy_conn.cursor()

# Convert list to dict
line_data_dict = dict()
for dat in line_data:
    line_data_dict[dat[2]] = dat
for pro in project_data:
    if pro[2] in line_data_dict:
        # Compare names, if equal replace in project database
        copy_cur.execute(f'UPDATE chip_lib SET '
                         f'chip_param="{line_data_dict[pro[2]][3]}",'
                         f'vision_param="{line_data_dict[pro[2]][4]}",'
                         f'nozzle_param="{line_data_dict[pro[2]][5]}",'
                         f'feeder_param="{line_data_dict[pro[2]][6]}",'
                         f'action_param="{line_data_dict[pro[2]][7]}",'
                         f'mark1="{line_data_dict[pro[2]][8]}",'
                         f'mark2="{line_data_dict[pro[2]][9]}",'
                         f'nozzle_param2="{line_data_dict[pro[2]][10]}"'
                         f' WHERE chip_name="{pro[2]}";')
        copy_conn.commit()

        print(f"{pro[2]} updated")
    else:
        print(f"{pro[2]} not found in production line {line_nb}")
copy_conn.close()

print("\nSuccess!\n")
os.system("PAUSE")
