import numpy as np
import random

class City:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"({self.x},{self.y},{self.z})"

def distance(ca, cb):
    return np.linalg.norm([ca.x - cb.x, ca.y - cb.y, ca.z - cb.z])

def distance_route(path):
    path_array = np.array([[city.x, city.y, city.z] for city in path])
    delta = np.diff(path_array, axis=0)
    distances = np.linalg.norm(delta, axis=1)
    distance_to_start = np.linalg.norm(path_array[0] - path_array[-1])

    return np.sum(distances) + distance_to_start

def CreateInitialPopulation(size, cities, greedy_rate):
    pop = []
    greedy_solutions = int(size * greedy_rate)
    for i in range(greedy_solutions):
        path = greedy_search(i % len(cities), cities)
        pop.append(path)

    for i in range(size - greedy_solutions):
        path = random.sample(cities, len(cities))
        pop.append(path)

    return pop

def greedy_search(start_city_index, cities):
    current_city = cities[start_city_index]
    path = [current_city]
    unvisited = set(cities)
    unvisited.remove(current_city)

    while unvisited:
        next_city = min(unvisited, key=lambda city: distance(current_city, city))
        path.append(next_city)
        unvisited.remove(next_city)
        current_city = next_city

    return path

def fitness(path):
    return 1.0 / distance_route(path)

def rank(pop):
    rankPop_dic = {}
    for i in range(len(pop)):
        fit = fitness(pop[i])
        rankPop_dic[i] = fit

    return sorted(rankPop_dic.items(), key=lambda x: x[1], reverse=True)

def select(pop, eliteSize):
    select_pop = []
    pop_rank = rank(pop)
    for i in range(eliteSize):
        select_pop.append(pop[pop_rank[i][0]])

    cum_sum = sum(item[1] for item in pop_rank)
    cum_prob = []
    previous_prob = 0
    for i in range(len(pop)):
        prob = pop_rank[i][1]/cum_sum
        cum_prob.append(previous_prob + prob)
        previous_prob = cum_prob[-1]

    for i in range(len(pop) - eliteSize):
        r = random.random()
        for j, prob in enumerate(cum_prob):
            if r <= prob:
                select_pop.append(pop[pop_rank[j][0]])
                break

    return select_pop

def crossover(pop, eliteSize):
    breed_pop = []
    for i in range(eliteSize):
        breed_pop.append(pop[i])

    while len(breed_pop) < len(pop):
        parent1 = random.choice(pop)
        parent2 = random.choice(pop)
        if parent1 != parent2:
            a = random.randint(0, len(parent1) - 1)
            b = random.randint(0, len(parent2) - 1)
            start_index = min(a, b)
            end_index = max(a, b)
            child = [-1] * len(parent1)

            for i in range(start_index, end_index):
                child[i] = parent1[i]

            pointer = 0
            for city in parent2:
                 if city not in child:
                        while pointer < len(child) and child[pointer] != -1:
                            pointer += 1

                        if pointer < len(child):
                            child[pointer] = city

            breed_pop.append(child)

    return breed_pop

def mutate(pop, mutationRate):
    mutation_pop = []
    for i in range(len(pop)):
        for j in range(len(pop[i])):
            rate = random.random()
            if rate < mutationRate:
                a = random.randint(0, len(pop[i]) - 1)
                pop[i][a], pop[i][j] = pop[i][j], pop[i][a]
        mutation_pop.append(pop[i])

    return mutation_pop


def next_pop(pop, eliteSize, mutationRate):
    select_pop = select(pop, eliteSize)
    breed_pop = crossover(select_pop, eliteSize)
    next_generation = mutate(breed_pop, mutationRate)

    return next_generation

def GA(cities, size, greedy_rate, eliteSize, mutationRate, generations):
    population = CreateInitialPopulation(size, cities, greedy_rate)
    process = []

    for i in range(generations):
        population = next_pop(population, eliteSize, mutationRate)
        process.append(1.0 / (rank(population)[0][1]))

    index_rank_pop = rank(population)[0][0]
    best_route = population[index_rank_pop]

    f_output = open('output.txt', 'w')
    f_output.write(str(1.0 / (rank(population)[0][1])) + '\n')
    for i in range(len(best_route)):
        f_output.write(
            str(int(best_route[i].x)) + ' ' + str(int(best_route[i].y)) + ' ' + str(int(best_route[i].z)) + '\n')
    f_output.write(str(int(best_route[0].x)) + ' ' + str(int(best_route[0].y)) + ' ' + str(int(best_route[0].z)) + '\n')
    f_output.close()

    city_x = []
    city_y = []
    city_z = []
    for j in range(len(best_route)):
        city = best_route[j]
        city_x.append(city.x)
        city_y.append(city.y)
        city_z.append(city.z)
    city_x.append(best_route[0].x)
    city_y.append(best_route[0].y)
    city_z.append(best_route[0].z)

cities = []

with open('input.txt', 'r', encoding='UTF-8') as f:
    lines = f.readlines()
    num_city = int(lines[0])
for line in lines[1:]:
    city = line.split(' ')
    cities.append(City(float(city[0]), float(city[1]), float(city[2])))

GA(cities, 200, 0.5, 40, 0.01, 510)