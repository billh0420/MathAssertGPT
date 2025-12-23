# from shared.plot
# plot_bucket_step_statistics.py

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from typing import Union

from dataclasses import dataclass

@dataclass
class BucketPlotData:
    step: int
    y: Union[float, int]
    sample_count: int

def x_ticker_formatter(x, pos):
    k = 1000
    if x < 10 * k:
        formatted_x = f'{x}'
    else:
        formatted_x = f'{int(x / k)}K'
    return formatted_x

def plot_bucket_step_statistics(bucket_count: int, bucket_plot_data: list[BucketPlotData], xlabel: str, ylabel: str, title: str, x_ticker_formatter=None):
    if len(bucket_plot_data) == 0:
        return
    x_steps = [bucket_plot_datum.step for bucket_plot_datum in bucket_plot_data]
    y_values = [bucket_plot_datum.y for bucket_plot_datum in bucket_plot_data]
    sample_counts = [bucket_plot_datum.sample_count for bucket_plot_datum in bucket_plot_data]
    first_step = x_steps[0]
    last_step = x_steps[-1]
    bucket_count = min(bucket_count, len(x_steps))  # Note this
    step_size = last_step // bucket_count
    if step_size > 1:
        bucket_ranges = list(range(step_size, last_step + step_size, step_size))
    else:
        step_size = 1
        bucket_ranges = list(range(step_size, last_step + step_size, step_size))
    bucket_ys = [0] * (len(bucket_ranges))
    bucket_sample_counts = [0] * (len(bucket_ranges))
    for i in range(len(x_steps)):
        x_step = x_steps[i]
        y = y_values[i]
        sample_count = sample_counts[i]
        bucket_index = _get_bucket_index(x_step, bucket_count, first_step, last_step)
        if bucket_index >= bucket_count:
            continue
        bucket_ys[bucket_index] += y
        bucket_sample_counts[bucket_index] += sample_count
    # plot
    ys = [y / sample_count if sample_count > 0 else 0 for (y, sample_count) in zip(bucket_ys, bucket_sample_counts)]
    markersize = 3
    if x_ticker_formatter is not None:
        # Apply the formatter to the x-axis
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(x_ticker_formatter))
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.plot(bucket_ranges, ys, marker='o', linewidth=markersize / 2, markersize=markersize)
    plt.show()

def _get_bucket_index(step, bucket_count, first_step, last_step) -> int:
    step_count = last_step - first_step + 1
    bucket_size = step_count // bucket_count
    if bucket_size < 1:
        bucket_size = 1
    remainder = step_count % bucket_count
    cutoff = first_step + remainder * (bucket_size + 1)
    if step <= cutoff:
        bucket_index = (step - first_step) // (bucket_size + 1)
    else:
        bucket_index = remainder + (step - cutoff) // bucket_size
    assert bucket_index >= 0
    return bucket_index

def _get_bucket_index_original(step, bucket_count, first_step, last_step) -> int:
    step_count = last_step - first_step + 1
    bucket_size = step_count // bucket_count
    if bucket_size < 1:
        bucket_size = 1
    bucket_index = (step - first_step) // bucket_size
    if bucket_index < 0:
        bucket_index = 0
    return bucket_index