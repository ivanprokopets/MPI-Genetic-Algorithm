import numpy as np
import numpy.random as rd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from collections import OrderedDict

from multiprocessing.managers import BaseManager
from mpi4py import MPI
from time import time
from function import Func
from worker import WorkerGA




import os


class OptimizerGA:
    def __init__(self, function):
        self.function = Func(function)
        self.f = function

    
    def calculate(self, optimizer='min'):
        if optimizer == 'min':
            return min([self.function(*chromosome) for chromosome in self.chromosomes])
        elif optimizer == 'max':
            return max([self.function(*chromosome) for chromosome in self.chromosomes])
        else:
            raise ValueError(optimizer + 'should be max or min')

    def next_generation(self, mutation=False, optimizer='min'):
        part = np.array([self.chromosomes[j] for j in range(0, 4)])
        new_population = self.generate_new_part(part, mutation, optimizer)

        for parts_number in range(1, int(len(self.chromosomes) / 4)):
            part = np.array([self.chromosomes[j] for j in range(parts_number * 4, (parts_number + 1) * 4)])
            new_part = self.generate_new_part(part, mutation, optimizer)
            new_population = np.append(new_population, new_part, axis=0)


        return new_population

    
    def generate_new_part(self, chromosomes, mutation=False, optimizer='min'):
        values = [self.function(*chromosome) for chromosome in chromosomes]
        chromosomesDict = dict(zip([str(i) for i in range(4)], values))
        if optimizer == 'min':
            chromosomesDict = OrderedDict(sorted(chromosomesDict.items(), key=lambda t: t[1]))
        elif optimizer == 'max':
            chromosomesDict = OrderedDict(sorted(chromosomesDict.items(), key=lambda t: -t[1]))
        else:
            raise ValueError(str(optimizer) + 'should be max or min')

        chromosome_indexes = list()

        for chromosome_index in chromosomesDict.keys():
            chromosome_indexes.append(chromosome_index)   #sin(x) * cos(y)

        good_chromosome = chromosomes[int(chromosome_indexes[2])]
        better_chromosome = chromosomes[int(chromosome_indexes[1])]
        best_chromosome = chromosomes[int(chromosome_indexes[0])]
        new_part = np.array([[(better_chromosome[0] + good_chromosome[0]) / 2 + float(2 * mutation * rd.rand(1) - 1 * mutation), (better_chromosome[1] + 0.3 * good_chromosome[1]) + float(2 * mutation * rd.rand(1) - 1 * mutation)],
                             [(better_chromosome[0] + best_chromosome[0]) / 2  + float(2 * mutation * rd.rand(1) - 1 * mutation), (better_chromosome[1] + best_chromosome[1]) / 2  + float(2 * mutation * rd.rand(1) - 1 * mutation)],
                             [(best_chromosome[0] + good_chromosome[0]) / 2 , (best_chromosome[1] + good_chromosome[1]) / 2 + float(2 * mutation * rd.rand(1) - 1 * mutation)],
                             [(better_chromosome[0] + 0.7 * good_chromosome[0]) / 1.7 , (best_chromosome[1] + 0.6 * better_chromosome[1]) / 1.6]])
        return new_part


    def startGA(self, chromosomes_number=4, generations_number=10,
                mutation=False, optimizer='min',
                statistics=True, save=False, plot=True):
        info = {
            'chromosomes_number': chromosomes_number,
            'generations_number': generations_number,
            'mutation': mutation,
            'optimizer': optimizer,
            'function': self.f
        }


        BaseManager.register('register_queue')
        BaseManager.register('input_queue')
        BaseManager.register('results_queue')
        m = BaseManager(address=('localhost', 8080), authkey=b'blah')
        m.connect()
        register_queue = m.register_queue()
        input_queue = m.input_queue()
        results_queue = m.results_queue()
        wait_for_workers = True
        self.workers = 0
        worker_processes = []

        while (wait_for_workers):
            try:
                if (self.workers == 0):
                    worker_processes.append(register_queue.get())

                else:
                    worker_processes.append(register_queue.get(timeout=2))
                input_queue.put(info)
                self.workers += 1

            except:
                wait_for_workers = False

        new_chromosomes_number = 0
        self.chromosomes = None
        for i in range (self.workers):
            chromosomes = results_queue.get()
            if (i == 0):                
                self.chromosomes = np.array(chromosomes)
            else:
                self.chromosomes = np.append(self.chromosomes, chromosomes, axis=0)
            new_chromosomes_number += chromosomes_number * (worker_processes[i] - 1)

        f = open('results/GA-statistics.txt', 'w')
        for i in range(generations_number):
            self.chromosomes = self.next_generation(mutation, optimizer)
            print(self.chromosomes)

            df = pd.DataFrame(self.chromosomes, columns=['x', 'y'])
            x = np.array(df['x'])
            y = np.array(df['y'])
            df['f(x, y)'] = self.function(x, y)
            df.to_csv("generations/generation_{}.csv".format(i + 1))

            f.write('_' * 70)
            f.write('\nINFO about generation {}:\n'.format(i + 1))
            for chromosome in self.chromosomes:
                f.write('chromosome {} gives value: {}\n'.format(chromosome, self.function(*chromosome)))
            f.write('{} value for this generation: {}\n'.format(optimizer, self.calculate(optimizer)))

        f.close()

        if plot:
            self.plotGA(new_chromosomes_number, generations_number, optimizer, save)

        if not (save):
            for i in range(generations_number):
                os.remove("generations/generation_{}.csv".format(i + 1))


    def plotGA(self, chromosomes_number, generations_number, optimizer, save=False):
        print("p1a")

        data = pd.concat([pd.read_csv('generations/generation_{}.csv'.format(i + 1), index_col=0)
                          for i in range(generations_number)], ignore_index=True)
        print("p1b", chromosomes_number)

        data['time'] = [i for i in range(chromosomes_number * generations_number)]
        print("p1c", chromosomes_number)

        def update_graph(num):
            df = data[abs(num * chromosomes_number - data['time']) <= 2 * chromosomes_number]
            graph.set_data(np.array(df['x']), np.array(df['y']))
            graph.set_3d_properties(np.array(df['f(x, y)']))
            title.set_text('GA-optimizer generation={}'.format(num + 1))
            return title, graph,

        fig = plt.figure(figsize=(15, 8), num='GA animation')

        ax = fig.add_subplot(111, projection='3d')

        # Make data.
        X = np.arange(-4, 4, 0.25)
        Y = np.arange(-4, 4, 0.25)
        X, Y = np.meshgrid(X, Y)
        Z = self.function(X, Y)
        '''
                if optimizer == 'min':
                    color = 'blue'
                    color_map = cm.OrRd
                else:
                    color = 'red'
                    color_map = cm.Blues

                # Plot the surface.
                surf = ax.plot_surface(X, Y, Z, cmap=color_map,
                                       linewidth=0, antialiased=True)

                title = ax.set_title('GA-optimizer plot')

                df = data[data['time'] == 0]
                graph, = ax.plot(np.array(df['x']), np.array(df['y']), np.array(df['f(x, y)']),
                                 linestyle="", c=color, marker='o', ms=5)
        '''
        theCM = cm.get_cmap()
        theCM._init()
        alphas = np.abs(np.linspace(-1, 1, int(theCM.N)))
        theCM._lut[:-3, -1] = alphas

        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z, cmap=theCM,
                               linewidth=0, antialiased=True, alpha=0.6)

        title = ax.set_title('GA-optimizer plot')

        df = data[data['time'] == 0]
        graph, = ax.plot(np.array(df['x']), np.array(df['y']), np.array(df['f(x, y)']),
                         linestyle="", c='black', marker='2', ms=2)

        anim = animation.FuncAnimation(fig, update_graph, generations_number,
                                       interval=200, save_count=True)

        # Customize the z axis.
        ax.set_zlim(-5, 5)
        ax.zaxis.set_major_locator(LinearLocator(10))
        ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Add a color bar which maps values to colors.
        fig.colorbar(surf, shrink=0.8, aspect=3)

        plt.show()
        if save:
            anim.save('results/GA-animation.gif', writer='imagemagick', fps=60)