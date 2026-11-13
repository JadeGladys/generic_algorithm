import csv
import random
import time

from pso.pso_algorithm import particle_swarm_optimization

# SETTINGS - numbers you choose yourself
BASE_SEED = 42
NUMBER_OF_RUNS = 5       # how many runs per setting (one seed each)

# gbest counts as 'settled' once it is this close to its final value
SETTLED_TOLERANCE = 0.000001

PARTICLE_COUNTS = [5, 30, 100]
ITERATION_COUNTS = [20, 100, 300]
W_VALUES = [0.3, 0.7, 1.0]
C1_VALUES = [0.5, 1.5, 2.5]
C2_VALUES = [0.5, 1.5, 2.5]

RESULTS_FILE = "pso_results.csv"


def iterations_needed(best_value_per_iteration, best_value):
    """Return the iteration after which gbest stopped improving"""
    for index, value in enumerate(best_value_per_iteration):
        if value - best_value < SETTLED_TOLERANCE:
            return index + 1        # index 0 = after iteration 1
    return len(best_value_per_iteration)


def run_with_seeds(settings):
    """Run PSO once per seed; return the seeds used, the best f of each run,
    the iterations each run needed, and how long each run took."""
    seeds_used = []
    best_positions = []
    best_values = []
    iterations = []
    run_times = []

    for run_number in range(NUMBER_OF_RUNS):
        seed = BASE_SEED + run_number
        rdm = random.Random(seed)       # a fresh random generator for this run

        start_time = time.perf_counter()
        best_position, best_value, best_value_per_iteration = particle_swarm_optimization(
            settings, rdm)
        run_times.append(time.perf_counter() - start_time)

        seeds_used.append(seed)
        best_positions.append(best_position)
        best_values.append(best_value)
        iterations.append(iterations_needed(
            best_value_per_iteration, best_value))

    return seeds_used, best_positions, best_values, iterations, run_times


def run_experiments():
    """Run every combination of the setting values with every seed, and return one result per combination."""
    results = []

    # one loop per setting: every value of each setting meets every value of the others
    for number_of_particles in PARTICLE_COUNTS:
        for number_of_iterations in ITERATION_COUNTS:
            for w in W_VALUES:
                for c1 in C1_VALUES:
                    for c2 in C2_VALUES:
                        settings = {
                            "number_of_particles": number_of_particles,
                            "iterations": number_of_iterations,
                            "w": w,
                            "c1": c1,
                            "c2": c2,
                        }
                        print("running", settings, "...")
                        seeds_used, best_positions, best_values, needed_iterations, run_times = \
                            run_with_seeds(settings)

                        results.append({
                            "settings": settings,
                            "seeds": seeds_used,
                            "best_positions": best_positions,
                            "best_values": best_values,
                            "iterations": needed_iterations,
                            "run_times": run_times,
                        })

    return results


def save_results(results, file_name):
    """Write one row per experiment to a CSV file: all settings,
    best f per seed, iterations per seed, and the averages."""
    # column names
    header = ["number_of_particles", "iterations", "w", "c1", "c2"]
    for seed in results[0]["seeds"]:
        header.append("best_position_seed_" + str(seed))
        header.append("best_f_value_seed_" + str(seed))
        header.append("iterations_needed_seed_" + str(seed))
    header += ["average_best_f", "average_iterations_needed", "average_time_s"]

    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)

        for result in results:
            settings = result["settings"]
            row = [settings["number_of_particles"], settings["iterations"],
                   settings["w"], settings["c1"], settings["c2"]]

            # each seed's run, side by side
            for best_position, best_value, needed_iterations in zip(
                    result["best_positions"], result["best_values"], result["iterations"]):
                best_x, best_y = best_position
                row.append((round(best_x, 6), round(best_y, 6)))
                row.append(round(best_value, 6))
                row.append(needed_iterations)

            # averages over the seeds
            row.append(
                round(sum(result["best_values"]) / len(result["best_values"]), 6))
            row.append(
                round(sum(result["iterations"]) / len(result["iterations"]), 1))
            row.append(
                round(sum(result["run_times"]) / len(result["run_times"]), 3))
            writer.writerow(row)


def main():
    """Run all the experiments and save them to a CSV file."""
    results = run_experiments()
    save_results(results, RESULTS_FILE)
    print("saved all results to", RESULTS_FILE)


if __name__ == "__main__":
    main()
