import matplotlib.pyplot as plt
from copy import deepcopy
from time import time
from os import path
from os import walk
import itertools
import random
import sys
import os

script_path = path.basename(__file__)
directory_path = os.getcwd()

boards_path = path.join(directory_path, "boards")
results_path_images = path.join(directory_path, "results", "images")
results_path_boards = path.join(directory_path, "results", "boards")

if not path.exists(boards_path):
    os.makedirs(boards_path)
if not path.exists(results_path_images):
    os.makedirs(results_path_images)
if not path.exists(results_path_boards):
    os.makedirs(results_path_boards)

restarts = 1
searchs = 10

zone_dimensions = (3, 3)

if len(sys.argv) > 1:
    arguments = sys.argv[1:]
    for argument_index in range(len(arguments)):
        if argument_index < (len(arguments) - 1):
            argument_value = arguments[argument_index]
            if argument_value == "--generations":
                generations = int(arguments[argument_index + 1])
            if argument_value == "--population":
                population = int(arguments[argument_index + 1])
            if argument_value == "--restarts":
                restarts = int(arguments[argument_index + 1])
            if argument_value == "--searchs":
                searchs = int(arguments[argument_index + 1])


def get_file_name(board_path):
    return path.basename(board_path).split(".")[0]


def custom_fitness_report(individual):
    row_collisions, column_collisions, zone_collisions = 0, 0, 0

    for row in range(len(individual)):
        row_set = set()
        for column in range(len(individual[row])):
            row_set.add(individual[row][column])
        repetitions = abs(len(individual[row]) - len(row_set))
        row_collisions += repetitions

    for row in range(len(individual)):
        column_set = set()
        for column in range(len(individual[row])):
            column_set.add(individual[column][row])
        column_repetitions = abs(len(individual[row]) - len(column_set))
        column_collisions += column_repetitions

    for row in range(0, len(individual), zone_dimensions[-1]):
        for column in range(0, len(individual[row]), zone_dimensions[0]):
            zone_set = set()
            for i in range(zone_dimensions[-1]):
                sub1 = individual[row + i][column : column + zone_dimensions[0]]
                zone_set.update(set(sub1))
            zone_repetitions = abs(
                (zone_dimensions[0] * zone_dimensions[-1]) - len(zone_set)
            )
            zone_collisions += zone_repetitions

    print("errors in zones: " + str(zone_collisions))
    print("errors in rows: " + str(row_collisions))
    print("erros in columns: " + str(column_collisions))


def custom_fitness(individual):
    collisions = 0

    for row in range(len(individual)):
        column_set = set()
        for column in range(len(individual[row])):
            column_set.add(individual[column][row])
        column_repetitions = abs(len(individual[row]) - len(column_set))
        collisions += column_repetitions

    for row in range(0, len(individual), zone_dimensions[-1]):
        for column in range(0, len(individual[row]), zone_dimensions[0]):
            zone_set = set()
            for i in range(zone_dimensions[-1]):
                sub1 = individual[row + i][column : column + zone_dimensions[0]]
                zone_set.update(set(sub1))
            zone_repetitions = abs(
                (zone_dimensions[0] * zone_dimensions[-1]) - len(zone_set)
            )
            collisions += zone_repetitions

    return collisions


def correct_row(individual, fi1):
    global board_b
    for col1 in range(len(board_b[fi1])):
        if board_b[fi1][col1] != 0 and individual[fi1][col1] != board_b[fi1][col1]:
            col2 = individual[fi1].index(board_b[fi1][col1])
            individual[fi1][col1], individual[fi1][col2] = (
                individual[fi1][col2],
                individual[fi1][col1],
            )
    return individual


def generar_estados(individual, fila):
    global board_b
    if1 = fila
    estados = []
    numeros_moviles = list(
        filter(
            lambda x: x not in board_b[if1],
            [n for n in range(1, (zone_dimensions[0] * zone_dimensions[-1]) + 1)],
        )
    )
    variaciones_numeros_moviles = list(
        itertools.permutations(numeros_moviles, len(numeros_moviles))
    )
    for variacion_fila in variaciones_numeros_moviles:
        Fila = [n for n in board_b[if1]]
        variacion_fila = list(variacion_fila)
        for i in range(len(board_b[if1])):
            if Fila[i] == 0:
                Fila[i] = variacion_fila[0]
                variacion_fila.remove(variacion_fila[0])
        estados.append((custom_fitness(individual), Fila))
    return estados


def mejorar_1(individual):
    individuali = deepcopy(individual)
    if1 = random.randrange(len(individual))
    ic1 = random.randrange(len(individual[if1]))
    ic2 = random.randrange(len(individual[if1]))
    individual[if1][ic1], individual[if1][ic2] = (
        individual[if1][ic2],
        individual[if1][ic1],
    )
    individual = correct_row(individual, if1)
    if custom_fitness(individual) <= custom_fitness(individuali):
        return individual
    else:
        return individuali


def save_board(board, output_file_path):

    if path.exists(output_file_path):
        os.remove(output_file_path)

    for row in board:
        with open(output_file_path, "a") as output_file:
            for number in row:
                output_file.write(f"{number} ")
            output_file.write("\n")


def read_initial_board(board_path):
    board_a = []
    archivo = open(board_path, "r")
    lineas = list(archivo)
    for linea in lineas:
        linea = linea.split(" ")
        linea = [x for x in filter(lambda x: x != "\n", linea)]
        for i in range(len(linea)):
            linea[i] = int(linea[i])
        board_a.append(linea)
    archivo.close()
    return board_a


def start_board(board_a):
    for fila in board_a:
        for indice in range(len(fila)):
            if fila[indice] == 0:
                while True:
                    nuevonumero = random.randrange(
                        1, (zone_dimensions[0] * zone_dimensions[-1]) + 1
                    )
                    if nuevonumero not in fila:
                        break
                fila[indice] = nuevonumero
    return board_a


all_files_list = [file_name for _, _, file_name in walk(boards_path)][0]
txt_files_list = [
    file_name
    for file_name in filter(
        lambda file_name: file_name.split(".")[-1] == "txt", all_files_list
    )
]

print("")
for file_name in txt_files_list:

    board_path = path.join(boards_path, file_name)
    board_name = get_file_name(board_path)
    board_a = read_initial_board(board_path)
    board_b = deepcopy(board_a)

    puntuaciones = list()
    tableros = list()

    searchs_counter = 0

    y_axis_0 = list()
    y_axis_1 = list()
    x_axis_0 = list()

    print(f"solving with: {get_file_name(script_path)}")
    print(f"board name: {board_name}")
    print(f"board path: {board_path}")

    print("starting to solve the board")

    start_time = time()

    for i in range(restarts + 1):
        individual = start_board(board_a)
        for i in range(searchs):
            searchs_counter += 1
            print(
                f"elapsed searches: {searchs_counter}/{searchs * (restarts + 1)}",
                end="\r",
            )
            individual = mejorar_1(individual)
            tableros.append(individual)
            puntuaciones.append(custom_fitness(individual))

    elapsed_time = time() - start_time

    for i in tableros:
        if custom_fitness(i) < custom_fitness(individual):
            board_a = i

    print("")
    print("board solved")
    print("execution time: %0.2f seconds" % elapsed_time)
    print(f"restarts: {restarts}")
    print(f"searches per restart: {searchs}")
    print(f"total searches: {searchs * (restarts + 1)}")
    print(f"errors: {custom_fitness(board_a)}")

    save_board(board_a, path.join(results_path_boards, f"{board_name}_hc_result.txt"))

    custom_fitness_report(board_a)
    print("saving algorithm performance trace")

    plt.figure(figsize=(16, 9))

    plt.plot(
        puntuaciones,
        "-",
        linewidth=0.8,
        color="r",
        label=f"performance trace [errors: {custom_fitness(board_a)}]",
    )

    plt.xlabel("iterations")
    plt.ylabel("errors")
    plt.legend()
    plt.grid()
    plt.savefig(path.join(results_path_images, f"{board_name}_hc_performance.png"))
    plt.clf()

    del board_a, board_b
    print("algorithm performance trace saved")
    print("")
