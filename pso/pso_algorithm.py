# the search area from the assignment: x and y in <-4.5, 4.5>
LOWER_LIMIT = -4.5
UPPER_LIMIT = 4.5

# starting velocities are random between -START_SPEED and START_SPEED
START_SPEED = 1.0

# =====================================================================
# PART 1 - The function we want to minimise
# =====================================================================


def calculate_f(x, y):
    """Return f(x, y). Smaller is better."""
    f_value = ((1.5 - x - x * y) ** 2
               + (2.25 - x + x * y ** 2) ** 2
               + (2.625 - x + x * y ** 3) ** 2)
    return f_value


# =====================================================================
# PART 2 - Create the swarm that conations a list of particles
# a dictionary: where it is, how it moves, and its best spot so far
# =====================================================================

def create_particle(rdm):
    """Return one particle at a random spot, with a small random velocity."""
    x = rdm.uniform(LOWER_LIMIT, UPPER_LIMIT)
    y = rdm.uniform(LOWER_LIMIT, UPPER_LIMIT)
    velocity_x = rdm.uniform(-START_SPEED, START_SPEED)
    velocity_y = rdm.uniform(-START_SPEED, START_SPEED)
    value = calculate_f(x, y)

    return {
        "position": (x, y),
        "velocity": (velocity_x, velocity_y),
        "value": value,
        # its best spot so far = where it starts (it has not been anywhere else yet)
        "best_position": (x, y),
        "best_value": value,
    }


def create_swarm(number_of_particles, rdm):
    """Return a list of number_of_particles random particles."""
    swarm = []
    for _ in range(number_of_particles):
        swarm.append(create_particle(rdm))
    return swarm


def find_global_best(swarm):
    """Return the best spot any particle has found: best_position, best_value."""
    best_position = None
    best_value = float("inf")

    for particle in swarm:
        if particle["best_value"] < best_value:
            best_position = particle["best_position"]
            best_value = particle["best_value"]

    return best_position, best_value


# =====================================================================
# PART 3 - Move one particle
# new velocity and new position
# =====================================================================

def move_particle(particle, global_best_position, w, c1, c2, rdm):
    """Move one particle one step and update its best spot if the new spot is better."""
    x, y = particle["position"]
    velocity_x, velocity_y = particle["velocity"]
    best_x, best_y = particle["best_position"]
    global_best_x, global_best_y = global_best_position

    # random numbers between 0 and 1
    r1 = rdm.random()
    r2 = rdm.random()

    # new velocity, once for x and once for y
    new_velocity_x = (w * velocity_x
                      + c1 * r1 * (best_x - x)
                      + c2 * r2 * (global_best_x - x))
    new_velocity_y = (w * velocity_y
                      + c1 * r1 * (best_y - y)
                      + c2 * r2 * (global_best_y - y))

    # move, and stay inside the area (a particle past the edge is put back on the edge)
    new_x = min(max(x + new_velocity_x, LOWER_LIMIT), UPPER_LIMIT)
    new_y = min(max(y + new_velocity_y, LOWER_LIMIT), UPPER_LIMIT)

    particle["position"] = (new_x, new_y)
    particle["velocity"] = (new_velocity_x, new_velocity_y)
    particle["value"] = calculate_f(new_x, new_y)

    # better than its best so far? then this is its new best
    if particle["value"] < particle["best_value"]:
        particle["best_position"] = particle["position"]
        particle["best_value"] = particle["value"]


# =====================================================================
# PART 4 - The PSO loop
#   each iteration: move every particle, and update gbest whenever one finds a better spot
# =====================================================================

def particle_swarm_optimization(settings, rdm):
    """Run PSO with the given settings. Return the best position found, its f value,
    and the best f value after each iteration."""
    swarm = create_swarm(settings["number_of_particles"], rdm)
    global_best_position, global_best_value = find_global_best(swarm)
    best_value_per_iteration = []

    for _ in range(settings["iterations"]):
        for particle in swarm:
            move_particle(particle, global_best_position,
                          settings["w"], settings["c1"], settings["c2"], rdm)

            # did this particle find a spot better than the group's best?
            if particle["best_value"] < global_best_value:
                global_best_position = particle["best_position"]
                global_best_value = particle["best_value"]

        best_value_per_iteration.append(global_best_value)

    return global_best_position, global_best_value, best_value_per_iteration
