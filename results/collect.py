import glob

categories = {}

simulation_line = 3 if input("For MCTS: 1  For Q-Learning: 2") == "1" else 2

for file_name in glob.glob("*.txt"):
    category = file_name.split("-")[0]

    # Remove last 7 characters
    category = category[4:-7]
    print(category)

    if category not in categories:
        categories[category] = []

    with open(file_name, "r") as f:
        simulations = 0
        results = ""
        line_n = 0
        
        for line in f.readlines():
            if line_n == simulation_line:
                simulations = int(line[18:])
            if line_n == 5:
                results = line.split(",")
                
            line_n += 1
        
        print(simulations)
        print(results)

    data = [simulations] + results
    categories[category].append(data)

# Sort array
def takeSecond(elem):
    return elem[0]

for category, val in categories.items():
    val.sort(key=takeSecond)

    import csv

    with open("{}.csv".format(category), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(val)
        
print(categories)
