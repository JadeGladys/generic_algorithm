import random
import csv
import time
from genetic_algorithm import CSV_FILE, load_jobs, genetic_algorithm

# SETTINGS - numbers you choose yourself
BASE_SEED = 42
NUMBER_OF_RUNS = 5      # how many runs per setting (seed per each)

DEFAULT_SETTINGS = {
    "population_size": 50,      # number of lists at a time (keep it even)
    "generations": 500,         # how many times we repeat: score -> parents -> children
    "tournament_size": 2,       # how many parents we compare during a tournament
    "crossover_chance": 0.8,    # how often two parents are mixed (0.8 = 80%)
    "mutation_chance": 0.1,     # chance that a child gets one swap (0.1 = 10%)
}

# for each setting: the values to try (all other settings stay at their default)
EXPERIMENTS = {
    "population_size": [20, 50, 100],         # keep them even
    "generations": [100, 500, 1000],
    "tournament_size": [2, 3, 5],
    "crossover_chance": [0.6, 0.8, 1.0],
    "mutation_chance": [0.01, 0.1, 0.3],
}

# pairs of settings to change together; every combination of their EXPERIMENTS values is tried
COMBINATIONS = [
    ("population_size", "crossover_chance"),
    ("population_size", "mutation_chance"),
    ("tournament_size", "mutation_chance"),
]

COMBINATIONS_FILE = "ga_combinations.csv"

RESULTS_FILE = "ga_results.csv"


def run_with_seeds(jobs, settings):
    """Run the GA once per seed; return the seeds used, the best score of each run,
    and how long each run took."""
    seeds_used = []
    best_scores = []
    best_lists = []
    run_times = []

    for n in range(NUMBER_OF_RUNS):
        seed = BASE_SEED + n
        # a fresh random generator for this run
        rdm = random.Random(seed)

        start_time = time.perf_counter()
        best_list, best_score, _ = genetic_algorithm(jobs, settings, rdm)
        run_times.append(time.perf_counter() - start_time)

        seeds_used.append(seed)
        best_scores.append(best_score)
        best_lists.append(best_list)

    return seeds_used, best_scores, best_lists, run_times


def run_one_experiment(jobs, changed_setting, settings):
    """Run these settings with every seed and return the result
    (what changed, all settings, score per seed, average, time)."""
    print("running", changed_setting, "with", settings, "...")

    seeds_used, best_scores, best_lists, run_times = run_with_seeds(
        jobs, settings)

    # store each score under its seed
    score_per_seed = {}
    list_per_seed = {}

    for seed, best_score, best_list in zip(seeds_used, best_scores, best_lists):
        score_per_seed[seed] = best_score
        list_per_seed[seed] = best_list

    return {
        "changed_setting": changed_setting,   # which setting(s) changed
        "settings": settings,                 # ALL the settings used
        "score_per_seed": score_per_seed,     # {42: 2153, 43: 2223, ...}
        "list_per_seed": list_per_seed,
        "average": sum(best_scores) / len(best_scores),
        "average_time": sum(run_times) / len(run_times),
    }


def run_experiments(jobs):
    """Change one setting at a time, run each value with every seed,
    and return one result per value."""
    results = []

    for setting_name, values in EXPERIMENTS.items():
        for value in values:
            # copy the defaults, then change only this one setting
            settings = dict(DEFAULT_SETTINGS)
            settings[setting_name] = value

            results.append(run_one_experiment(jobs, setting_name, settings))

    return results


def run_combinations(jobs):
    """For each pair in COMBINATIONS, try every combination of their values
    (all other settings stay at their default) and return one result per combination."""
    results = []

    for first_setting, second_setting in COMBINATIONS:
        for first_value in EXPERIMENTS[first_setting]:
            for second_value in EXPERIMENTS[second_setting]:
                # copy the defaults, then change both settings of the pair
                settings = dict(DEFAULT_SETTINGS)
                settings[first_setting] = first_value
                settings[second_setting] = second_value

                changed_setting = first_setting + " + " + second_setting
                results.append(run_one_experiment(
                    jobs, changed_setting, settings))

    return results


def save_results(results, file_name):
    """Write one row per experiment to a CSV file."""
    seeds = list(results[0]["score_per_seed"].keys())

    # column names
    header = ["changed_setting"]
    for setting_name in DEFAULT_SETTINGS:
        header.append(setting_name)
    for seed in seeds:
        header.append("seed_" + str(seed))
        header.append("best_list_seed_" + str(seed))
    header.append("average")
    header.append("average_time_s")

    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for result in results:
            row = [result["changed_setting"]]
            for setting_name in DEFAULT_SETTINGS:
                row.append(result["settings"][setting_name])
            for seed in seeds:
                row.append(result["score_per_seed"][seed])
                row.append(result["list_per_seed"][seed])
            row.append(round(result["average"], 1))
            row.append(round(result["average_time"], 2))
            writer.writerow(row)


def main():
    """Run all the experiments, and save it to a CSV file."""
    jobs = load_jobs(CSV_FILE)

    results = run_experiments(jobs)
    save_results(results, RESULTS_FILE)
    print("saved all results to", RESULTS_FILE)

    combination_results = run_combinations(jobs)
    save_results(combination_results, COMBINATIONS_FILE)
    print("saved combination results to", COMBINATIONS_FILE)


if __name__ == "__main__":
    main()
