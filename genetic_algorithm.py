import csv

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
# PART 2 - create random lists
# =====================================================================

def random_list(jobs, rdm):
    """Return one random list: each job number once per step, shuffled."""
    one_list = []

    # create one list that is in order listing all jobs 11 times
    for job_position, job_steps in enumerate(jobs):
        number_of_steps = len(job_steps)
        for step in range(number_of_steps):
            one_list.append(job_position)

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
# PART 3 - score the population
# each member of the population is a pair: (list, score)
# =====================================================================

def calculate_score(one_list, jobs):
    """Build the schedule from one list and return when the last step finishes."""
    job_ready_at = [0] * len(jobs)      # when each job can start its next step
    next_step = [0] * len(jobs)         # which step is each job on
    machine_free_time = {}              # when each machine is free

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


def score_population(population, jobs):
    """Return the population as (list, score) pairs."""
    scored_population = []
    for one_list in population:
        score = calculate_score(one_list, jobs)
        scored_population.append((one_list, score))

    return scored_population


# =====================================================================
# PART 4 - Tournament
# =====================================================================

def tournament(scored_population, tournament_size, rdm):
    """Pick TOURNAMENT_SIZE random members and return the list with the lowest score."""
    contestants = rdm.sample(scored_population, tournament_size)

    # start qith no winner yet and the score being infinity
    best_list = None
    best_score = float("inf")

    for one_list, score in contestants:
        if score < best_score:
            best_list = one_list
            best_score = score

    return best_list


def create_parents(scored_population, tournament_size, rdm):
    """Run one tournament per member of the population and return all the winners."""
    parents = []
    for _ in range(len(scored_population)):
        parents.append(tournament(scored_population, tournament_size, rdm))

    return parents


# =====================================================================
# PART 5  - crossover + repair
# =====================================================================

def repair(child, jobs):
    """Replace extra copies of a job with the jobs that are missing."""
    # 1. read left to right: any job seen more times than it has steps is an extra
    seen = [0] * len(jobs)
    extra_position = []

    for position, job_number in enumerate(child):
        seen[job_number] += 1
        if seen[job_number] > len(jobs[job_number]):
            extra_position.append(position)

    # 2. list the jobs that appear too few times (once for each missing copy)
    missing_jobs = []
    for job_position, job_steps in enumerate(jobs):
        how_many_missing = len(job_steps) - seen[job_position]
        for _ in range(how_many_missing):
            missing_jobs.append(job_position)

    # 3. put a missing job into each extra position
    for position, job_number in zip(extra_position, missing_jobs):
        child[position] = job_number


def crossover(parent_1, parent_2, crossover_chance, jobs, rdm):
    """Return 2 children: mixed (cut and swap, then repaired) or copies of the parents."""
    if rdm.random() < crossover_chance:
        # cut both parents at the same random spot and swap the ends
        cut = rdm.randint(1, len(parent_1) - 1)
        child_1 = parent_1[:cut] + parent_2[cut:]
        child_2 = parent_2[:cut] + parent_1[cut:]

        repair(child_1, jobs)
        repair(child_2, jobs)
        return child_1, child_2

    # no crossover this time: children are copies of the parents
    return list(parent_1), list(parent_2)


def make_children(parents, jobs, crossover_chance, rdm):
    """Pair the parents up (1st with 2nd, 3rd with 4th, ...) and return all their children."""
    children = []
    for pair_start in range(0, len(parents), 2):
        parent_1 = parents[pair_start]
        parent_2 = parents[pair_start + 1]
        child_1, child_2 = crossover(
            parent_1, parent_2, crossover_chance, jobs, rdm)
        children.append(child_1)
        children.append(child_2)

    return children


# =====================================================================
# PART 6  - mutation
# =====================================================================

def mutate(child, mutation_chance,  rdm):
    """With MUTATION_CHANCE, swap the numbers at 2 random positions of the child."""
    if rdm.random() < mutation_chance:
        first_position, second_position = rdm.sample(range(len(child)), 2)

        # swap: keep the first number aside so it isn't lost
        first_number = child[first_position]
        child[first_position] = child[second_position]
        child[second_position] = first_number


def mutate_children(children, mutation_chance, rdm):
    """Give every child its chance to be mutated."""
    for child in children:
        mutate(child, mutation_chance, rdm)


# =====================================================================
# PART 7  - the genetic algorithm loop
# =====================================================================

def find_best(scored_population):
    """Return the list with the lowest score in the population, and that score."""
    best_list = None
    best_score = float("inf")

    for one_list, score in scored_population:
        if score < best_score:
            best_list = one_list
            best_score = score

    return best_list, best_score


def genetic_algorithm(jobs, settings, rdm):
    """use the given settings return the best list ever, its score, and best score per gen."""
    population = whole_population(settings["population_size"], jobs, rdm)

    best_list_ever = None
    best_score_ever = float("inf")
    best_score_per_generation = []      # for the chart in the report

    for _ in range(settings["generations"]):
        # score every list
        scored_population = score_population(population, jobs)

        # remember the best of this generation, and the best ever
        best_list, best_score = find_best(scored_population)
        best_score_per_generation.append(best_score)
        if best_score < best_score_ever:
            best_list_ever = list(best_list)
            best_score_ever = best_score

        # make the next generation
        parents = create_parents(
            scored_population, settings["tournament_size"], rdm)
        children = make_children(
            parents, jobs, settings["crossover_chance"], rdm)
        mutate_children(children, settings["mutation_chance"], rdm)

        # the children replace the old population
        population = children

    return best_list_ever, best_score_ever, best_score_per_generation
