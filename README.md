# Café Queue Simulation

An introductory **Operations Research (OR)** project that uses Python to study how cashier capacity affects customer waiting times in a café.

## Project Overview

This project models a simplified café queue and compares two operating configurations:

- **Scenario A:** one cashier serves customers.
- **Scenario B:** two cashiers serve customers through one shared queue.

Artificial customer arrival times and service durations are generated, then passed through a queue simulation. The resulting waiting times are summarized using basic statistics. A sensitivity analysis also examines how the results change when customer arrivals become less or more frequent.

**Main question:** How does increasing cashier capacity from one cashier to two affect customer waiting times under different demand conditions?

The project demonstrates a basic OR workflow: identify an operational question, represent it with a mathematical model, implement and experiment with that model, analyze the results, and discuss what they mean for a decision.

## Model at a Glance

The simulation uses the following baseline assumptions:

| Setting | Baseline value |
|---|---:|
| Number of customers | 100 |
| First customer arrival | Minute 0 |
| Interarrival interval | Random integer from 3 to 6 minutes |
| Service duration | Random integer from 3 to 5 minutes |
| Cashier configurations | 1 cashier and 2 cashiers |
| Queue arrangement | One shared queue; customers are processed in arrival order |
| Long-wait threshold | More than 5 minutes |
| Random seed | 42 |

For each customer, the model records their arrival time, assigned cashier, service start time, service completion time, and waiting time.

The key waiting-time relationship is:

$$
W_i = B_i - A_i
$$

where \(W_i\) is the waiting time of customer \(i\), \(B_i\) is the time their service begins, and \(A_i\) is their arrival time. The detailed mathematical formulation, notation, and explanation of the remaining equations are provided in the technical documentation.

## How to Run

### Prerequisites

- Python 3.9 or later
- Matplotlib

### Installation

From the repository's root directory, install Matplotlib:

```bash
python -m pip install matplotlib
```

### Run the program

```bash
python src/main.py
```

The program generates customer data, runs the one-cashier and two-cashier baseline experiments, calculates performance statistics, conducts the sensitivity analysis, and saves the charts in `results/figures/`.

## Project Structure

```text
cafe-queue-simulation/
├── README.md
├── src/
│   └── main.py
└── results/
    └── figures/
        ├── baseline_average_wait.png
        ├── baseline_long_wait.png
        └── sensitivity_average_wait.png
```

## Technical Documentation

Soon to be uploaded. 

## Scope and Limitations

This is an educational simulation using artificially generated data. It assumes that customers do not abandon the queue, cashiers have identical service-time behavior, and there are no breaks or service interruptions. It does not include labor costs, revenue, or customer-loss data, so it cannot determine whether hiring another cashier is financially worthwhile.

The results should therefore be interpreted as a comparison of queue performance under the stated assumptions, not as a staffing recommendation for a real café.
