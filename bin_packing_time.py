# Frage: An welche Stelle wird welches Item getauscht?
# Hinweis: "Durch Serie von Moves wird p emptified" (laut paper) - ist bei BPP nicht moeglich
import random
import math
from pathlib import Path
from collections import namedtuple
import pandas as pd
import time

Item = namedtuple('Item', 'name capacity') # ermoeglicht Zugriff ueber Item.name und Item.capacity

# Einlesen der Textdokumente 
def read_instances(path):
    documents_path = Path(path)
    instances = []
    for document in documents_path.iterdir():
        with open(document) as f:
            content = f.readlines()
        instances.append([x.strip() for x in content])
    return instances

# Generieren der Instanz aus Textdokument
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

# Das Verbesserungsverfahren
def hill_climbing(item_list, bin_capacity, lower_bound,typ, n_items, df_results, instance_index):

    tic = time.perf_counter() # Starte Zeitmessung

    # (0) Konstruktionsverfahren: first fit descending
    solution = first_fit_descending(item_list, bin_capacity)
    iters = 0
    # Anzahl der Iterationen ist je nach gewuenschter Loesungsguete und vorhandener Rechenzeit festzulegen
    while (time.perf_counter() - tic <= 100):
        iters += 1
    #for iters in range(0,500):
        # (1) Teilmenge aus Loesung bildet Permutationsgruppe
        permutation = []
        solution, permutation = random_permutation(solution, permutation)
        #solution, permutation = permutation_by_heuristic(solution,permutation)

        # (2) Improvement procedure
        change = [True]
        while change[0] and time.perf_counter() - tic <= 100: 
            solution, permutation = bpp_improvement_procedure(solution, permutation, bin_capacity, change)
            #test_feasibility(permutation,bin_capacity)
            #test_feasibility(solution,bin_capacity)

        # (3a) fuege die permutationsgruppen der bisherigen Loesung hinzu
        for bin in permutation:
            solution.append(bin)

        ##### Test
        #test_feasibility(solution,bin_capacity)
        #####    

        # (3b) Shuffle die Bins/Gruppen nach Heuristik/ Random
        shuffle(solution)
        # (3c) Rufe Greedy-Algorithmus mit permutierter Loesung aus (3b) auf
        old_solution_length = len(solution)
        # wichtig: Greedy benoetigt "flache Itemlist"
        solution = [item for bin in solution for item in bin]

        solution = greedy(solution, bin_capacity)
        # schreibe Zwischenergebnis in Ergebnis DataFrame
        num_cols = df_results.shape[0] # aktuelle Zeile
        hit = 0
        if len(solution) == lower_bound:
            hit = 1
        else: hit = 0
        df_results.loc[num_cols] = [typ, instance_index, n_items, bin_capacity, lower_bound,len(solution), len(solution) - lower_bound, hit, iters, time.perf_counter()-tic]
        #['Typ','Instanzindex','Anzahl_Items','Bin_Kapazitaet','LB','HC','Bins_beyond_LB','Hit_LB', 'Iteration','elapsed_time'] 
        if len(solution) == lower_bound:
            return lower_bound
    return len(solution)

def random_permutation(solution, permutation):
    probability = 1/len(solution)
    while len(permutation) == 0:
        for i, bin in enumerate(solution):
            if random.uniform(0,1) <= probability:
                permutation.append(solution[i])
                solution.pop(i)
    return solution, permutation

# waehle den ersten Bin mit der geringsten Anzahl an Items
def permutation_by_heuristic(solution, permutation):
    min_num_items = 10000000
    min_index = 0
    for index, bin in enumerate(solution):
        num_items = len(bin)
        if num_items < min_num_items:
            min_num_items = num_items
            min_index = index
    permutation.append(solution[min_index])
    solution.pop(min_index)
    return solution, permutation

def test_feasibility(solution, bin_capacity):
    for bin in solution:
        assert fullness(bin) <= bin_capacity, print(bin)
        
def bpp_improvement_procedure(solution, permutation, bin_capacity, change):
    change[0] = False
    #iteriere ueber alle bins in pi
    for g in range(0,len(solution)):
        # 2:2 Swap
        for i in range(0,len(solution[g])):
            for j in range(0, len(solution[g])):
                if i != j and j > i:
                    for h in range(0,len(permutation)):
                        for k in range(0,len(permutation[h])):
                            for l in range(0,len(permutation[h])):
                                if l > k:
                                    delta = size(permutation[h][k]) + size(permutation[h][l]) - size(solution[g][i])- size(solution[g][j])
                                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                                        move(i,j, permutation[h], k, l, solution[g])
                                        change[0] = True
                                        #test_feasibility(permutation, bin_capacity)
        # 2:1 Swap
        i = 0
        j = 0
        # iteriere ueber alle items im aktuellen bin
        while i < len(solution[g]):
        # iteriere ueber alle Tauschpartner im aktuellen Bin 
            while j < len(solution[g]):
                 if j > i: # Uebpruefe moeglichen move() nur fuer gueltige Paare
                    # fuer jedes Paar aus aktuellem bin in pi iteriere ueber alle Bins in p
                    for h in range(0,len(permutation)):
                        # iteriere fuer jedes paar ueber alle items im aktuellen Bin in p
                        k = 0 # starte beim ersten item
                        while k < len(permutation[h]):
                            if j > i: # erneute Uebpruefung weil bei move Index j zurueckgesetzt wird                               
                                delta = size(permutation[h][k]) - size(solution[g][i]) - size(solution[g][j]) # erhoeht das Item aus p die Auslastung in pi beim Tausch gegen das Paar?
                                if delta > 0 and fullness(solution[g]) + delta <= bin_capacity: # passt die zusaetzliche Kapazitaet noch in den Bin
                                    move2(i,j,permutation[h], k, solution[g])
                                    change[0] = True
                                    #test_feasibility(permutation, bin_capacity)
                                    k -= 1 # wenn move von Item k stattgefunden hat, ersetzt ein Item aus pi den Platz von k. Setze Index zurueck um fuer dieses Item zu ueberpruefen, ob Ruecktausch gegen andere Items sinnvoll
                                    j -= 1 # setze j zurueck, da Anzahl Items im Bin, um 1 schrumpft. Damit wird sichergestellt, dass naechstes Item nicht uebersprungen wird
                                    # Index von i bleibt unveraendert, da der Platz nun von Item k eingenommen, fuer Item k werden nun Paare gebildet
                            k += 1 # gehe zum naechsten Item im aktuellen bin in p
                 j += 1 # gehe zum naechsten Item im aktuellen bin in pi
            i += 1 # Bilde fuer naechstes Item alle Paare
        # #1:1 Swap
        i = 0
        k = 0
        # fuer alle items im aktuellen bin in pi
        for i in range(0,len(solution[g])):
            # fuer alle bins in p
            for h in range(0,len(permutation)):
                # fuer alle items im aktuellen bin in p
                for k in range(0,len(permutation[h])):
                    delta = size(permutation[h][k]) - size(solution[g][i])
                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                        # tausche item i aus pi mit item k aus p 
                        move3(i, permutation[h], k, solution[g])
                        #test_feasibility(permutation, bin_capacity)
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
    # items aus pi behalten/ zwischenspeichern
    item_i = bin[i]
    item_j = bin[j]
    bin[i] = bin_p[k] # item k aus p ersetzt das Item i in pi
    bin_p[k] = item_i # item i aus pi ersetzt das Item k in p
    bin.pop(j) # item j aus bin in pi wird entfernt
    bin_p.append(item_j) #item j wird am Ende vom bin in pi eingefuegt

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

    #Ergebnis DataFrame erstellen
    df_results = pd.DataFrame(columns = ['Typ','Instanzindex','Anzahl_Items','Bin_Kapazitaet','LB','HC','Bins_beyond_LB','Hit_LB', 'Iteration','elapsed_time'])

    instances_falkenauer_uniform = read_instances("Instanzen/Falkenauer/uniform")
    generate_results_of_instances(instances_falkenauer_uniform, df_results, "uniform")
    
    #instances_falkenauer_triplet = read_instances("Instanzen/Falkenauer/triplet")
    #generate_results_of_instances(instances_falkenauer_triplet, df_results, "triplet")

    print(df_results.head(20))
    df_results.to_csv('results_zeitmessung_u_randomPermutation_100sec.csv',index=False, encoding='utf-8')


# diese Methode ruft die HC Methode fuer die aktuelle Instanz auf und schreibt die Statistiken in ein DataFrame
def generate_results_of_instances(instances, df_results, typ):

    instance_index = 0
    for i in range(0,len(instances)):
        item_list, n_items, bin_capacity, lower_bound  = generate_instance(instances[i])
        # Hill Climbing
        bins_hc = hill_climbing(item_list, bin_capacity, lower_bound,typ, n_items, df_results, instance_index)
        instance_index +=1
        print("Anzahl Bins HC", bins_hc)
        print("-------------")

def main():

    generate_results()    

    return 0

if __name__ == '__main__':
    main()