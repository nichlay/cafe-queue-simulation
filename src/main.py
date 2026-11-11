"""
PROJECT: Cafe Queue Simulation

GOAL:
    Investigate the effect of cashier capacity on customer waiting times
    by simulating a cafe's customer queue.

    Compare two operating scenarios:
        1. One cashier
        2. Two cashiers

PROCESS:
    1. Generate customer arrival times.
    2. Generate customer service durations.
    3. Simulate the queue with one cashier.
    4. Simulate the queue with two cashiers.
    5. Calculate customer waiting times.
    6. Analyze and compare the results.
    7. Conduct sensitivity analysis under different demand conditions.
    8. Interpret the findings and evaluate the model.

OBJECTIVE:
    Understand how different cashier capacities affect the operational
    performance of a customer queue.

METHOD:
    Queue simulation using Python.

NOTE:
    All customer data and operational parameters are artificially
    generated for educational purposes. They are not observations
    collected from an actual cafe.
"""

import random
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


# global constants
NUM_CUSTOMERS = 100

MIN_INTERARRIVAL_TIME = 3
MAX_INTERARRIVAL_TIME = 6

MIN_SERVICE_TIME = 3
MAX_SERVICE_TIME = 5

RANDOM_SEED = 42
PREVIEW_ROWS = 10
LONG_WAIT_THRESHOLD = 5

# sensitivity analysis scenarios
DEMAND_SCENARIOS = {
    "Low demand": (5, 8),
    "Normal demand": (3, 6),
    "High demand": (1, 4),
}

# project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "results" / "figures"


def generate_arrival_times(
    num_customers: int, min_interarrival: int, max_interarrival: int
) -> list[int]:
    """
    Generate chronological arrival times for a specified number of customers.

    The first customer arrives at time zero. Each subsequent arrival time
    is calculated by adding a randomly generated interarrival interval
    to the previous customer's arrival time.

    Args:
        num_customers (int): Number of customers to generate. Must be at least 1.
        min_interarrival (int): Minimum interval between arrivals. Must be positive.
        max_interarrival (int): Maximum interval between arrivals. Must be
                                greater than or equal to min_interarrival.

    Returns:
        list[int]: Customer arrival times, measured in minutes.

    Raises:
        ValueError: If the customer count or interarrival bounds are invalid.
    """
    if num_customers < 1:
        raise ValueError("The number of customers must be at least one.")

    if min_interarrival < 1 or max_interarrival < min_interarrival:
        raise ValueError("Interarrival bounds must be positive and ordered.")

    arrival_times = [0]

    for _ in range(1, num_customers):
        interval = random.randint(min_interarrival, max_interarrival)
        next_arrival = arrival_times[-1] + interval
        arrival_times.append(next_arrival)

    return arrival_times


def generate_service_times(
    num_customers: int, min_service: int, max_service: int
) -> list[int]:
    """
    Generate random service durations for each customer.

    Each customer's service duration is independently generated as an
    integer within the specified inclusive range.

    Args:
        num_customers (int): Number of customers to generate. Must be at least 1.
        min_service (int): Minimum service duration. Must be positive.
        max_service (int): Maximum service duration. Must be greater than
                           or equal to min_service.

    Returns:
        list[int]: Customer service durations, measured in minutes.

    Raises:
        ValueError: If the customer count or service-time bounds are invalid.
    """
    if num_customers < 1:
        raise ValueError("The number of customers must be at least one.")

    if min_service < 1 or max_service < min_service:
        raise ValueError("Service-time bounds must be positive and ordered.")

    service_times = []

    for _ in range(num_customers):
        service = random.randint(min_service, max_service)
        service_times.append(service)

    return service_times


def generate_customer_data(
    num_customers: int,
    min_interarrival: int,
    max_interarrival: int,
    min_service: int,
    max_service: int,
) -> tuple[list[int], list[int]]:
    """
    Generate customer arrival times and service durations.

    This function coordinates the arrival-time and service-time generators
    and returns both datasets in corresponding customer order.

    Args:
        num_customers (int): Number of customers to generate.
        min_interarrival (int): Minimum interval between arrivals.
        max_interarrival (int): Maximum interval between arrivals.
        min_service (int): Minimum service duration.
        max_service (int): Maximum service duration.

    Returns:
        tuple[list[int], list[int]]: A pair containing arrival times and
                                     service durations. The values at the
                                     same index belong to the same customer.
    """
    arrival_times = generate_arrival_times(
        num_customers, min_interarrival, max_interarrival
    )
    service_times = generate_service_times(
        num_customers, min_service, max_service
    )

    return arrival_times, service_times


def simulate_queue(
    arrival_times: list[int], service_times: list[int], cashier_count: int
) -> list[dict[str, int]]:
    """
    Simulate customers moving through a shared queue served by cashiers.

    Customers are processed in arrival order and assigned to the cashier
    with the earliest next-available time. The function calculates each
    customer's service start, service completion, and waiting times, while
    updating the availability of the assigned cashier.

    Args:
        arrival_times (list[int]): Chronologically ordered customer arrival times.
        service_times (list[int]): Positive service durations corresponding to
                                   arrival_times.
        cashier_count (int): Number of cashiers. Must be a positive integer.

    Returns:
        list[dict[str, int]]: One record per customer, containing customer
                              number, assigned cashier, arrival time, service
                              duration, service start, service completion,
                              and waiting time.

    Raises:
        ValueError: If the input lists differ in length, arrival times are not
                    chronological or nonnegative, service durations are not
                    positive, or cashier_count is invalid.
    """
    if len(arrival_times) != len(service_times):
        raise ValueError("Arrival and service data must have equal lengths.")

    if (
        not isinstance(cashier_count, int)
        or isinstance(cashier_count, bool)
        or cashier_count < 1
    ):
        raise ValueError("Cashier count must be a positive integer.")

    if any(arrival < 0 for arrival in arrival_times):
        raise ValueError("Arrival times cannot be negative.")

    if any(
        arrival_times[i] > arrival_times[i + 1]
        for i in range(len(arrival_times) - 1)
    ):
        raise ValueError("Arrival times must be in chronological order.")

    if any(service <= 0 for service in service_times):
        raise ValueError("Service durations must be positive.")

    cashier_available = [0] * cashier_count
    simulation_results = []

    for i, (arrival, service) in enumerate(zip(arrival_times, service_times)):
        # Find the cashier with the earliest next-available time.
        # If there is a tie, list.index() selects the lowest cashier index.
        cashier_index = cashier_available.index(min(cashier_available))
        min_available_time = cashier_available[cashier_index]

        # A customer can start only after arriving and when the cashier is free.
        service_start = max(arrival, min_available_time)
        waiting_time = service_start - arrival
        service_finish = service_start + service

        # Update the selected cashier's next-available time.
        cashier_available[cashier_index] = service_finish

        # Store the outcome for this customer.
        record = {
            "customer": i + 1,
            "cashier": cashier_index + 1,
            "arrival": arrival,
            "service": service,
            "start": service_start,
            "finish": service_finish,
            "waiting": waiting_time,
        }
        simulation_results.append(record)

    return simulation_results


def display_customer_data(
    arrival_times: list[int], service_times: list[int], preview_rows: int = 10
) -> None:
    """
    Display a preview of generated customer arrival and service data.

    Args:
        arrival_times (list[int]): Customer arrival times.
        service_times (list[int]): Customer service durations.
        preview_rows (int, optional): Maximum number of customers to display.
                                      Defaults to 10.

    Returns:
        None

    Side effects:
        Prints a formatted customer-data table to the console.

    Raises:
        ValueError: If the input lists have different lengths or preview_rows
                    is negative.
    """
    if len(arrival_times) != len(service_times):
        raise ValueError("Arrival and service data must have equal lengths.")
    if preview_rows < 0:
        raise ValueError("Preview row count cannot be negative.")

    rows_to_display = min(preview_rows, len(arrival_times))

    print(f"{'Customer':<12}{'Arrival':>12}{'Service':>12}")
    print("-" * 36)

    for i in range(rows_to_display):
        print(f"{i + 1:<12}{arrival_times[i]:>12}{service_times[i]:>12}")

    print(f"\nShowing {rows_to_display} of {len(arrival_times)} customers.")


def display_simulation_results(
    results: list[dict[str, int]], preview_rows: int = 10
) -> None:
    """
    Display a preview of customer-level queue simulation records.

    Args:
        results (list[dict[str, int]]): Customer simulation records.
        preview_rows (int, optional): Maximum number of records to display.
                                      Defaults to 10.

    Returns:
        None

    Side effects:
        Prints customer assignment, arrival, service, and waiting details.

    Raises:
        ValueError: If preview_rows is negative.
    """
    if preview_rows < 0:
        raise ValueError("Preview row count cannot be negative.")

    rows_to_display = min(preview_rows, len(results))

    print(
        f"{'Customer':<10}"
        f"{'Cashier':>9}"
        f"{'Arrival':>9}"
        f"{'Service':>9}"
        f"{'Start':>9}"
        f"{'Finish':>9}"
        f"{'Waiting':>9}"
    )
    print("-" * 64)

    for record in results[:rows_to_display]:
        print(
            f"{record['customer']:<10}"
            f"{record['cashier']:>9}"
            f"{record['arrival']:>9}"
            f"{record['service']:>9}"
            f"{record['start']:>9}"
            f"{record['finish']:>9}"
            f"{record['waiting']:>9}"
        )

    print(f"\nTotal customers simulated: {len(results)}")
    print(f"Customers displayed: {rows_to_display}")


def calculate_statistics(
    results: list[dict[str, int]], long_wait_threshold: int = 5
) -> dict[str, float]:
    """
    Calculate statistical performance measurements from customer waiting times.

    The function calculates mean, median, maximum waiting time, and the
    percentage of customers waiting strictly longer than the threshold.

    Args:
        results (list[dict[str, int]]): Customer simulation records.
        long_wait_threshold (int, optional): Long-wait threshold in minutes.
                                             Defaults to 5.

    Returns:
        dict[str, float]: Average, median, maximum, and long-wait percentage.

    Raises:
        ValueError: If results are empty or the threshold is negative.
    """
    if not results:
        raise ValueError("Simulation results cannot be empty.")
    if long_wait_threshold < 0:
        raise ValueError("Long-wait threshold cannot be negative.")

    waiting_times = [record["waiting"] for record in results]

    average_wait = statistics.mean(waiting_times)
    median_wait = statistics.median(waiting_times)
    maximum_wait = max(waiting_times)

    long_wait_count = sum(
        waiting > long_wait_threshold for waiting in waiting_times
    )
    long_wait_percentage = (long_wait_count / len(waiting_times)) * 100

    return {
        "average_wait": float(average_wait),
        "median_wait": float(median_wait),
        "maximum_wait": float(maximum_wait),
        "long_wait_percentage": float(long_wait_percentage),
    }


def compare_scenarios(
    results_one: list[dict[str, int]], results_two: list[dict[str, int]]
) -> dict[str, dict[str, float]]:
    """
    Calculate and organize statistics for one-cashier and two-cashier scenarios.

    Args:
        results_one (list[dict[str, int]]): Results from one cashier.
        results_two (list[dict[str, int]]): Results from two cashiers.

    Returns:
        dict[str, dict[str, float]]: Performance measurements organized by
                                     operating scenario.

    Raises:
        ValueError: If the scenarios contain different numbers of customers.
    """
    if len(results_one) != len(results_two):
        raise ValueError("Both scenarios must contain equal customer counts.")

    statistics_one = calculate_statistics(results_one, LONG_WAIT_THRESHOLD)
    statistics_two = calculate_statistics(results_two, LONG_WAIT_THRESHOLD)

    return {
        "One cashier": statistics_one,
        "Two cashiers": statistics_two,
    }


def display_comparison(comparison: dict[str, dict[str, float]]) -> None:
    """
    Display statistical comparisons between the two cashier scenarios.

    Args:
        comparison (dict[str, dict[str, float]]): Statistics for each scenario.

    Returns:
        None

    Side effects:
        Prints a formatted comparison table to the console.
    """
    one = comparison["One cashier"]
    two = comparison["Two cashiers"]

    print("\nCUSTOMER WAITING TIME COMPARISON\n")
    print(f"{'Measurement':<30}{'One Cashier':>15}{'Two Cashiers':>15}")
    print("-" * 60)

    measurements = [
        ("Average waiting time (min)", "average_wait", "number"),
        ("Median waiting time (min)", "median_wait", "number"),
        ("Maximum waiting time (min)", "maximum_wait", "number"),
        ("Long waiting customers (%)", "long_wait_percentage", "percent"),
    ]

    for label, key, value_type in measurements:
        if value_type == "percent":
            one_value = f"{one[key]:.1f}%"
            two_value = f"{two[key]:.1f}%"
        else:
            one_value = f"{one[key]:.2f}"
            two_value = f"{two[key]:.2f}"

        print(f"{label:<30}{one_value:>15}{two_value:>15}")


def save_current_figure(filename: str) -> Path:
    """
    Save the currently active Matplotlib figure in the project figures folder.

    Args:
        filename (str): Image filename, including its extension.

    Returns:
        Path: Full path to the saved image file.

    Side effects:
        Creates the figures directory if it does not exist and saves
        the current figure as a high-resolution image.
    """
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_path = FIGURE_DIR / filename
    plt.savefig(figure_path, dpi=300, bbox_inches="tight")
    print(f"Saved figure: {figure_path.relative_to(PROJECT_ROOT)}")
    return figure_path


def plot_comparison(comparison: dict[str, dict[str, float]]) -> None:
    """
    Create and save charts comparing the two baseline cashier configurations.

    Creates separate charts for average waiting time and the percentage
    of customers waiting longer than the configured threshold.

    Args:
        comparison (dict[str, dict[str, float]]): Statistics for each scenario.

    Returns:
        None

    Side effects:
        Saves two PNG files and displays the charts.
    """
    scenarios = list(comparison.keys())

    average_waits = [
        comparison[scenario]["average_wait"] for scenario in scenarios
    ]

    plt.figure(figsize=(7, 5))
    plt.bar(scenarios, average_waits)
    plt.title("Average Customer Waiting Time")
    plt.xlabel("Operating Scenario")
    plt.ylabel("Average Waiting Time (Minutes)")
    plt.tight_layout()
    save_current_figure("baseline_average_wait.png")
    plt.show()
    plt.close()

    long_wait_percentages = [
        comparison[scenario]["long_wait_percentage"] for scenario in scenarios
    ]

    plt.figure(figsize=(7, 5))
    plt.bar(scenarios, long_wait_percentages)
    plt.title(f"Customers Waiting More Than {LONG_WAIT_THRESHOLD} Minutes")
    plt.xlabel("Operating Scenario")
    plt.ylabel("Customers (%)")
    plt.tight_layout()
    save_current_figure("baseline_long_wait.png")
    plt.show()
    plt.close()


def run_sensitivity_analysis() -> dict[str, dict[str, dict[str, float]]]:
    """
    Conduct queue simulations under low, normal, and high demand conditions.

    Each demand condition is tested with one and two cashiers. The random
    seed is reset for each condition. Since all interarrival ranges contain
    four possible integer values and each scenario generates the same number
    of arrivals, the scenarios use the same seeded service-time sequence.

    Args:
        None

    Returns:
        dict[str, dict[str, dict[str, float]]]: Statistics organized by
                                               demand and cashier scenario.
    """
    sensitivity_results = {}

    for scenario_name, (min_interarrival, max_interarrival) in DEMAND_SCENARIOS.items():
        random.seed(RANDOM_SEED)

        arrival_times, service_times = generate_customer_data(
            NUM_CUSTOMERS,
            min_interarrival,
            max_interarrival,
            MIN_SERVICE_TIME,
            MAX_SERVICE_TIME,
        )

        results_one = simulate_queue(arrival_times, service_times, cashier_count=1)
        results_two = simulate_queue(arrival_times, service_times, cashier_count=2)

        statistics_one = calculate_statistics(results_one, LONG_WAIT_THRESHOLD)
        statistics_two = calculate_statistics(results_two, LONG_WAIT_THRESHOLD)

        sensitivity_results[scenario_name] = {
            "One cashier": statistics_one,
            "Two cashiers": statistics_two,
        }

    return sensitivity_results


def display_sensitivity_results(
    sensitivity_results: dict[str, dict[str, dict[str, float]]],
) -> None:
    """
    Display performance measurements across all demand scenarios.

    Args:
        sensitivity_results (dict): Statistics for each demand and cashier
                                    configuration.

    Returns:
        None

    Side effects:
        Prints a comparison table for each demand condition.
    """
    print("\nSENSITIVITY ANALYSIS RESULTS\n")

    measurements = [
        ("Average waiting time", "average_wait", "min"),
        ("Median waiting time", "median_wait", "min"),
        ("Maximum waiting time", "maximum_wait", "min"),
        ("Long-wait percentage", "long_wait_percentage", "%"),
    ]

    for scenario_name, scenario_results in sensitivity_results.items():
        min_interarrival, max_interarrival = DEMAND_SCENARIOS[scenario_name]
        print(
            f"\n{scenario_name.upper()} "
            f"({min_interarrival}-{max_interarrival} minutes)\n"
        )
        print(f"{'Measurement':<30}{'One Cashier':>15}{'Two Cashiers':>15}")
        print("-" * 60)

        for label, key, unit in measurements:
            one_value = scenario_results["One cashier"][key]
            two_value = scenario_results["Two cashiers"][key]

            if unit == "%":
                one_display = f"{one_value:.1f}%"
                two_display = f"{two_value:.1f}%"
            else:
                one_display = f"{one_value:.2f}"
                two_display = f"{two_value:.2f}"

            print(f"{label:<30}{one_display:>15}{two_display:>15}")


def plot_sensitivity_analysis(
    sensitivity_results: dict[str, dict[str, dict[str, float]]],
) -> None:
    """
    Create and save a grouped bar chart of average waits across demand levels.

    Args:
        sensitivity_results (dict): Statistics for each demand and cashier
                                    configuration.

    Returns:
        None

    Side effects:
        Saves a PNG chart and displays it.
    """
    scenarios = list(sensitivity_results.keys())

    one_cashier_waits = [
        sensitivity_results[scenario]["One cashier"]["average_wait"]
        for scenario in scenarios
    ]
    two_cashier_waits = [
        sensitivity_results[scenario]["Two cashiers"]["average_wait"]
        for scenario in scenarios
    ]

    bar_width = 0.35
    positions = list(range(len(scenarios)))
    one_positions = [position - bar_width / 2 for position in positions]
    two_positions = [position + bar_width / 2 for position in positions]

    plt.figure(figsize=(9, 5))
    plt.bar(one_positions, one_cashier_waits, width=bar_width, label="One cashier")
    plt.bar(two_positions, two_cashier_waits, width=bar_width, label="Two cashiers")
    plt.title("Effect of Customer Demand on Waiting Time")
    plt.xlabel("Demand Scenario")
    plt.ylabel("Average Waiting Time (Minutes)")
    plt.xticks(positions, scenarios)
    plt.legend()
    plt.tight_layout()
    save_current_figure("sensitivity_average_wait.png")
    plt.show()
    plt.close()


def main() -> None:
    """
    Coordinate customer data generation, baseline experiments, and analysis.

    Generates one baseline customer dataset, runs one-cashier and
    two-cashier simulations using the same customers, presents the results,
    and then conducts sensitivity analysis under three demand conditions.

    Args:
        None

    Returns:
        None

    Side effects:
        Prints customer data and analysis results, displays charts, and
        saves the charts in results/figures/.
    """
    # Generate the baseline customer dataset once for both experiments.
    random.seed(RANDOM_SEED)
    arrival_times, service_times = generate_customer_data(
        NUM_CUSTOMERS,
        MIN_INTERARRIVAL_TIME,
        MAX_INTERARRIVAL_TIME,
        MIN_SERVICE_TIME,
        MAX_SERVICE_TIME,
    )

    print("\nGENERATED CUSTOMER DATA\n")
    display_customer_data(arrival_times, service_times, PREVIEW_ROWS)

    # Experiment A: one cashier.
    print("\nEXPERIMENT A: ONE CASHIER\n")
    results_one = simulate_queue(arrival_times, service_times, cashier_count=1)
    display_simulation_results(results_one, PREVIEW_ROWS)

    # Experiment B: two cashiers, using exactly the same customer dataset.
    print("\nEXPERIMENT B: TWO CASHIERS\n")
    results_two = simulate_queue(arrival_times, service_times, cashier_count=2)
    display_simulation_results(results_two, PREVIEW_ROWS)

    # Baseline statistical comparison and visualizations.
    comparison = compare_scenarios(results_one, results_two)
    display_comparison(comparison)
    plot_comparison(comparison)

    # Sensitivity analysis under different customer demand conditions.
    sensitivity_results = run_sensitivity_analysis()
    display_sensitivity_results(sensitivity_results)
    plot_sensitivity_analysis(sensitivity_results)

    print("\nProject run completed.")
    print(f"Figures are saved in: {FIGURE_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
