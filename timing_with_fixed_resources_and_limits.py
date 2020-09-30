"""# Description of the experiment:
#
# - We generate the costs to up to 10.000 tasks for 100 resources.
# All costs follow linear functions with RNG seeds [0..99].
# - We schedule from 1.000 to 10.000 tasks with steps of 1000.
# - We run OLAR and the extended versions of Fed-LBAP, FedAvg, and
# Proportional.
# - All resources have a lower limit of 4, except the resource with the
# highest cost for the number of tasks. That resource gets a minimum of
# (tasks/resources)/4.
# - All resources have an upper limit of 2*(tasks/resources), except the
# resource with the lowest cost for the number of tasks. That resource
# gets an upper limit of (tasks/resources)/2.
# - Each sample is composed of 100 executions of the schedulers.
# - We get 50 samples for each pair (scheduler, tasks)
# - The order of execution of the different schedulers is
# randomly defined. We set an initial RNG seed = 0 and increase
# it every time we need a new order.
"""

import timeit
import numpy as np
import code.support as support

# File containing the results
logger = support.Logger('results_of_timing_with_fixed_resources_and_limits.csv')
min_tasks = 1000
max_tasks = 10001
step_tasks = 1000
size_of_sample = 100
number_of_samples = 50
shuffle_initial_seed = 10000
scheduler_name = ['Proportional', 'FedAvg', 'Fed-LBAP', 'OLAR']


def run_timing():
    # Stores the description of the experiments
    logger.header(__doc__)
    # Header of the CSV file
    logger.store('Scheduler,Tasks,Resources,Time')
    # Runs experiments for 100 resources
    run_for_fixed_resources()
    # Finishes logging
    logger.finish()


def run_for_fixed_resources():
    """
    Runs experiments for a fixed number of resources.
    """

    # counting the rounds of the experiment to update the RNG seed
    rounds = 0
    # runs experiments for all numbers of tasks
    for tasks in range(min_tasks, max_tasks, step_tasks):
        print(f'- Running experiments with {tasks} tasks')

        # sets the string to be used for each scheduler
        calls = []
        # version that verifies the results
        #calls.append(f"print(support.check_limits(schedulers.extended_proportional({tasks}, resources, cost, k, lower_limit, upper_limit), lower_limit, upper_limit))")
        #calls.append(f"print(support.check_limits(schedulers.extended_fedavg({tasks}, resources, lower_limit, upper_limit), lower_limit, upper_limit))")
        #calls.append(f"print(support.check_limits(schedulers.extended_fed_lbap({tasks}, resources, cost, lower_limit, upper_limit), lower_limit, upper_limit))")
        #calls.append(f"print(support.check_limits(schedulers.olar({tasks}, resources, cost, lower_limit, upper_limit), lower_limit, upper_limit))")
        # version that does not verify the results
        calls.append(f"a = schedulers.extended_proportional({tasks}, resources, cost, k, lower_limit, upper_limit)")
        calls.append(f"a = schedulers.extended_fedavg({tasks}, resources, lower_limit, upper_limit)")
        calls.append(f"a = schedulers.extended_fed_lbap({tasks}, resources, cost, lower_limit, upper_limit)")
        calls.append(f"a = schedulers.olar({tasks}, resources, cost, lower_limit, upper_limit)")

        # Setup to generate 100 resources with 10001 costs
        avg_tasks = tasks // 100
        setup = f"""
import numpy as np
import code.schedulers as schedulers
import code.devices as devices
import code.support as support

rng_seed_resources = 0
tasks = 10000
resources = 100
k = 1
# Initializes the cost matrix with zeros
cost = np.zeros(shape=(resources, tasks+1))
# Fills the cost matrix with costs based on a linear function
base_seed = rng_seed_resources
for i in range(resources):
    devices.create_linear_costs(base_seed, cost, i, tasks)
    base_seed += 1
lower_limit = np.full(shape=resources, fill_value=4)
upper_limit = np.full(shape=resources, fill_value={avg_tasks}*2)
# Finds the resource with the maximum and minimum costs for 'tasks'
max_index = np.argmax(cost[:, tasks])
lower_limit[max_index] = {avg_tasks} // 4
min_index = np.argmin(cost[:, tasks])
upper_limit[min_index] = {avg_tasks} // 2
"""

        # gathers all samples for a given (number of tasks, scheduler)
        for sample in range(number_of_samples):
            # sets the RNG seed and generates an order of execution
            np.random.seed(shuffle_initial_seed + rounds)
            rounds += 1
            order = np.arange(4)  # four different schedulers
            np.random.shuffle(order)  # random order

            # gathers samples for all schedulers
            for i in order:
                # gathers one sample
                timing = timeit.timeit(setup=setup,
                                       stmt=calls[i],
                                       number=size_of_sample)
                # stores the timing information
                logger.store(f'{scheduler_name[i]},{tasks},100,{timing}')


if __name__ == '__main__':
    run_timing()
