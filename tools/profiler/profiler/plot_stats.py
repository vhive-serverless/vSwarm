
import math
import matplotlib.pyplot as plt
import numpy as np

from log_config import *


def plot_histograms(memory: list, duration: list, cpu: list, output_folder: list) -> None:
    """
    Plots the collected percentile averages in log-histogram format

    Parameters:
    - `memory` (list): list of memory utilization of functions
    - `duration` (list): list of duration utilization of functions
    - `cpu` (list): list of cpu utilization of functions
    - `output_folder` (str): Directory path where the output PNGs are to be stored
    """

    def plot_hist_log_scale(
        data: list,
        data_name: str,
        plot_name: str,
        xlabel: str,
        ylabel: str,
        png_filename: str,
    ) -> None:
        """
        Plots the data in log-histogram format

        Parameters:
        - `data` (list): list of data points
        - `data_name` (str): Name of data
        - `plot_name` (str): Name of plot
        - `xlabel` (str): X-label data
        - `ylabel` (str): Y-label data
        - `png_filename` (str): File path where the output PNG is to be stored
        """

        # If data is empty, then return without plotting
        if len(data) == 0:
            log.critical(f"{data_name} data empty. {plot_name} not plotted.")
            return

        try:

            # To avoid math errors
            data = [d + 0.01 if d == 0 else d for d in data]

            # Plotting bins on log scale: 0.1-0.2, 0.2-0.3...0.9-1, 1-2, 2-3, 3-4.... 8-9, 9-10, 10-20, 20-30, ....90-100, 100-200, 200-300,...
            max_data = max(data)
            min_data = min(data)
            max_data_log = math.ceil(math.log10(max_data))
            min_data_log = math.floor(math.log10(min_data))

            bins = [
                i * math.pow(10, j)
                for j in range(min_data_log, max_data_log)
                for i in range(1, 10)
            ]
            bins.append(math.pow(10, max_data_log))
            bins.sort()

            counts, bins = np.histogram(data, bins)

            # X-Label
            xlabel_bins = []
            for i in range(1, len(bins)):
                u = bins[i - 1]
                v = bins[i]
                if u >= 1:
                    u = int(u)
                else:
                    u = round(u, abs(math.floor(math.log10(u))))
                if v >= 1:
                    v = int(v)
                else:
                    v = round(v, abs(math.floor(math.log10(v))))
                xlabel_bins.append(f"{u}:{v}")

            # Clear the plot
            plt.clf()

            # Increase the figure size and resolution
            dpi = plt.rcParams["figure.dpi"] * 3
            figsize = [i * 3 for i in plt.rcParams["figure.figsize"]]
            plt.figure(figsize=figsize, dpi=dpi)

            # Plot the histogram bars
            plt.bar(x=range(1, len(bins)), height=counts, edgecolor="black")
            plt.xticks(
                ticks=range(1, len(bins)), labels=xlabel_bins, rotation=90, fontsize=16
            )
            plt.yticks(fontsize=16)
            plt.xlabel(f"{xlabel}", fontsize=17)
            plt.ylabel(f"{ylabel}", fontsize=17)
            plt.title(f"{plot_name}", fontsize=18)

            # Change figure size to fit the PNG image and save it
            plt.tight_layout()
            plt.savefig(f"{png_filename}")
            plt.clf()

            log.info(f"{plot_name} plotted at {png_filename}")

        except Exception as e:
            log.critical(f"Error while plotting {plot_name}. Error: {e}")

    plot_hist_log_scale(
        data=memory,
        data_name="memory utilization of benchmark functions",
        plot_name="Memory Utilization Distribution of Benchmark functions",
        xlabel="Memory (Mb)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/memory-utilization-distribution.png",
    )
    plot_hist_log_scale(
        data=cpu,
        data_name="cpu utilization of benchmark functions",
        plot_name="CPU Utilization Distribution of Benchmark functions",
        xlabel="CPU Utilization",
        ylabel="Frequency",
        png_filename=f"{output_folder}/cpu-utilization-distribution.png",
    )
    plot_hist_log_scale(
        data=duration,
        data_name="Duration of benchmark functions",
        plot_name="Duration Distribution of Benchmark functions",
        xlabel="Time Duration (milliseconds)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/duration-distribution.png",
    )

