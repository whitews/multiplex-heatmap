import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import ttkthemes as themed_tk

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BACKGROUND_COLOR = '#ededed'
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 720
PAD_SMALL = 2
PAD_MEDIUM = 4
PAD_LARGE = 8


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
        self.heat_map_fig = None

        main_frame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        main_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=0,
            pady=0
        )

        file_chooser_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
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

        self.bottom_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        self.bottom_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=PAD_LARGE,
            pady=0
        )

    def load_csv_files(self):
        self.csv_files = filedialog.askopenfiles(
            initialdir="/home/swhite/vbox_share/John_Yi_projects/multiplex_heatmaps/clean"
        )
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

        df = df.groupby("Sample").mean()

        df_norm_col = (df - df.min()) / (df.max() - df.min())
        df_norm_col['mean'] = df_norm_col.mean(axis=1)

        self.data = df_norm_col

    def generate_heat_map(self):
        sort_column = self.sort_by_column.get()

        if sort_column == 'Sample':
            df = self.data.sort_values("Sample")
        elif sort_column == "mean":
            df = self.data.sort_values("mean", ascending=False)
        else:
            df = self.data

        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        self.heat_map_fig = plt.figure(figsize=(14, 18))
        heat_map_ax = sns.heatmap(
            df,
            cmap='bwr',
            cbar_kws={"aspect": 80}
        )
        heat_map_ax.set_ylim((self.data.shape[0], 0))
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(self.heat_map_fig, master=self.bottom_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def save_heat_map_image(self):
        save_file = filedialog.asksaveasfilename(
            filetypes=(("PNG Image", "*.png"), ("All Files", "*.*")),
            defaultextension='.png',
            title="Save Heat Map as PNG file")
        if save_file is None:
            return

        self.heat_map_fig.savefig(save_file, bbox_inches="tight")


if __name__ == "__main__":
    root = themed_tk.ThemedTk()
    root.set_theme('arc')

    screen_height = root.winfo_screenheight()

    if screen_height > 2000:
        scaling = 2.0
    else:
        scaling = 1.0

    print(scaling)
    root.tk.call('tk', 'scaling', scaling)

    app = Application(root, scaling)
    root.mainloop()
