import pulp
import csv

# Initialize the problem
problem = pulp.LpProblem("Weekend_Work_Schedule_Adjusted", pulp.LpMinimize)

# Employees and weekends
employees = ['A', 'B', 'C', 'D']
# Assume a 52-week year for simplicity; adjust as needed for leap years or specific calendar considerations
weekends = range(1, 53)

# Define 2 agent weekends
month_weekend_mapping = {
    'april': [r for r in range(14, 18)],  # Assuming April covers weekends 14 to 17
    'may': [r for r in range(18, 22)],
    'october': [r for r in range(40, 44)],
    'november': [r for r in range(44, 48)],
    'december': [r for r in range(48, 52)],
    'january_first_weekend': [1]  # The first weekend of January
}

two_people_weekends = []

for value in month_weekend_mapping.values():
    two_people_weekends.extend(value)

# Decision variables
# x[i][j] is 1 if employee i works on weekend j, 0 otherwise
x = pulp.LpVariable.dicts("work",
                          [(i, j) for i in employees for j in weekends],
                          cat='Binary')

# Constraint: Each weekend must be covered by at least one employee
for j in weekends:
    if j in two_people_weekends:
        problem += pulp.lpSum(x[(i, j)] for i in employees) == 2, f"Weekend_coverage_{j}"
    else:
        problem += pulp.lpSum(x[(i, j)] for i in employees) == 1, f"Weekend_coverage_{j}"

# Additional constraints for employee D
# To model the constraint that D must work one weekend and then have three weekends off,
# we use a modified approach to consider each 16-week cycle for D's scheduling
for start in range(1, 53, 16):  # Start of each 16-week cycle
    # D works exactly once in each 16-week cycle
    problem += pulp.lpSum(x[('D', j)] for j in range(start, min(start + 16, 53))) == 1, f"D_work_pattern_{start}"

# Assume x is your decision variable dictionary from before

# Constraint to minimize the difference in total weekends worked between A, B, and C
total_weekends_worked = {employee: pulp.lpSum(x[(employee, j)] for j in weekends) for employee in ['A', 'B', 'C']}

# Assuming we want the difference in total weekends worked to be as small as possible,
# we do not have a specific maximum difference in mind, let's say it's 1 for a tight balance
# Note: Depending on the total number of weekends and specific constraints, a difference of 1 might not be feasible
# You might need to adjust this threshold based on the feasibility of your problem

for employee1 in ['A', 'B', 'C']:
    for employee2 in ['A', 'B', 'C']:
        if employee1 != employee2:
            problem += (total_weekends_worked[employee1] - total_weekends_worked[employee2] <= 1), f"Balance_{employee1}_{employee2}_max"
            problem += (total_weekends_worked[employee1] - total_weekends_worked[employee2] >= -1), f"Balance_{employee1}_{employee2}_min"


# Solve the problem
problem.solve()

# Check if the problem was solved successfully
if pulp.LpStatus[problem.status] == 'Optimal':
    # Extract the results
    results = []
    for employee in employees:
        for weekend in weekends:
            if pulp.value(x[(employee, weekend)]) == 1:
                results.append({'Employee': employee, 'Weekend': weekend})
else:
    print("No optimal solution found.")

# Define the CSV file name
csv_file = 'scheduling_results.csv'

# Write the results to the CSV file
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ['Employee', 'Weekend']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write the rows
    for row in results:
        writer.writerow(row)

print(f"Scheduling results have been saved to {csv_file}")