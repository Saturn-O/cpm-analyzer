# Critical Path Method Analyzer

#### Video Demo: <https://youtu.be/z8wLO0AvsHA>

---

## Overview

The **Critical Path Method (CPM)** is a project scheduling technique used to determine the longest sequence of tasks that must be completed on time for a project to finish by its deadline. By calculating task dependencies, durations, and scheduling constraints, CPM enables efficient resource allocation, risk identification, and timeline optimization.

This tool provides a command-line interface for analyzing a project's schedule using CPM logic, allowing users to identify early/late timings and the critical path.

---

## Abbreviations

| Abbreviation | Description                  |
|--------------|------------------------------|
| ES           | Early Start                  |
| EF           | Early Finish                 |
| LS           | Late Start                   |
| LF           | Late Finish                  |
| Slack        | Schedule Flexibility         |

---

## What This Script Does

- Loads a CSV file containing a project's task schedule.
- Parses task durations and predecessor relationships.
- Computes ES, EF, LS, LF, and Slack for each task.
- Identifies critical tasks (tasks with zero Slack).
- Outputs the full schedule with computed timings, critical path, and exports results to CSV for reporting or further analysis.

---

## Usage

### Terminal Execution

Run the script by providing the CSV file as an argument:
```python cpm.py your_schedule.csv```

### Input CSV Format

The input file must use semicolon (`;`) delimiters and include the following columns:

- `Task`: Unique identifier for each activity (e.g., A, B, C)
- `Duration`: Integer representing task duration
- `Predecessors`: Comma-separated list of task IDs the activity depends on. Leave blank if none.

Example:
```
Task;Predecessors;Duration
A;;6
B;;8
C;A,B;12
D;C;4
E;C;6
F;D,E;15
G;E;12
H;F,G;8
```
### Exporting Results

Once the analysis is complete, the tool will export the full schedule and critical path data to a CSV file.

Example:

```
Task;Predecessors;Duration;ES;EF;LS;LF;Slack;Critical;Successors
A;;6;0;6;2;8;2;False;C
B;;8;0;8;0;8;0;True;C
C;A,B;12;8;20;8;20;0;True;D,E
D;C;4;20;24;22;26;2;False;F
E;C;6;20;26;20;26;0;True;F,G
F;D,E;15;26;41;26;41;0;True;H
G;E;12;26;38;29;41;3;False;H
H;F,G;8;41;49;41;49;0;True;
```

### Notes

- Ensure the CSV is encoded in UTF-8.
- Columns must be named exactly as shown above.

---

## Project Structure

<pre>
cpm_project/
├── cpm.py # Main script to execute CPM analysis
├── example1.csv # Sample input file (CSV format)
├── example2.csv # Sample input file (CSV format)
├── output/ # Folder where CPM results are exported (e.g., cpm_results.csv)
├── README.md # Project documentation
</pre>

---

## Author

**José Guillermo Hernández Armendáriz**
* Location: Chihuahua, Mexico
* Final Submission – CS50X, 2025
* GitHub: Saturn-O
* EdX: Memo_Hernandez
