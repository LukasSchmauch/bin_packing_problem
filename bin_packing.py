# Frage: An welche Stelle wird welches Item getauscht?
# Hinweis: "Durch Serie von Moves wird p emptified" (laut paper) - ist bei BPP nicht moeglich
import random
import math
from pathlib import Path
from collections import namedtuple
import pandas as pd
import time

Item = namedtuple('Item', 'name capacity')

def read_instances(path):
    documents_path = Path(path)
    instances = []
    for document in documents_path.iterdir():
        with open(document) as f:
            content = f.readlines()
        instances.append([x.strip() for x in content])
    return instances

def generate_instance(instances):
    item_list = []
    bin_capacity = 0
    n_items = 0
    for i, item_capacity in enumerate(instances):
        if i == 0:
            n_items = int(item_capacity)
        elif i == 1:
            bin_capacity = int(item_capacity) 
        elif i > 1:
            item_list.append(Item(i-1,int(item_capacity)))
    print("Anzahl Items", n_items)
    print("Bin Kapazitaet", bin_capacity)
    lower_bound = math.ceil(sum(item.capacity for item in item_list)/ bin_capacity)
    print("Lower Bound", lower_bound)
    
    return item_list, n_items, bin_capacity, lower_bound 


def hill_climbing(item_list, bin_capacity, lower_bound):
    # (0) Konstruktionsverfahren: first fit descending
    solution = first_fit_descending(item_list, bin_capacity)
    best_solution = len(solution) # Loesung im Worst Case = FFD Loesung
    for i in range(0,1000):
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
        # (3b) Shuffle die Bins/Gruppen nach Heuristik/ Random
        shuffle(solution)
        # (3c) Rufe Greedy-Algorithmus mit permutierter Loesung aus (3b) auf
        # wichtig: Greedy benoetigt "flache Itemlist"
        solution = [item for bin in solution for item in bin]
        solution = greedy(solution, bin_capacity)
        if len(solution) < best_solution:
            best_solution = len(solution)
        if best_solution == lower_bound:
            return best_solution
    return best_solution

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
    # items zwischenspeichern
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
        solution = largest_first(solution)
    elif rnd_int <= 10:
        solution.reverse()
    else:
        random.shuffle(solution)

def largest_first(solution):
  sorted_dict = {}
  for i, bin in enumerate(solution):
    sorted_dict[i] = fullness(bin)
  sorted_dict = {k: v for k, v in sorted(sorted_dict.items(), reverse=True, key=lambda item: item[1])}
  shuffled_solution = [0] * len(solution)
  i = 0
  for index, capacity in sorted_dict.items():
    shuffled_solution[i] = solution[index]
    i = i +1 
  return shuffled_solution


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

def generate_results():
    
    #instances_falkenauer.append(read_triplet_instances_falkenauer)
    #Ergebnis DataFrame erstellen
    df_results = pd.DataFrame(columns = ['Typ','Anzahl Items','Bin-Kapazitaet','LB','Hill Climbing','First Fit Descending','Abs. LB HC', 'Abs. LB FFD', 'Zeit HC (sec)', 'Zeit FFD (sec)'])
    
    #instances_scholl1 = read_instances("Instanzen/Scholl/Scholl_1")
    #generate_results_of_instances(instances_scholl1, df_results, "scholl_1")

    instances_falkenauer_uniform = read_instances("Instanzen/Falkenauer/uniform")
    generate_results_of_instances(instances_falkenauer_uniform, df_results, "uniform")
    
    #instances_falkenauer_triplet = read_instances("Instanzen/Falkenauer/triplet")
    #generate_results_of_instances(instances_falkenauer_triplet, df_results, "triplet")

    df_results = df_results.sort_values(by=['Typ','Anzahl Items'])
    print(df_results.head(20))
    df_results.to_csv('results_unif_1000.csv',index=False, encoding='utf-8')
    df_grouped = df_results.groupby(['Typ', 'Anzahl Items'])
    df_mean = df_grouped.mean()
    #df_grouped.columns = ['Bin-Kapazitaet', ' Mean LB', 'Mean Hill Climbing', 'Mean First Fit Descending','Mean Abs. LB HC', 'Mean Abs. LB FFD', 'Mean Zeit HC (sec)', 'Mean Zeit FFD (sec)']
    print(df_mean.head())
    df_mean.to_csv('mean_results_1000.csv',index=False, encoding='utf-8')

def generate_results_of_instances(instances, df_results, typ):
    num_cols = df_results.shape[0]
    for i in range(0,len(instances)):
        item_list, n_items, bin_capacity, lower_bound  = generate_instance(instances[i])
        # Hill Climbing
        tic = time.perf_counter()
        bins_hc = hill_climbing(item_list, bin_capacity, lower_bound)
        toc = time.perf_counter()
        elapsed_time_hc = toc - tic
        # First Fit Descending
        tic = time.perf_counter()
        bins_firstfit = len(first_fit_descending(item_list, bin_capacity))
        toc = time.perf_counter()
        elapsed_time_ffd = toc - tic

        print("Anzahl Bins HC", bins_hc)
        print("Anzahl Bins FFD", bins_firstfit)
        print("-------------")
        df_results.loc[num_cols + i] = [typ, n_items, bin_capacity/1.0, lower_bound/1.0, bins_hc/1.0, bins_firstfit/1.0, (bins_hc - lower_bound)/1.0, (bins_firstfit-lower_bound)/1.0, round(elapsed_time_hc,2), round(elapsed_time_ffd,2)]


def main():

    generate_results()    

    return 0

if __name__ == '__main__':
    main()