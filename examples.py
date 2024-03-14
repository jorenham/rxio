# ruff: noqa: ANN201, T201

import math

from rxio import rx


def example_pythagoras():
    a, b = rx(3), rx(4)
    c = (a ** 2 + b ** 2) ** 0.5

    print(f'{c = }')
    # c = (rx(3)**2 + rx(4)**2)**0.5
    print(float(c))
    # 5.0

    a += 2
    b *= 3

    print(f'{c = }')
    # c = (rx(5)**2 + rx(12)**2)**0.5
    print(float(c))
    # 13.0


def example_zero_division():
    # TODO: use exception groups for multiple errors

    a = rx(-1)
    b = rx(4)
    c = a / b

    print(f'{a = }')
    print(f'{b = }')
    print(f'{c = }')

    print()
    print('b *= 0')
    b *= 0

    print()
    print(f'{a = }')
    print(f'{b = }')
    print(f'{c = }')

    print()
    print('float(c)')
    print(float(c))


def example_callable():

    f = rx(math.sqrt)
    x = rx(4)
    y = f(x)
    print('>>> f = rx(math.sqrt)')
    print('>>> x = rx(4)')
    print('>>> y = f(x)')
    print('>>> float(y)', float(y), sep='\n')

    x //= 2
    print('>>> x //= 2')
    print('>>> float(y)', float(y), sep='\n')

    f.__rx_set__(math.cbrt)
    print('>>> f.__rx_set__(math.cbrt)')
    print('>>> float(y)', float(y), sep='\n')


# example_pythagoras()
# example_zero_division()
example_callable()
