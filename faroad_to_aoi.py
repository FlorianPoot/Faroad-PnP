import os
import re

print("FAROAD PnP to AOI EKT-VT-880 converter")
print("--------------------------------------\n")

path = input("FAROAD PnP path: ")
print()

with open(path, "r") as file:
    data = file.readlines()

data = [d.split() for d in data]  # Split columns

aoi_data = list(["ChipName X(mm) Y(mm) Angle ModalName\n"])
unique_components = set()
for line in data[1:]:
    aoi_line = [""] * 5  # Five columns

    aoi_line[0] = "".join(re.findall("[a-zA-Z]", line[3]))
    digit = re.findall(r"\d+", line[3])
    if len(digit) > 0:
        aoi_line[0] += str(int(digit[0]))  # Remove leading zeros

    aoi_line[1] = line[0]  # X
    aoi_line[2] = line[1]  # Y
    aoi_line[3] = str(int(float(line[2])))  # Angle (without floating number)

    component = line[4].split(":")
    aoi_line[4] = component[1]  # Modal name
    if not bool(re.search(r"\d+", component[1])):
        # Add more info if no number
        aoi_line[4] += f":{component[-1]}"

    unique_components.add(aoi_line[4])
    aoi_data.append(" ".join(aoi_line) + "\n")

with open("aoi_cad.txt", "w") as file:
    file.writelines(aoi_data)

print("Unique components:")
print("------------------")
for c in unique_components:
    print(c)

print("\nSuccess!\n")
os.system("PAUSE")
