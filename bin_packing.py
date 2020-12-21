import random
from pathlib import Path
from collections import namedtuple

Item = namedtuple('Item', 'name capacity')

def generate_instances():
    documents_path = Path("Falkenauer/uniform")
    instances_falkenauer = []
    for document in documents_path.iterdir():
        with open(document) as f:
            content = f.readlines()
        instances_falkenauer.append([x.strip() for x in content])

    item_list = []
    bin_capacity = 0
    for i, item_capacity in enumerate(instances_falkenauer[1]):
        if i == 1:
            bin_capacity = int(item_capacity) 
        elif i > 1:
            item_list.append(Item(i-1,int(item_capacity)))
    return item_list, bin_capacity

def hill_climbing(item_list, bin_capacity):
    solution = first_fit_descending(item_list, bin_capacity)
    return solution

def first_fit_descending(item_list, bin_capacity):
    item_list = sorted(item_list, reverse = True, key = lambda i: i.capacity)
    return greedy(item_list, bin_capacity)

def greedy(item_list, bin_capacity):
    groups = [[]]
    for i, item in enumerate(item_list):
        j = 0
        found = False
        while not found and j <= len(groups) - 1:
            if is_feasible(item.capacity, bin_capacity, groups[j]):
                groups[j].append(item)
                found = True
            else:
                j +=1
        if not found:
            groups.append([item])
    return groups

def is_feasible(item_capacity, bin_capacity, current_bin):
    if (bin_capacity - fullness(current_bin) - item_capacity) >= 0:
        return True
    else:
        return False

def fullness(bin):
    if len(bin) == 0:
        return 0
    else:
        return sum(item.capacity for item in bin)

def print_solution(solution, name):
    print(name)
    #print("Loesung: ", solution)
    print("Anzahl Gruppen: ", len(solution))

def main():
    item_list, bin_capacity = generate_instances()
    solution = hill_climbing(item_list, bin_capacity)
    print_solution(solution, "greedy")


    return 0

if __name__ == '__main__':
    main()