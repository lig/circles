import click

from . import solve


@click.command(name="circles")
@click.argument('number', type=click.INT)
def main(number: int) -> None:
    assert number > 0

    solutions = solve.calculate_circles(num_circles=number)

    for n, solution in enumerate(sorted(solutions), 1):
        print(f"{n}: {solution}")
    print(f"The number of solutions for `{number}` circles is `{len(solutions)}`")
