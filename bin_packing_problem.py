# ToDo
# - Eingaberepraesentation
# - Parameter verschiedener Instanzen
# - verschiedene Instanzen simulieren
# - Greedy Algorithmus (first fit) fuer verschiedene Instanzen implementieren
# - Warum lookup Hashtabelle?
# - LB minimale Bin Anzahl eigentlich easy? auch freien Platz minimieren?
# - wie sollen Instanzen generiert werden
# - spielt Reihenfolge in Bin eine Rolle? Wegen HT?
# - Was wird Greedy uebergeben? Bei uns Dictionary, woraus G ermittelt wird, bin_capacity aber auch noetig fuer feasibility test

# def greedy(Items, Bucketsize):
# fuege Items der Reihe nach in Bucket mit niedrigstem Index ein, solange Kapazitaet nicht ueberschritten
# Kapazitaet ueberschritten ? neuer Bucket
# Resultat: Abhaengig von Reihenfolge der Items, minimal LB

# arbitratry permutaiton
# Loesungsrepraesentation

#from collections import ChainMap
import random
from pathlib import Path

def generate_instances():
    documents_path = Path("Falkenauer/uniform")
    instances_falkenauer = []
    for document in documents_path.iterdir():
        with open(document) as f:
            content = f.readlines()
        instances_falkenauer.append([x.strip() for x in content])
    
    # Beispielhaft erste Instanz extrahieren
    item_list = {}
    bin_capacity = 0
    for i, item_capacity in enumerate(instances_falkenauer[0]):
        if i == 1:
            bin_capacity = item_capacity # Zeile 1 enthaelt bin capacity
        elif i > 1:
            item_list[i] = int(item_capacity)
    
    return item_list    


def is_feasible(item_capacity, bin_capacity, current_bin):
    # hat aktueller bin noch Platz fuer aktuelles Item?
    if (bin_capacity - fullness(current_bin) - item_capacity) >= 0:
        return True
    else:
        return False

def greedy(item_list, bin_capacity, groups):

    for item_name, item_capacity in item_list.items():
        j = 0
        found = False
        while not found and j <= len(groups) - 1: 
            if is_feasible(item_capacity, bin_capacity, groups[j]):
                groups[j][item_name] = item_capacity
                found = True
            else:
                j += 1
        if not found:
            groups.append({item_name: item_capacity}) # open new group & add item
    return groups

def first_fit_descending(item_list, bin_capacity, groups):
    # sortiere dictionary by value (Items nach absteigender Kapazität)
    # item[1] ist der Value (die Kapazitaet) des jeweiligen Items
    sorted_item_list = {item_name: item_value for item_name, item_value in sorted(item_list.items(), reverse=True, key=lambda item: item[1])}
    first_solution = greedy(sorted_item_list, bin_capacity, groups) # rufe Greedy-Heuristik mit sortierter Item-List auf
    return first_solution

def generate_pairs(group):
    # group ist Dictoniary der Items in einer Gruppe (Bin)
    # langsame Version 
    pairs = []
    i = 0
    j = 0
    for item_i_name, item_i_capacity in group.items():
        j = 0
        for item_j_name, item_j_capacity in group.items():
            if item_i_name != item_j_name and j > i:
                pairs.append(({item_i_name: item_i_capacity},{item_j_name: item_j_capacity}))
            j += 1
        i +=1        
        
    return pairs

def size(tupel_item):
    # uebergebe Tupel / Paar of dict
    return next(iter(tupel_item.values()))

def fullness(group):
    # group ist ein dictionary der Items
    return sum(group.values())

def move1(pair, permutation_pair, group_in_solution, group_in_permutation):
    # pair, permuation_pair sind jeweils Tupel of dict
    # group_in_solution und group_in_permutation sind jeweils dict
    # entferne items aus der jeweiligen Gruppe
    print("Paar ", pair)
    print("aktuelles pi ", group_in_solution)
    print("Tauschpartner ", permutation_pair)
    print("P: ", group_in_permutation)
    
    
    del group_in_solution[next(iter(pair[0].keys()))]
    del group_in_solution[next(iter(pair[1].keys()))]
    del group_in_permutation[next(iter(permutation_pair[0].keys()))]
    del group_in_permutation[next(iter(permutation_pair[1].keys()))]
    # fuege items in die Gruppe der anderen Menge hinzu
    group_in_permutation[next(iter(pair[0].keys()))] = next(iter(pair[0].values()))
    group_in_permutation[next(iter(pair[1].keys()))] = next(iter(pair[1].values()))
    group_in_solution[next(iter(permutation_pair[0].keys()))] = next(iter(permutation_pair[0].values()))
    group_in_solution[next(iter(permutation_pair[1].keys()))] = next(iter(permutation_pair[1].values()))

    print("Tausch durchgefuehrt")
    print("Paar ", pair)
    print("aktuelles pi ", group_in_solution)
    print("Tauschpartner ", permutation_pair)
    print("P: ", group_in_permutation)
    


def move2(pair, p_item, group_in_solution, group_in_permutation):
    # pair, permuation_pair sind jeweils Tupel of dict
    # group_in_solution und group_in_permutation sind jeweils dict
    print("Paar ", pair)
    print("Loesung ", group_in_solution)
    print("Permutationsitem ", p_item)
    print("Permutationsmenge ", group_in_permutation)
    # entferne items aus der jeweiligen Gruppe
    del group_in_solution[next(iter(pair[0].keys()))]
    del group_in_solution[next(iter(pair[1].keys()))]
    del group_in_permutation[p_item[0]]
    # fuege items in die Gruppe der anderen Menge hinzu
    group_in_permutation[next(iter(pair[0].keys()))] = next(iter(pair[0].values()))
    group_in_permutation[next(iter(pair[1].keys()))] = next(iter(pair[1].values()))
    group_in_solution[p_item[0]] = p_item[1]
    print("Tausch durchgefuehrt")
    print("Paar ", pair)
    print("Loesung ", group_in_solution)
    print("Permutationsitem ", p_item)
    print("Permutationsmenge ", group_in_permutation)

def move3(item_i, p_item, group_in_solution, group_in_permutation):
    # pair, permuation_pair sind jeweils Tupel of dict
    # group_in_solution und group_in_permutation sind jeweils dict
    # entferne items aus der jeweiligen Gruppe
    print("Item aus pi", item_i)
    print("item aus p", p_item)
    print("pi", group_in_solution)
    print("pi", group_in_permutation)
    del group_in_solution[next(iter(item_i.keys()))]
    del group_in_permutation[next(iter(p_item.keys()))]
    # fuege items in die Gruppe der anderen Menge hinzu
    group_in_permutation[next(iter(item_i.keys()))] = next(iter(item_i.values()))
    group_in_solution[next(iter(p_item.keys()))] = next(iter(p_item.values()))


def bpp_improvement_procedure(solution, permutations, bin_capacity, changed):

    print("improvement()")

    changed[0] = False

    for g in range(0,len(solution)): # iteriere über alle Gruppen (der Teilmenge pi) / Liste (g ist Index)
        pair_list = generate_pairs(solution[g]) # generiere alle moeglichen Itempaare im aktuellen Bin
        moved = False
        for pair in pair_list: # iteriere ueber alle moeglichen Paare im aktuellen Bin
            # pair ist ein Tupel of dict der Form: ({'a':10},{'b':20})
            for h in range(0,len(permutations)): # Iteriere ueber Gruppen der Permutationen (List of Dict)
                if moved:break
                permutation_pair_list = generate_pairs(permutations[h]) # erzeuge alle Paare aktueller Gruppe in Permutation
                for permutation_pair in permutation_pair_list: # Iteriere ueber Paare der aktuellen Gruppe in Permuation
                    if moved:break
                    delta = size(permutation_pair[0]) + size(permutation_pair[1]) - size(pair[0]) - size(pair[1])
                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                        # Move items i and j into group h in p and move items k into group g in pi
                        # entferne Paar aus Gruppe
                        print("move1()")
                        print(pair_list)
                        move1(pair, permutation_pair, solution[g], permutations[h])
                        moved = True
                        changed[0] = True
                        break
            
                        # nach move aendert sich solution und dementsprechen muesste die pair list neu generiert werden

        pair_list = generate_pairs(solution[g])
        for pair in pair_list: # iteriere ueber alle Paare des aktuellen Bins
            if moved: break
            for h in range(0,len(permutations)): # iteriere ueber alle Gruppen der Permutationsmenge
                if moved:break
                for p_item in permutations[h].copy().items(): # fuer jedes Item in aktueller Gruppe ueberpruefe delta
                    delta = p_item[1] - (size(pair[0]) + size(pair[1]))
                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                        print("move2()")
                        move2(pair, p_item, solution[g], permutations[h])
                        moved = True
                        changed[0] = True
                        break

        moved = False
        for item_i, item_i_capacity in solution[g].copy().items():
            if moved:break
            for h in range(0, len(permutations)):
                if moved:break
                for p_item, p_item_capacity in permutations[h].copy().items():
                    
                    delta = p_item_capacity - item_i_capacity
                    if delta > 0 and fullness(solution[g]) + delta <= bin_capacity:
                        print("move3()")
                        move3({item_i: item_i_capacity}, {p_item:p_item_capacity}, solution[g], permutations[h])
                        moved = True
                        changed[0] = True
                        break

def hill_climbing(item_list, bin_capacity):
    solution = [{}] # leere Liste aus dictionaries
    solution = first_fit_descending(item_list, bin_capacity, solution) # Konstruktionsverfahren
    # (1) Teilmenge aus Loesung bildet Permutationsgruppe 
    permutations = []
    for i in range(0,2): # wahl der zufaelligen Teilmenge?
        random_index = random.randint(0,len(solution)-1)  # ziehe zufaelligen Index
        permutations.append(solution[random_index]) # fuege Gruppe aus Loesung in Permutationsgruppe ein
        solution.pop(random_index) # entferne Gruppe/ bin aus solution (pi)
    
    changed = []
    changed.append(True)
    while changed[0]:
        bpp_improvement_procedure(solution, permutations, bin_capacity, changed)
    
    for group in permutations:
        solution.append(group)
    
    # Schritt 3
    solution = {item_name: item_value for bin in solution for item_name, item_value in bin.items()} # flaches Dict
    solution = greedy(solution, bin_capacity, [{}])
    return solution
    

def print_solution(solution, name):
    print(name)
    print("Loesung: ", solution)
    print("Anzahl Gruppen: ", len(solution))
      

def main():
    # to do: Greedy bekommt Lösung übergeben statt ItemList

    #item_list = {'a': 4, 'd':5, 'b':3, 'e':4, 'g':4, 'c':2, 'h':2, 'i':2, 'f':1, 'l':2,'j':2,'k':2,'m':5, 'z':1, 'y':1}
    
    
    bin_capacity = 150 # Klasse mit Attribut oder andere Loesung, hier 150 da so in Paper

    item_list = generate_instances()
    solution_greedy = [{}]
    solution_greedy = greedy(item_list, bin_capacity, solution_greedy)
    print_solution(solution_greedy, "Greedy Heuristik")
    
    item_list = generate_instances()
    solution_first_fit = [{}]
    solution_first_fit = greedy(item_list, bin_capacity, solution_first_fit)
    print_solution(solution_first_fit, "First Fit (mit Greedy)")

    item_list = generate_instances()
    solution_improvement = hill_climbing(item_list, bin_capacity)
    print_solution(solution_improvement, "Improvement")

    #groups = {item_name: item_value for bin in groups for item_name, item_value in bin.items()} # extrahiere flaches Dictionary aus List

    return 0



if __name__ == "__main__":
    main()



