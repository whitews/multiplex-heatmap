import io
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import seaborn as sns
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import ttkthemes as themed_tk

matplotlib.use("TkAgg")

BACKGROUND_COLOR = '#ededed'
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 720
PAD_SMALL = 2
PAD_MEDIUM = 4
PAD_LARGE = 8

COLOR_MAPS = [
    'bwr', 'coolwarm',
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
    'RdYlBu', 'RdYlGn', 'Spectral', 'seismic',
    'gist_rainbow', 'rainbow', 'jet'
]


class Application(tk.Frame):

    def __init__(self, master, scaling):

        tk.Frame.__init__(self, master=master)

        self.master.minsize(
            width=int(WINDOW_WIDTH * scaling),
            height=int(WINDOW_HEIGHT * scaling)
        )
        self.master.config(bg=BACKGROUND_COLOR)
        self.master.title("Multiplex Heat Map")

        self.csv_files = []
        self.data = None
        self.sort_by_column = tk.StringVar(self.master)
        self.pan_start_x = None
        self.pan_start_y = None
        self.pil_image = None
        self.tk_image = None
        self.current_colormap = tk.StringVar(self.master)
        self.current_colormap.set('bwr')

        self.master.bind("<Control-m>", self.toggle_cmap_option)

        self.main_frame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        self.main_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=0,
            pady=0
        )

        file_chooser_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        file_chooser_frame.pack(
            fill=tk.X,
            expand=False,
            anchor=tk.N,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM
        )

        file_chooser_button_frame = tk.Frame(
            file_chooser_frame,
            bg=BACKGROUND_COLOR
        )

        load_csv_button = ttk.Button(
            file_chooser_button_frame,
            text='Load CSV Files',
            command=self.load_csv_files
        )
        load_csv_button.pack(side=tk.LEFT)

        self.generate_heat_map_button = ttk.Button(
            file_chooser_button_frame,
            text='Generate Heat Map',
            command=self.generate_heat_map
        )
        self.generate_heat_map_button.pack(
            side=tk.LEFT,
            padx=PAD_MEDIUM
        )

        ttk.Label(
            file_chooser_button_frame,
            text="Sort by:",
            background=BACKGROUND_COLOR
        ).pack(
            side=tk.LEFT,
            padx=PAD_MEDIUM
        )
        self.sort_option = ttk.Combobox(
            file_chooser_button_frame,
            textvariable=self.sort_by_column,
            state='readonly'
        )
        self.sort_option['values'] = ['Sample', 'mean']
        self.sort_option.pack(side=tk.LEFT, fill='x', expand=False)

        self.colormap_option = ttk.Combobox(
            file_chooser_button_frame,
            textvariable=self.current_colormap,
            state='readonly'
        )
        self.colormap_option['values'] = COLOR_MAPS

        save_regions_button = ttk.Button(
            file_chooser_button_frame,
            text='Save Plot',
            command=self.save_heat_map_image
        )
        save_regions_button.pack(side=tk.RIGHT, anchor=tk.N)

        file_chooser_button_frame.pack(
            anchor='n',
            fill='x',
            expand=False,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM
        )

        self.bottom_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.bottom_frame.pack(
            fill=tk.BOTH,
            expand=True,
            anchor='n',
            padx=PAD_LARGE,
            pady=0
        )

        self.canvas = tk.Canvas(self.bottom_frame)

        self.scrollbar_v = ttk.Scrollbar(
            self.bottom_frame,
            orient=tk.VERTICAL
        )
        self.scrollbar_h = ttk.Scrollbar(
            self.bottom_frame,
            orient=tk.HORIZONTAL
        )
        self.scrollbar_v.config(command=self.canvas.yview)
        self.scrollbar_h.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.scrollbar_v.set)
        self.canvas.config(xscrollcommand=self.scrollbar_h.set)

        self.scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas.bind("<ButtonPress-1>", self.on_pan_button_press)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        self.canvas.bind("<ButtonRelease-1>", self.on_pan_button_release)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_button_press)
        self.canvas.bind("<B2-Motion>", self.pan_image)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_button_release)
        self.canvas.bind("<ButtonPress-3>", self.on_pan_button_press)
        self.canvas.bind("<B3-Motion>", self.pan_image)
        self.canvas.bind("<ButtonRelease-3>", self.on_pan_button_release)

    def toggle_cmap_option(self, event):
        if self.colormap_option.winfo_ismapped():
            self.colormap_option.pack_forget()
        else:
            self.colormap_option.pack(side=tk.LEFT, fill='x', expand=False)

    def load_csv_files(self):
        self.csv_files = filedialog.askopenfiles()
        if len(self.csv_files) == 0:
            return

        self.process_csv_files()

    def process_csv_files(self):
        data_frames = []
        for f in self.csv_files:
            data_frames.append(pd.read_csv(f))
        df = pd.concat(data_frames)

        del_pattern = r"(Standard|Background|Control|custom|overlapping|no stim)"
        sample_filter = df.Sample.str.contains(del_pattern)
        df = df[~sample_filter]

        if "Population" in df:
            df = df.set_index(["Sample", "Population"])
            self.sort_option['values'] = ['Sample', 'Population', 'mean']
        else:
            # if there are more than 1 row for a sample, average the rows
            # also sets index to "Sample"
            df = df.groupby(["Sample", "Population"]).mean()

        df_norm_col = (df - df.min()) / (df.max() - df.min())
        df_norm_col['mean'] = df_norm_col.mean(axis=1)

        self.data = df_norm_col

    def generate_heat_map(self):
        sort_column = self.sort_by_column.get()

        if sort_column == 'Sample':
            df = self.data.sort_values("Sample")
        elif sort_column == 'Population':
            df = self.data.sort_values("Population")
        elif sort_column == "mean":
            df = self.data.sort_values("mean", ascending=False)
        else:
            df = self.data

        # half inch per row and column, plus some space for the text
        plt.figure(
            figsize=((0.5 * self.data.shape[1]) + 2.0, (0.5 * self.data.shape[0]))
        )
        heat_map_ax = sns.heatmap(
            df[df.columns[~df.columns.isin(['mean'])]],  # exclude mean col from plot
            cmap=self.current_colormap.get(),
            cbar_kws={"aspect": 80}
        )
        heat_map_ax.set_ylim((self.data.shape[0], 0))
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        self.pil_image = Image.open(buf)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)

        width, height = self.pil_image.size
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, width, height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.update()

    def on_pan_button_press(self, event):
        self.canvas.config(cursor='fleur')

        # starting position for panning
        self.pan_start_x = int(self.canvas.canvasx(event.x))
        self.pan_start_y = int(self.canvas.canvasy(event.y))

    def pan_image(self, event):
        self.canvas.scan_dragto(
            event.x - self.pan_start_x,
            event.y - self.pan_start_y,
            gain=1
        )

    # noinspection PyUnusedLocal
    def on_pan_button_release(self, event):
        self.canvas.config(cursor='')

    def save_heat_map_image(self):
        save_file = filedialog.asksaveasfilename(
            filetypes=(("PNG Image", "*.png"), ("All Files", "*.*")),
            defaultextension='.png',
            title="Save Heat Map as PNG file")
        if save_file is None:
            return

        self.pil_image.save(save_file)


if __name__ == "__main__":
    root = themed_tk.ThemedTk()
    root.set_theme('arc')

    screen_height = root.winfo_screenheight()

    if screen_height > 2000:
        tk_scaling = 2.0
    else:
        tk_scaling = 1.0

    root.tk.call('tk', 'scaling', tk_scaling)

    app = Application(root, tk_scaling)
    root.mainloop()
