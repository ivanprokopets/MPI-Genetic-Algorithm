# Maksymum Minimum Funkcji poprzez Algorytm genetyczny

### Uruchomienie:
** python3 main.py aby uruchomić ten program i otworzyć GUI


Program ten w przybliżeniu oblicza minimum lub maksimum funkcji o dwóch parametrach na podstawie algorytmu genetycznego.  
Każdy osobnik ma jeden chromosom (x, y) i ze względu na to, że osobnik i chromosom mają to samo znaczenie, pokolenie składa się z części, gdzie jedna część to 4 osobniki, w konsekwencji liczba chromosomów jest wielokrotnością 4.  

Zasada crossover to:  

(x_better, y_best), (y_better, y_best), (x_best, y_better), (x_best, y_good)  

gdzie (x_best, y_best), (x_better, y_better), (x_good, y_good) są zaznaczonymi individs.


Mutacja może być wybrana losowo w dowolnym Genie (można ją skonfigurować w metodzie startGA_with_statistics).  
Wypełnienie z pokolenia zerowego losowymi liczbami zmiennoprzecinkowymi w [-chromosomes_number / 2, chromosomes_number).  
Wyniki są wyświetlane na ekranie, a także zapisywane w ' Ga-statistics.txt".  

https://pl.wikipedia.org/wiki/Algorytm_genetyczny
https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_crossover.html
https://www.sciencedirect.com/science/article/pii/S0045794900000894
https://www.geeksforgeeks.org/crossover-in-genetic-algorithm/
 
