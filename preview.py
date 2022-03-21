from tkinter import *
from convert import Convert


class PreviewWindow(Toplevel):

    def __init__(self, parent):
        super(PreviewWindow, self).__init__()

        self.parent = parent
        self.transient(self.parent)

        self.width = 800
        self.height = 500

        self.origin_offset = 120

        optionheight = (self.winfo_screenheight() // 2) - (self.height // 2)
        optionwidth = (self.winfo_screenwidth() // 2) - (self.width // 2)

        self.geometry(f"{self.width}x{self.height}+{optionwidth}+{optionheight}")
        # self.resizable(False, False)
        self.minsize(self.width, self.height)

        self.geometry(f"{self.width}x{self.height}")

        self.title("Preview")
        # self.iconbitmap("icon.ico")

        self.positions = [p["position"] for p in Convert(self.parent.source.get()).parse()]

        # Change units
        if self.parent.units.get() == "inch":
            self.positions = [[x * 25.4, y * 25.4] for x, y in self.positions]
        elif self.parent.units.get() == "mil":
            self.positions = [[x / 39.37, y / 39.37] for x, y in self.positions]

        x_dim, y_dim = Convert.panel_dimensions(self.positions)
        self.positions = Convert.rotate((x_dim / 2, y_dim / 2), self.positions, int(self.parent.rot.get()))

        self.canvas = Canvas(self, bg="black")
        self.canvas.pack(expand=YES, fill=BOTH)

        self.draw_origin()
        self.draw_components()

        self.bind("<Configure>", self.scale)

        self.focus_set()
        self.grab_set()

    def scale(self, _=None) -> None:
        """Scale axis with window size"""

        self.height = int(self.geometry().split("x")[1].split("+")[0])
        self.width = int(self.geometry().split("x")[0])

        self.canvas.delete("all")
        self.draw_origin()
        self.draw_components()

    def draw_origin(self) -> None:
        """Draw origin axis"""

        self.canvas.create_line(self.width - self.origin_offset, 0, self.width - self.origin_offset, self.height,
                                fill="white")
        self.canvas.create_line(0, self.height - self.origin_offset, self.width, self.height - self.origin_offset,
                                fill="white")

        for x in range(round(-self.width, -2), 400, 100):
            if x != 0:
                self.canvas.create_text(x + (self.width - self.origin_offset), (self.height - self.origin_offset) + 10,
                                        text=str(-x // 5), fill="white")

        for y in range(round(-self.height, -2), 400, 100):
            if y != 0:
                self.canvas.create_text((self.width - self.origin_offset) + 10, y + (self.height - self.origin_offset),
                                        text=str(-(y // 5)), fill="white")

    def draw_components(self) -> None:
        """Draw components on canvas with offsets"""

        for p in self.positions:
            self.canvas.create_rectangle((p[0] * 5) + (self.width - self.origin_offset) - float(self.parent.x_offset.get() * 5) - 5,
                                         -(p[1] * 5) + (self.height - self.origin_offset) - float(self.parent.y_offset.get() * 5) - 5,
                                         (p[0] * 5) + (self.width - self.origin_offset) - float(self.parent.x_offset.get() * 5) + 5,
                                         -(p[1] * 5) + (self.height - self.origin_offset) - float(self.parent.y_offset.get() * 5) + 5,
                                         fill="blue")
