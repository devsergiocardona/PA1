# PA1: Process Scheduler

This repository contains:
- **scheduler-gpt.py**: Main script implementing FCFS, preemptive SJF, and Round Robin scheduling.
- **compare.py**: A helper script for line-by-line comparison of two output files.
- **input_files/**: Folder containing `.in` files (the inputs).
- **output_files/**: Folder containing reference `.out` files for comparison (given by prof)

## Requirements
- Python 3.x

## Running the Scheduler
1. **Open a terminal** in the root folder of this repository (the same folder that contains `scheduler-gpt.py` and `compare.py`).
2. **Run** the scheduler with an input file from `input_files/`. For example:
   ```bash
   python3 scheduler-gpt.py input_files/c2-fcfs.in
