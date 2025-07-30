"""
cpm.py

Command-line tool for performing Critical Path Method (CPM) analysis on project schedules.

This script reads a CSV file containing project tasks, durations, and predecessor relationships.
It calculates key scheduling metrics including:
- Early Start (ES)
- Early Finish (EF)
- Late Start (LS)
- Late Finish (LF)
- Slack time
- Identification of critical activities

The CSV file must be passed as a command-line argument when executing the script.
Example usage:
    python cpm.py project_schedule.csv

Outputs:
- Tabular summary of activities with computed CPM values
- Printed representation of the critical path
- CSV export containing ES, EF, LS, LF, Slack, Critical status, and successor relationships

Requirements:
- pandas
- CSV formatted with columns: Task, Duration, Predecessors
"""

import pandas as pd
from datetime import datetime
import sys
import os

# Validate command-line input
if len(sys.argv) < 2:
    print("You must provide the CSV file name as a command-line argument.")
    print("Example: python cpm.py example2.csv")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.exists(filename):
    print(f"The file '{filename}' was not found. Check the name or path.")
    sys.exit(1)


# Load CSV and prepare DataFrame
def load_and_prepare_data(filename):
    """
    Loads a CSV file and prepares the DataFrame for CPM analysis.
    - Parses predecessors into lists
    - Initializes CPM columns
    - Builds successor relationships

    Parameters:
        filename (str): Path to the input CSV file

    Returns:
        pandas.DataFrame: Prepared DataFrame with all necessary columns
    """
    # Load CSV
    df = pd.read_csv(filename, sep=";", skipinitialspace=True)

    # Convert Predecessors column to list
    df["Predecessors"] = (
        df["Predecessors"].fillna("").apply(lambda x: x.split(",") if x else [])
    )

    # Initialize CPM columns
    df["ES"] = 0
    df["EF"] = 0
    df["LS"] = 0
    df["LF"] = 0
    df["Slack"] = 0
    df["Critical"] = False

    # Build successors map
    successors_map = {}
    for _, row in df.iterrows():
        for pred in row["Predecessors"]:
            successors_map.setdefault(pred, []).append(row["Task"])

    df["Successors"] = df["Task"].apply(lambda t: successors_map.get(t, []))

    return df


# Create DataFrame for further analysis
df = load_and_prepare_data(filename)

# Build activity dictionary
activities = {
    row["Task"]: {"duration": row["Duration"], "predecessors": row["Predecessors"]}
    for _, row in df.iterrows()
}


def export_cpm_to_csv(df, output_dir="outputs"):
    """
    Exports the CPM dataframe to a timestamped CSV file.
    Converts Predecessors list to string format.
    Converts Successors list to string format.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Convert Predecessors/Successors list to comma-separated string
    df["Predecessors"] = df["Predecessors"].apply(
        lambda x: ",".join(x) if isinstance(x, list) else str(x)
    )
    df["Successors"] = df["Successors"].apply(
        lambda x: ",".join(x) if isinstance(x, list) else str(x)
    )

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cpm_output_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    # Export to CSV
    df.to_csv(filepath, index=False, sep=";")
    print(f"CPM results exported to {filepath}")


# CPM functions
def calculate_es_ef(df):
    """
    Calculates Early Start (ES) and Early Finish (EF) for each activity in the project.

    Parameters:
        df (pandas.DataFrame): DataFrame containing tasks, durations, and predecessors.

    Returns:
        pandas.DataFrame: Updated DataFrame with ES and EF columns populated.
    """
    es_dict = {}
    ef_dict = {}
    remaining = df.copy()

    while not remaining.empty:
        for i, row in remaining.iterrows():
            # Check if all predecessors have their EF calculated
            if all(p in ef_dict for p in row["Predecessors"]):
                # If there are predecessors, ES is the max of their EF
                es = (
                    max([ef_dict[p] for p in row["Predecessors"]])
                    if row["Predecessors"]
                    else 0
                )
                # EF = ES + Duration
                ef = es + row["Duration"]
                es_dict[row["Task"]] = es
                ef_dict[row["Task"]] = ef
                remaining = remaining.drop(i)
                break
    # Add values to DataFrame
    df["ES"] = df["Task"].map(es_dict)
    df["EF"] = df["Task"].map(ef_dict)
    return df


def calculate_ls_lf(df):
    """
    Calculates Late Start (LS) and Late Finish (LF) for each activity based on project completion.

    Parameters:
        df (pandas.DataFrame): DataFrame with ES/EF already calculated and successor relationships.

    Returns:
        pandas.DataFrame: Updated DataFrame with LS and LF columns populated.
    """
    ls_dict = {}
    lf_dict = {}
    project_finish = df["EF"].max()  # Overall project finish time
    remaining = df.copy()

    # Initialize LF for tasks without successors (i.e., terminal nodes)
    for _, row in df.iterrows():
        if not row["Successors"]:
            lf_dict[row["Task"]] = project_finish

    while not remaining.empty:
        for i, row in remaining.iterrows():
            # Check if all successors have their LS calculated
            if all(s in ls_dict for s in row["Successors"]):
                # LF is minimum LS among all successors
                lf = (
                    min([ls_dict[s] for s in row["Successors"]])
                    if row["Successors"]
                    else project_finish
                )
                # LS = LF - Duration
                ls = lf - row["Duration"]
                lf_dict[row["Task"]] = lf
                ls_dict[row["Task"]] = ls
                remaining = remaining.drop(i)
                break
    # Add values to DataFrame
    df["LF"] = df["Task"].map(lf_dict)
    df["LS"] = df["Task"].map(ls_dict)
    return df


def calculate_slack(df):
    """
    Computes slack time and determines whether each activity is critical.

    Parameters:
        df (pandas.DataFrame): DataFrame containing ES, EF, LS, and LF values.

    Returns:
        pandas.DataFrame: Updated DataFrame with Slack and Critical columns.
    """
    df["Slack"] = df["LS"] - df["ES"]  # Total float for each activity
    df["Critical"] = df["Slack"] == 0  # True if task is on the critical path
    return df


def print_critical_path(df):
    """
    Identifies and displays the critical path based on tasks with zero slack.

    Parameters:
        df (pandas.DataFrame): DataFrame containing project scheduling data, including the 'Critical' column.

    Returns:
        str: A formatted string representing the ordered sequence of critical tasks.
    """
    critical_tasks = df[df["Critical"]]["Task"].tolist()  # Extracts critical tasks
    path_str = " -> ".join(critical_tasks)
    print(f"Critical path: {path_str}")
    return path_str


# Run CPM analysis
df = calculate_es_ef(df)
df = calculate_ls_lf(df)
df = calculate_slack(df)

# Output results
print(df)
print_critical_path(df)
export_cpm_to_csv(df)
