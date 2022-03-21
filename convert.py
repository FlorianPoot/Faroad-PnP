import math
import sqlite3
import re

DATABASE_PATH = "line1.db"


class Convert:

    def __init__(self, path: str):
        self.path = path

        self.model_altium = {"name": "altium", "desc": 0, "designator": (1, 10), "position": (2, 3), "rotation": 9}
        self.model_kicad = {"name": "kicad", "desc": 0, "designator": (1, 2), "position": (3, 4), "rotation": 5}
        self.model_mnt = {"name": "mnt", "desc": 0, "designator": (4, 5), "position": (1, 2), "rotation": 3}

    def parse(self) -> list:
        """Parse data from pick and place file"""

        # TODO Work only for 3 types of file
        # TODO Read already generated file

        with open(self.path, "r") as file:
            lines = file.readlines()

        if lines[0].split() == ['Designator', 'Footprint', 'Mid', 'X', 'Mid', 'Y',
                                'Ref', 'X', 'Ref', 'Y', 'Pad', 'X', 'Pad', 'Y', 'TB', 'Rotation', 'Comment']:
            file_model = self.model_altium
        elif lines[0] == "Ref,Val,Package,PosX,PosY,Rot,Side\n":
            file_model = self.model_kicad
        elif self.path[-3:] == "mnt":
            file_model = self.model_mnt
        else:
            raise ValueError("Unknown file model")

        lines = [line.replace("\n", "") for line in lines]  # Remove new line
        if file_model["name"] == "altium":
            lines = [[s.strip() for s in line.split(" ") if s] for line in lines]
            lines = lines[2:]  # Remove header
        elif file_model["name"] == "kicad":
            lines = [line.replace('"', "") for line in lines]
            lines = [line.split(",") for line in lines]
            lines = lines[1:]  # Remove header
        elif file_model["name"] == "mnt":
            lines = [line.replace("-", " ") for line in lines]
            lines = [line.split() for line in lines]
            print(lines)

        data = list()
        for line in lines:
            if len(line) > 0:
                d = dict()

                d["desc"] = "".join(re.findall("[a-zA-Z]", line[file_model["desc"]]))
                digit = re.findall(r"\d+", line[file_model["desc"]])
                if len(digit) > 0:
                    d["desc"] += digit[0].zfill(3)

                d["designator"] = f"{line[int(file_model['designator'][0])]} {line[int(file_model['designator'][1])]}"
                d["position"] = [float(re.findall(r"\d+\.\d+|\d+", line[i])[0]) for i in file_model["position"]]
                d["rotation"] = float(line[file_model["rotation"]])

                data.append(d)

        return data

    @staticmethod
    def search(designator: str) -> list:
        """Look in database"""

        matches = re.split("[_ :]", designator)

        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        dat = cur.execute("SELECT * FROM chip_lib;").fetchall()

        # chip_name = [d[2] for d in dat]  # Select chip_name

        for matche in matches:
            temp = list()
            for d in dat:
                if matche.upper() in d[2].upper():
                    temp.append(d)
            if len(temp) > 0:
                dat = temp

        return dat

    @staticmethod
    def panel_dimensions(points: list) -> tuple:
        """Get panel dimensions"""

        x = [p[0] for p in points]
        y = [p[1] for p in points]

        x_min, y_min = min(x), min(y)
        x_max, y_max = max(x), max(y)

        return round(abs(x_max - x_min), 3), round(abs(y_max - y_min), 3)

    @staticmethod
    def rotate(origin: tuple, points: list, angle: int) -> list:
        """Rotate a list of points clockwise by a given angle around a given origin"""

        new_pos = list()
        angle = math.radians(-angle)

        for p in points:
            ox, oy = origin
            px, py = p

            qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
            qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

            new_pos.append([qx, qy])

        return new_pos
