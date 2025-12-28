# from assert_gpt
# plot_correct.py

from pathlib import Path

from source.shared import BucketPlotData
from source.shared import plot_bucket_step_statistics

def plot_correct(model_folder_path: str, bucket_count, xlabel: str, ylabel: str, title: str=''):
    ok_steps, ok_counts = _get_counts_by_steps(model_folder_path, file_name='oks.txt')
    error_steps, error_counts = _get_counts_by_steps(model_folder_path, file_name='errors.txt')
    bucket_plot_data = []
    for i in range(len(ok_steps)):
        step = ok_steps[i]
        ok_count = ok_counts[i]
        error_count = error_counts[i]
        sample_count = ok_count + error_count
        bucket_plot_datum = BucketPlotData(step=step, y=ok_count, sample_count=sample_count)
        bucket_plot_data.append(bucket_plot_datum)
    plot_bucket_step_statistics(bucket_count=bucket_count, bucket_plot_data=bucket_plot_data, xlabel=xlabel, ylabel=ylabel, title=title)

def _get_counts_by_steps(folder_path: str, file_name: str) -> tuple[list[int], list[int | float]]:
    file_steps: list[int] = []
    file_counts: list[int | float] = []
    with open(Path(folder_path).joinpath(file_name), 'r') as file:
        for line in file:
            split_line = list(map(int, line.removesuffix('\n').split(', ')))
            line_step = split_line[0]
            line_count = sum(split_line[1:])
            file_steps.append(line_step)
            file_counts.append(line_count)
    return file_steps, file_counts
