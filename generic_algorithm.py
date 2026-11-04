import csv
import random

# SETTINGS BLOCK
CSV_FILE = "GA_task.csv"
CSV_SEPARATOR = ","
POPULATION_SIZE = 50    # how many lists we have at a time
SEED = 42


# =====================================================================
# PART 1 - Read the data
# =====================================================================

def load_jobs(file_name):
    """Read the CSV and return the jobs: each job is a list of (machine, time) steps."""
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

    # each job has 2 columns machine and Time
    jobs_size = len(step_rows[0]) // 2

    jobs = []
    machine_column = 0
    for job_columns in range(jobs_size):
        time_column = machine_column + 1

        # go down 2 columns of each row to collect all the steps for a job
        steps = []
        for row in step_rows:
            machine = int(row[machine_column])
            time_needed = int(row[time_column])
            steps.append((machine, time_needed))

        # add a job with all its steps to the list jobs[0] is a pointer to all its steps
        jobs.append(steps)
        machine_column += 2

    return jobs


# =====================================================================
# create random lists
# =====================================================================

def random_list(jobs, rdm):
    """Return one random list: each job number once per step, shuffled."""
    one_list = []

    # create one list that is in order listing all jobs 11 times
    for job_number, job_steps in enumerate(jobs):
        number_of_steps = len(job_steps)
        for step in range(number_of_steps):
            one_list.append(job_number)

    # mix the list into a random order
    rdm.shuffle(one_list)
    return one_list


def whole_population(population_size, jobs, rdm):
    """create multiple random list by calling the helper function that creates one random list"""
    population = []

    for _ in range(population_size):
        population.append(random_list(jobs, rdm))

    return population


# =====================================================================
# score a lists
# =====================================================================

def calculate_score(one_list, jobs):
    """Build the schedule from one list and return when the last step finishes."""
    job_ready_at = [0] * len(jobs)  # when each job can start its next step
    next_step = [0] * len(jobs)     # which step is each job on
    machine_free_time = {}          # when each machine is free

    for job_number in one_list:
        # check what step the job is on and retrive that step's machine and time
        step_number = next_step[job_number]
        machine, time_needed = jobs[job_number][step_number]

        machine_free_at = machine_free_time.get(machine, 0)
        start = max(job_ready_at[job_number], machine_free_at)
        end = start + time_needed

        job_ready_at[job_number] = end
        machine_free_time[machine] = end
        next_step[job_number] += 1

    # return when the last step finishes
    return max(job_ready_at)


# ---- temporary test ----
def main():
    """Temporary test of the parts written so far."""
    rdm = random.Random(SEED)
    jobs = load_jobs(CSV_FILE)
    population = whole_population(POPULATION_SIZE, jobs, rdm)

    # for step 1
    print("number of jobs:", len(jobs))
    print("steps per job:", len(jobs[0]))
    # print(jobs)
    # for i in range(len(jobs)):
    #     print("job", i + 1, ":", jobs[i])

    # for step 2
    print("number of lists:", len(population))
    print("length of one list:", len(population[0]))
    print("first 15 numbers of list 1:", population[0][:15])
    # print("list 2:", population[1])
    # for i in range(len(population)):
    #     print(population[i])

    # for step 3
    # the 3-job example: first 3 jobs and first 3 steps from the CSV
    small_jobs = [
        [(9, 22), (3, 49), (1, 47)],
        [(5, 17), (10, 13), (7, 23)],
        [(5, 24), (4, 28), (1, 18)],
    ]
    print("list [2, 0, 1, 2, 0, 1, 0, 2, 1]:", calculate_score(
        [2, 0, 1, 2, 0, 1, 0, 2, 1], small_jobs), "(should be 136)")

    # the real data: one random list
    print("random list from real data time take for that list:",
          calculate_score(population[0], jobs))


if __name__ == "__main__":
    main()
