#!/usr/bin/env python3
"""
scheduler-gpt.py

Team Members: Sergio Cardona , (ADD your names)

This file implements three process scheduling algorithms:
  - FCFS (First Come, First Served)
  - Preemptive SJF (Shortest Job First)
  - Round Robin

It reads an input file (with a .in extension), parses the simulation parameters and process list,
runs the selected scheduling algorithm, and writes the simulation log and metrics to an output file
with the same base name but a .out extension.

Usage:
    python3 scheduler-gpt.py <input file>
"""

import sys
import os
from collections import deque

# ------------------------------------------
# Data Structures
# ------------------------------------------
class Process:
    def __init__(self, name, arrival_time, burst_time):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1

        # Lists to log events at selection:
        self.selected_times = []      # when the process was scheduled
        self.remaining_burst = []     # the remaining burst at that moment (logged before execution)
        self.executed_bursts = []     # how many ticks were executed in that selection

class InputData:
    def __init__(self, scheduler, quantum, runfor, numProcesses, processes):
        self.scheduler = scheduler  # "fcfs", "sjf", or "rr"
        self.quantum = quantum      # Only used if scheduler == "rr"
        self.runfor = runfor        # Total simulation time
        self.numProcesses = numProcesses
        self.processes = processes

class OutputHolder:
    def __init__(self, section1="", section2="", section3=""):
        self.outputSection1 = section1
        self.outputSection2 = section2
        self.outputSection3 = section3

# ------------------------------------------
# Scheduler Implementations
# ------------------------------------------
def fcfs_scheduler(processes, runfor):
    sorted_processes = processes.copy()
    sorted_processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    for process in sorted_processes:
        if current_time >= runfor:
            break  # Stop simulation if runfor reached.
        if current_time < process.arrival_time:
            current_time = process.arrival_time  # CPU idle until process arrives.
        process.start_time = current_time
        # Record selection event.
        process.selected_times.append(current_time)
        process.remaining_burst.append(process.burst_time)
        process.executed_bursts.append(process.burst_time)  # Entire burst executed in one go.
        finish = current_time + process.burst_time
        if finish <= runfor:
            process.completion_time = finish
            process.remaining_time = 0
        else:
            process.completion_time = runfor
            process.remaining_time = finish - runfor
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        process.response_time = process.start_time - process.arrival_time
        current_time = process.completion_time

def round_robin_scheduling(processes, quantum, total_time):
    queue = deque()
    time = 0
    process_index = 0
    n = len(processes)
    
    sorted_processes = processes.copy()
    sorted_processes.sort(key=lambda p: p.arrival_time)

    while time < total_time:
        while process_index < n and sorted_processes[process_index].arrival_time <= time:
            queue.append(process_index)
            process_index += 1

        if queue:
            idx = queue.popleft()
            process = sorted_processes[idx]
            if process.response_time == -1:
                process.response_time = time - process.arrival_time
            if process.start_time < 0:
                process.start_time = time

            # Log selection event BEFORE execution.
            process.selected_times.append(time)
            process.remaining_burst.append(process.remaining_time)
            exec_time = min(quantum, process.remaining_time)
            process.executed_bursts.append(exec_time)
            time += exec_time
            process.remaining_time -= exec_time

            while process_index < n and sorted_processes[process_index].arrival_time <= time:
                queue.append(process_index)
                process_index += 1

            if process.remaining_time == 0:
                process.completion_time = time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
            else:
                queue.append(idx)
        else:
            time += 1

def sjf_scheduler(processes, runfor, timeline):
    current_time = 0
    last_chosen = None  # Tracks the process running in the previous tick
    while current_time < runfor:
        ready = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
        if ready:
            chosen = min(ready, key=lambda p: p.remaining_time)
            # Log a selection event only when there is a context switch.
            if chosen != last_chosen:
                chosen.selected_times.append(current_time)
                chosen.remaining_burst.append(chosen.remaining_time)
                chosen.executed_bursts.append(1)  # For SJF, one tick at a time.
                if chosen.response_time == -1:
                    chosen.response_time = current_time - chosen.arrival_time
                last_chosen = chosen
            # Record that the CPU is busy with the chosen process this tick.
            timeline[current_time] = chosen.name
            chosen.remaining_time -= 1
            if chosen.remaining_time == 0:
                chosen.completion_time = current_time + 1
                chosen.turnaround_time = chosen.completion_time - chosen.arrival_time
                chosen.waiting_time = chosen.turnaround_time - chosen.burst_time
                last_chosen = None
        else:
            timeline[current_time] = None
        current_time += 1

# ------------------------------------------
# Timeline Computation
# ------------------------------------------
def compute_timeline(inputData):
    # For FCFS and RR, use the logged selection events.
    timeline = [None] * inputData.runfor
    for p in inputData.processes:
        for sel_time, exec_burst in zip(p.selected_times, p.executed_bursts):
            for t in range(sel_time, min(sel_time + exec_burst, inputData.runfor)):
                timeline[t] = p.name
    return timeline

# ------------------------------------------
# Output Formatting Functions
# ------------------------------------------
def format_scheduler_info(scheduler_info):
    if scheduler_info.scheduler == "rr":
        scheduler_name = "Using Round-Robin"
    elif scheduler_info.scheduler == "fcfs":
        scheduler_name = "Using First-Come First-Served"
    elif scheduler_info.scheduler == "sjf":
        scheduler_name = "Using preemptive Shortest Job First"
    else:
        scheduler_name = ""
    return f"{scheduler_info.numProcesses} processes", scheduler_name

def get_quantum_info(scheduler_info):
    if scheduler_info.scheduler == "rr":
        return f"Quantum   {scheduler_info.quantum}\n\n"
    return ""

def create_log(input_data, timeline):
    log_lines = []
    runfor = input_data.runfor
    processes = input_data.processes
    for t in range(runfor):
        events = []
        # Arrivals
        for p in processes:
            if p.arrival_time == t:
                events.append(f"Time {t:3} : {p.name} arrived")
        # Finishes
        for p in processes:
            if p.completion_time == t:
                events.append(f"Time {t:3} : {p.name} finished")
        # Selections
        for p in processes:
            for idx, sel_time in enumerate(p.selected_times):
                if sel_time == t:
                    events.append(f"Time {t:3} : {p.name} selected (burst {p.remaining_burst[idx]:3})")
        # Only log Idle if the timeline indicates the CPU is truly idle.
        if timeline[t] is None:
            events.append(f"Time {t:3} : Idle")
        # Order events: arrivals, then finishes, then selections, then idle.
        arr_events = [e for e in events if "arrived" in e]
        fin_events = [e for e in events if "finished" in e]
        sel_events = [e for e in events if "selected" in e]
        idle_events = [e for e in events if "Idle" in e]
        ordered = arr_events + fin_events + sel_events + idle_events
        log_lines.extend(ordered)
    log_lines.append(f"Finished at time {runfor}")
    return "\n".join(log_lines)

def calculate_metrics(input_data):
    log = []
    unfinished = []
    for p in input_data.processes:
        if p.remaining_time > 0:
            unfinished.append(f"{p.name} did not finish")
        else:
            log.append(f"{p.name} wait {p.waiting_time:3} turnaround {p.turnaround_time:3} response {p.response_time:3}")
    if unfinished:
        log.append(" ".join(unfinished))
    return "\n".join(log)

def getResultText(inputData, timeline):
    outputHandler = OutputHolder()
    numProcessText, schedulerNameText = format_scheduler_info(inputData)
    quantumText = get_quantum_info(inputData)
    outputString1 = numProcessText + "\n" + schedulerNameText + "\n" + quantumText
    schedulerLog = create_log(inputData, timeline)
    processMetrics = calculate_metrics(inputData)
    outputHandler.outputSection1 = outputString1
    outputHandler.outputSection2 = schedulerLog
    outputHandler.outputSection3 = processMetrics
    return outputHandler.outputSection1 + schedulerLog + "\n\n" + outputHandler.outputSection3

# ------------------------------------------
# Input File Parsing (Original style)
# ------------------------------------------
def parse_input_file(filename):
    try:
        with open(filename, "r") as file:
            raw_lines = file.readlines()
    except IOError:
        print(f"Error: Cannot open file {filename}")
        sys.exit(1)
    lines = []
    for line in raw_lines:
        line = line.split("#")[0].strip()
        if line:
            lines.append(line)
    processcount = None
    runfor = None
    scheduler = None
    quantum = None
    processes = []
    i = 0
    while i < len(lines):
        tokens = lines[i].split()
        if not tokens:
            i += 1
            continue
        directive = tokens[0].lower()
        if directive == "processcount":
            if len(tokens) < 2:
                print("Error: Missing parameter processcount")
                sys.exit(1)
            processcount = int(tokens[1])
        elif directive == "runfor":
            if len(tokens) < 2:
                print("Error: Missing parameter runfor")
                sys.exit(1)
            runfor = int(tokens[1])
        elif directive == "use":
            if len(tokens) < 2:
                print("Error: Missing parameter use")
                sys.exit(1)
            scheduler = tokens[1].lower()
        elif directive == "quantum":
            if len(tokens) < 2:
                print("Error: Missing parameter quantum")
                sys.exit(1)
            quantum = int(tokens[1])
        elif directive == "process":
            try:
                name_index = tokens.index("name") + 1
                arrival_index = tokens.index("arrival") + 1
                burst_index = tokens.index("burst") + 1
                proc_name = tokens[name_index]
                proc_arrival = int(tokens[arrival_index])
                proc_burst = int(tokens[burst_index])
                processes.append(Process(proc_name, proc_arrival, proc_burst))
            except (ValueError, IndexError):
                print("Error: Missing parameter in process definition")
                sys.exit(1)
        elif directive == "end":
            break
        i += 1
    if processcount is None:
        print("Error: Missing parameter processcount")
        sys.exit(1)
    if runfor is None:
        print("Error: Missing parameter runfor")
        sys.exit(1)
    if scheduler is None:
        print("Error: Missing parameter use")
        sys.exit(1)
    if scheduler == "rr" and quantum is None:
        print("Error: Missing quantum parameter when use is 'rr'")
        sys.exit(1)
    if len(processes) != processcount:
        print("Error: Process count does not match the number of process definitions")
        sys.exit(1)
    return InputData(scheduler, quantum, runfor, processcount, processes)

# ------------------------------------------
# Main Function: Input -> Scheduling -> Output
# ------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)
    input_filename = sys.argv[1]
    if not input_filename.endswith(".in"):
        print("Usage: scheduler-gpt.py <input file>")
        sys.exit(1)
    inputData = parse_input_file(input_filename)
    # For SJF, record timeline during simulation.
    if inputData.scheduler == "rr":
        round_robin_scheduling(inputData.processes, inputData.quantum, inputData.runfor)
        timeline = compute_timeline(inputData)
    elif inputData.scheduler == "fcfs":
        fcfs_scheduler(inputData.processes, inputData.runfor)
        timeline = compute_timeline(inputData)
    elif inputData.scheduler == "sjf":
        timeline = [None] * inputData.runfor
        sjf_scheduler(inputData.processes, inputData.runfor, timeline)
    else:
        print("Error: Unknown scheduling algorithm.")
        sys.exit(1)
    output_text = getResultText(inputData, timeline)
    base = os.path.splitext(input_filename)[0]
    output_filename = base + ".out"
    try:
        with open(output_filename, "w") as outfile:
            outfile.write(output_text)
        print(f"Output written to {output_filename}")
    except IOError:
        print(f"Error: Cannot write to file {output_filename}")
        sys.exit(1)

if __name__ == "__main__":
    main()