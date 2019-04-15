import click

from . import solve


@click.command(name="circles")
@click.argument('n', type=click.INT)
def main(n: int) -> None:
    assert n > 0

    solutions = solve.calculate_circles(num_circles=n)

    for solution in solutions:
        print(solution)
    print(f"The number of solutions for `{n}` circles is `{len(solutions)}`")
