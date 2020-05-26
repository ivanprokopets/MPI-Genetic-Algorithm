from function import Func
from optimizer import OptimizerGA
from GUI import get_settings, info_GUI, error_GUI
from settingsGA import gaParams


# (x ** 1/2 - 5 * y ) / (x ** 2 + y ** 2  - 2 * x + 10) - przykladowa Funkcja do testowania

def main():
    try:
        while True:
            gaParams = get_settings()
            function = Func(gaParams.f)
            optimizer = OptimizerGA(function)
            optimizer.startGA_with_statistics(chromosomes_number=gaParams.chromosomes_number,
                                              generations_number=gaParams.generations_number,
                                              mutation=gaParams.mutation, optimizer=gaParams.optimizer)
            info_GUI()

    except Exception as err:
        print('BLAD!\n', type(err))
        print(err)
        error_GUI()


if __name__ == '__main__':
    main()
