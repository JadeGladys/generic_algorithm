import csv
import random

# SETTINGS BLOCK
CSV_FILE = "GA_task.csv"
CSV_SEPARATOR = ","
POPULATION_SIZE = 50    # how many lists we have at a time
SEED = 42
TOURNAMENT_SIZE = 2     # how many parents we compare during a tournament
# how often two parents are actually mixed (0.8 = 80% of the time)
CROSSOVER_CHANCE = 0.8
MUTATION_CHANCE = 0.1   # chance that a child gets one random swap (0.1 = 10%)


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
# each member of the population is a pair: (score, list)
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
    """Return the population as (score, list) pairs."""
    scored_population = []
    for one_list in population:
        score = calculate_score(one_list, jobs)
        scored_population.append((one_list, score))

    return scored_population


# =====================================================================
# PART 4 - Tournament
# =====================================================================

def tournament(scored_population, rdm):
    """Pick TOURNAMENT_SIZE random members and return the list with the lowest score."""
    contestants = rdm.sample(scored_population, TOURNAMENT_SIZE)

    # start qith no winner yet and the score being infinity
    best_list = None
    best_score = float("inf")

    for one_list, score in contestants:
        if score < best_score:
            best_list = one_list
            best_score = score

    return best_list


def create_parents(scored_population, rdm):
    """Run one tournament per member of the population and return all the winners."""
    parents = []
    for _ in range(len(scored_population)):
        parents.append(tournament(scored_population, rdm))

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


def crossover(parent_1, parent_2, jobs, rdm):
    """Return 2 children: mixed (cut and swap, then repaired) or copies of the parents."""
    if rdm.random() < CROSSOVER_CHANCE:
        # cut both parents at the same random spot and swap the ends
        cut = rdm.randint(1, len(parent_1) - 1)
        child_1 = parent_1[:cut] + parent_2[cut:]
        child_2 = parent_2[:cut] + parent_1[cut:]

        repair(child_1, jobs)
        repair(child_2, jobs)
        return child_1, child_2

    # no crossover this time: children are copies of the parents
    return list(parent_1), list(parent_2)


def make_children(parents, jobs, rdm):
    """Pair the parents up (1st with 2nd, 3rd with 4th, ...) and return all their children."""
    children = []
    for pair_start in range(0, len(parents), 2):
        parent_1 = parents[pair_start]
        parent_2 = parents[pair_start + 1]
        child_1, child_2 = crossover(parent_1, parent_2, jobs, rdm)
        children.append(child_1)
        children.append(child_2)

    return children


# =====================================================================
# PART 6  - mutation
# =====================================================================

def mutate(child, rdm):
    """With MUTATION_CHANCE, swap the numbers at 2 random positions of the child."""
    if rdm.random() < MUTATION_CHANCE:
        first_position, second_position = rdm.sample(range(len(child)), 2)

        # swap: keep the first number aside so it isn't lost
        first_number = child[first_position]
        child[first_position] = child[second_position]
        child[second_position] = first_number


def mutate_children(children, rdm):
    """Give every child its chance to be mutated."""
    for child in children:
        mutate(child, rdm)


# ---- temporary test ----
def is_valid(one_list, jobs):
    """Check that every job appears exactly once per step."""
    for job_position, job_steps in enumerate(jobs):
        if one_list.count(job_position) != len(job_steps):
            return False
    return True


def main():
    """Temporary test of the parts written so far."""
    rdm = random.Random(SEED)
    jobs = load_jobs(CSV_FILE)
    population = whole_population(POPULATION_SIZE, jobs, rdm)

    ##### for step 1 #####
    print("number of jobs:", len(jobs))
    print("steps per job:", len(jobs[0]))

    ##### for step 2 #####
    print("number of lists:", len(population))
    print("length of one list:", len(population[0]))
    print("first 15 numbers of list 1:", population[0][:15])

    ##### for step 3 #####
    # the real data: one random list
    print("random list from real data time take for that list:",
          calculate_score(population[0], jobs))

    ##### for step 4 #####
    # real data: are winners better than average?
    scored_population = score_population(population, jobs)
    one_list, score = scored_population[0]
    print("irst 15 numbers and score of scored population:",
          one_list[:15], "score", score)
    total = 0
    for _, score in scored_population:
        total += score
    print("average score of population:", total / len(scored_population))
    for _ in range(5):
        winner = tournament(scored_population, rdm)
        print("sample winner score:", calculate_score(winner, jobs))

    ##### for step 5: real parents from 50 tournaments -> 50 children #####
    parents = create_parents(scored_population, rdm)
    children = make_children(parents, jobs, rdm)
    print("parents:", len(parents), " children:", len(children))

    # are all children valid (every job exactly 11 times)?
    valid_count = 0
    for child in children:
        if is_valid(child, jobs):
            valid_count += 1
    print("valid children:", valid_count, "out of", len(children))

    # compare average scores
    parents_total = 0
    for parent in parents:
        parents_total += calculate_score(parent, jobs)
    children_total = 0
    for child in children:
        children_total += calculate_score(child, jobs)
    print("average parent score:", parents_total / len(parents))
    print("average child score:", children_total / len(children))

    ##### for step 6: mutate the children and count how many changed #####
    children_before = []
    for child in children:
        # copies, to compare with afterwards
        children_before.append(list(child))

    mutate_children(children, rdm)

    changed_count = 0
    for before, after in zip(children_before, children):
        if before != after:
            changed_count += 1
    print("children changed by mutation:",
          changed_count, "out of", len(children))

    valid_count = 0
    for child in children:
        if is_valid(child, jobs):
            valid_count += 1
    print("valid children after mutation:",
          valid_count, "out of", len(children))


if __name__ == "__main__":
    main()
