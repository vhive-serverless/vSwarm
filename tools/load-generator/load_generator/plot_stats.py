import math
import matplotlib.pyplot as plt
import numpy as np

from log_config import *


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


def plot_hist_log_scale_compare_data(
    data: list,
    data_name: str,
    compare_data: list,
    scatterplot_label: list,
    plot_name: str,
    xlabel: str,
    ylabel: str,
    png_filename: str,
) -> None:
    """
    Plots the data in log-histogram format. It also highlights the bars by depicting a marker on the bars (as scatter plot) where compare_data exists

    Parameters:
    - `data` (list): list of data points
    - `data_name` (str): Name of data
    - `compare_data` (list): list of compare-data points
    - `scatterplot_label` (str): compare-data label
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

        # Maximum height along Y-axis
        max_height = max(counts)

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

        # Find the bins where compare_data datapoints exist. Mark those indices.
        count_compare, bins = np.histogram(compare_data, bins)
        marker_indices = []
        for i in range(0, len(count_compare)):
            if count_compare[i] > 0:
                marker_indices.append(i + 1)

        # Clear the plot
        plt.clf()

        # Change the figure size and resolution
        dpi = plt.rcParams["figure.dpi"] * 3
        figsize = [i * 3 for i in plt.rcParams["figure.figsize"]]
        plt.figure(figsize=figsize, dpi=dpi)

        # Plot the bars
        plt.bar(x=range(1, len(bins)), height=counts, edgecolor="black")
        plt.xticks(
            ticks=range(1, len(bins)), labels=xlabel_bins, rotation=90, fontsize=16
        )
        plt.yticks(fontsize=16)

        # Mark those bins where compare_data datapoints exist.
        plt.scatter(
            x=marker_indices,
            y=[counts[i - 1] + (max_height * 0.025) for i in marker_indices],
            label=f"{scatterplot_label}",
            color="green",
            marker="v",
            s=200,
        )

        # Write labels, legend, fit the figure, and save it
        plt.xlabel(f"{xlabel}", fontsize=17)
        plt.ylabel(f"{ylabel}", fontsize=17)
        plt.title(f"{plot_name}", fontsize=18)
        plt.legend(fontsize=17)
        plt.tight_layout()
        plt.savefig(f"{png_filename}")
        plt.clf()

        log.info(f"{plot_name} plotted at {png_filename}")

    except Exception as e:
        log.critical(f"Error while plotting {plot_name}. Error: {e}")


def plot_scatter_logx_logy(
    data1: list,
    data1_label: str,
    data2: list,
    data2_label: str,
    plot_name: str,
    xlabel: str,
    ylabel: str,
    png_filename: str,
) -> None:

    try:
        x1, y1 = zip(*data1)
        x2, y2 = zip(*data2)

        # Clear the plot
        plt.clf()

        # Change the figure size and resolution
        dpi = plt.rcParams["figure.dpi"] * 3
        figsize = [i * 3 for i in plt.rcParams["figure.figsize"]]
        plt.figure(figsize=figsize, dpi=dpi)

        plt.scatter(x=x1, y=y1, color="blue", marker="o", label=data1_label, s=100)
        plt.scatter(x=x2, y=y2, color="red", marker="o", label=data2_label, s=100)

        # Set the plot to log scale on both axes
        plt.xscale("log")
        plt.yscale("log")

        # Write labels, legend, fit the figure, and save it
        plt.xlabel(f"{xlabel}", fontsize=18)
        plt.ylabel(f"{ylabel}", fontsize=18)
        plt.yticks(fontsize=18)
        plt.xticks(fontsize=18)
        plt.title(f"{plot_name}", fontsize=18)
        plt.legend(fontsize=18)
        plt.tight_layout()
        plt.savefig(f"{png_filename}")
        plt.clf()

        log.info(f"{plot_name} plotted at {png_filename}")

    except Exception as e:
        log.critical(f"Error while plotting {plot_name}. Error: {e}")
