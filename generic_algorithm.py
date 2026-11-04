import csv
import random

# SETTINGS BLOCK
CSV_FILE = "GA_task.csv"
CSV_SEPARATOR = ","


# =====================================================================
# PART 1 - Read the data
# =====================================================================

def load_jobs(file_name):
    """Read the csv file and inject all rows in all_rows"""
    with open(file_name, newline="", encoding="utf-8") as file:
        all_rows = list(csv.reader(file, delimiter=CSV_SEPARATOR))

    # skip the first 2 rows with the labels and any empty row
    step_rows = []
    for row in all_rows[2:]:
        if row and row[0].strip() != "":
            step_rows.append(row)

    # check if we have any rows with value
    if len(step_rows) == 0:
        raise ValueError("The CSV has no step rows after the 2 label rows")

    # each job has 2 colums Resource and Time
    jobs_size = len(step_rows[0]) // 2

    jobs = []
    resource_column = 0
    for job_columns in range(jobs_size):
        time_column = resource_column + 1

        # go down 2 columns of each row to collect all the steps for a job
        steps = []
        for row in step_rows:
            resource = int(row[resource_column])
            time_needed = int(row[time_column])
            steps.append((resource, time_needed))

        # add a job with all its steps to the list jobs[0] is a pointer to all its steps
        jobs.append(steps)
        resource_column += 2

    return jobs

# ---- temporary test ----


def main():
    """Temporary test of the parts written so far."""
    jobs = load_jobs(CSV_FILE)

    print("number of jobs:", len(jobs))
    print("steps per job:", len(jobs[0]))
    # print(jobs)
    for i in range(len(jobs)):
        print("job", i + 1, ":", jobs[i])


if __name__ == "__main__":
    main()
