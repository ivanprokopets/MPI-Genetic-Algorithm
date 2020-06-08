import numpy as np
import numpy.random as rd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from multiprocessing.managers import BaseManager

from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from collections import OrderedDict

from mpi4py import MPI
from time import time
from function import Func

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



import os






class WorkerGA:
    def __init__(self):
        self.data = {}
        self.data = comm.bcast(self.data, root=0)
        self.function = Func(self.data['function'])
        self.chromosomes = np.array([(2 * rd.rand(2) - 2) for i in range(self.data['chromosomes_number'])])
        all_gens = None
        all_values = None
        for i in range(self.data['generations_number']):
            self.chromosomes, values = self.next_generation(self.data['mutation'], self.data['optimizer'])
            if (i == 0):
                all_gens = self.chromosomes
                all_values = values
            else:
                all_gens = np.append(all_gens, self.chromosomes, axis=0)
                all_values = np.append(all_values, values, axis=0)                
        recvbuf = None
        # if (rank ==  1):
            # print(all_gens[np.argsort(all_values)[0:4]])
        if(self.data['optimizer'] == 'min'):
            comm.Gather(all_gens[np.argsort(all_values)[0:4]], recvbuf, root=0)
        elif (self.data['optimizer'] == 'max'):
            comm.Gather(all_gens[np.argsort(all_values)[-3::]], recvbuf, root=0)

    


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
            chromosome_indexes.append(chromosome_index)

        good_chromosome = chromosomes[int(chromosome_indexes[2])]
        better_chromosome = chromosomes[int(chromosome_indexes[1])]
        best_chromosome = chromosomes[int(chromosome_indexes[0])]

        x0 = (better_chromosome[0] + good_chromosome[0]) / 2 + float(2 * mutation * rd.rand(1) - 1 * mutation) 
        y0 = (better_chromosome[1] + 0.3 * good_chromosome[1]) + float(2 * mutation * rd.rand(1) - 1 * mutation)
        x1 = (better_chromosome[0] + best_chromosome[0]) / 2  + float(2 * mutation * rd.rand(1) - 1 * mutation)
        y1 = (better_chromosome[1] + best_chromosome[1]) / 2  + float(2 * mutation * rd.rand(1) - 1 * mutation)
        x2 = (best_chromosome[0] + good_chromosome[0]) / 2 
        y2 = (best_chromosome[1] + good_chromosome[1]) / 2 + float(2 * mutation * rd.rand(1) - 1 * mutation)
        x3 = (better_chromosome[0] + 0.7 * good_chromosome[0]) / 1.7 
        y3 = (best_chromosome[1] + 0.6 * better_chromosome[1]) / 1.6

        new_part = np.array([[x0, y0],
                             [x1, y1],
                             [x2, y2],
                             [x3, y3]])
        values = np.array([self.function(x0, y0), self.function(x1, y1), self.function(x2, y2), self.function(x3, y3)])               
        
        return (new_part, values)

    def next_generation(self, mutation=False, optimizer='min'):
        part = np.array([self.chromosomes[j] for j in range(0, 4)])
        new_population, values = self.generate_new_part(part, mutation, optimizer)

        for parts_number in range(1, int(len(self.chromosomes) / 4)):
            part = np.array([self.chromosomes[j] for j in range(parts_number * 4, (parts_number + 1) * 4)])
            new_part, values_part = self.generate_new_part(part, mutation, optimizer)
            new_population = np.append(new_population, new_part, axis=0)
            values = np.append(values, values_part, axis=0)

        return (new_population, values)


    def calculate(self, optimizer='min'):
        if optimizer == 'min':
            return min([self.function(*chromosome) for chromosome in self.chromosomes])
        elif optimizer == 'max':
            return max([self.function(*chromosome) for chromosome in self.chromosomes])
        else:
            raise ValueError(optimizer + 'should be max or min')


if __name__ == '__main__':
    if (rank == 0):
        BaseManager.register('register_queue')
        BaseManager.register('input_queue')
        BaseManager.register('results_queue')
        m = BaseManager(address=('localhost', 8080), authkey=b'blah')
        m.connect()
        register_queue = m.register_queue()
        input_queue = m.input_queue()
        results_queue = m.results_queue()
        register_queue.put(size)
        print(rank, size)
        data = input_queue.get()
        print(data)

        comm.bcast(data, root=0)
        sendbuf = np.empty([data['chromosomes_number'], 2])
        recvbuf = np.empty([size, data['chromosomes_number'], 2])
        comm.Gather(sendbuf, recvbuf, root=0)
        chromosomes_to_send = None
        for i in range (1, size):
            if (i == 1):
                chromosomes_to_send = recvbuf[i]
            else:
                chromosomes_to_send = np.append(chromosomes_to_send, recvbuf[i], axis=0)
        results_queue.put(chromosomes_to_send)
    else:
        worker = WorkerGA()