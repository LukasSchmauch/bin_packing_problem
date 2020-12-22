# Frage: An welche Stelle wird welches Item getauscht?
# Hinweis: Durch Serie von Moves wird p emptified ist nicht moeglich
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
    for i, item_capacity in enumerate(instances_falkenauer[7]):
        if i == 1:
            bin_capacity = int(item_capacity) 
        elif i > 1:
            item_list.append(Item(i-1,int(item_capacity)))
    return item_list, bin_capacity

def hill_climbing(item_list, bin_capacity):
    # (0) Konstruktionsverfahren: first fit descending
    solution = first_fit_descending(item_list, bin_capacity)
    for i in range(0,10):
        # (1) Teilmenge aus Loesung bildet Permutationsgruppe
        permutation = []
        probability = 1/len(solution)
        while len(permutation) == 0:
            for i, bin in enumerate(solution):
                if random.uniform(0,1) <= probability:
                    permutation.append(solution[i])
                    solution.pop(i)
        
        # (2) Improvement procedure
        change = [True]
        while change[0]: 
            solution, permutation = bpp_improvement_procedure(solution, permutation, bin_capacity, change)

        # (3a) fuege die permutationsgruppen der bisherigen Loesung hinzu
        for bin in permutation:
            solution.append(bin)
        # (3b) Shuffle die Bins/Gruppen 
        shuffle(solution)
        # (3c) Rufe Greedy-Algorithmus mit permutierter Loesung aus (3b) auf
        # wichtig: Greedy benoetigt "flache Itemlist"
        solution = [item for bin in solution for item in bin]
        solution = greedy(solution, bin_capacity)

    return solution

def bpp_improvement_procedure(solution, permutation, bin_capacity, change):
    change[0] = False
    for g in range(0,len(solution)):
        # 2:2 Swap
        for i in range(0,len(solution[g])):
            for j in range(0, len(solution[g])):
                if i != j and j > i:
                    for h in range(0,len(permutation)):
                        for k in range(0,len(permutation[h])):
                            for l in range(0,len(permutation[h])):
                                if k != l and l > k:
                                    delta = size(permutation[h][k]) + size(permutation[h][l]) - size(solution[g][i])- size(solution[g][j])
                                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                                        move(i,j, permutation[h], k, l, solution[g])
                                        change[0] = True
        # 2:1 Swap
        i = 0
        j = 0
        K = 0
        while i < len(solution[g]):
            while j < len(solution[g]):
                if i != j and j > i:
                    for h in range(0,len(permutation)):
                        while k < len(permutation[h]):
                            delta = size(permutation[h][k]) - size(solution[g][i]) - size(solution[g][j])
                            if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                                move2(i,j,permutation[h], k, solution[g])
                                change[0] = True
                                k -= 1
                                j -= 1
                            k += 1
                j += 1
            i += 1
        #1:1 Swap
        i = 0
        k = 0
        for i in range(0,len(solution[g])):
            for h in range(0,len(permutation)):
                for k in range(0,len(permutation[h])):
                    delta = size(permutation[h][k]) - size(solution[g][i])
                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                        move3(i, permutation[h], k, solution[g])
                        change[0] = True

    return solution, permutation

def size(item):
    return item.capacity

def move(i,j, bin_p, k, l, bin):
    # items behalten
    item_i = bin[i]
    item_j = bin[j]
    # Value wird kopiert (keine Referenz!)
    bin[i] = bin_p[k]
    bin[j] = bin_p[l]
    bin_p[k] = item_i
    bin_p[l] = item_j

def move2(i,j, bin_p, k, bin):
    # items behalten
    item_i = bin[i]
    item_j = bin[j]
    item_k = bin_p[k]
    bin[i] = item_k
    bin.pop(j)
    bin_p.append(item_i)
    bin_p.append(item_j)

def move3(i, bin_p, k, bin):
    item_i = bin[i]
    bin[i] = bin_p[k]
    bin_p[k] = item_i




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

def shuffle(solution):
    rnd_int = random.randint(1,13)
    if rnd_int <= 5:
        solution.reverse()
    elif rnd_int <= 10:
        solution.reverse()
    else:
        random.shuffle(solution)


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
    sol_vec = []
    for i in range(0,100):
        solution = hill_climbing(item_list, bin_capacity)
        sol_vec.append(len(solution))
    
    mean = (sum(sol_vec)/len(sol_vec))
    print(mean)

    print(len(first_fit_descending(item_list, bin_capacity)))


    return 0

if __name__ == '__main__':
    main()