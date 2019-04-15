import itertools
import typing

from . import types


def calculate_contained(
    circle: types.Circle, indexes: typing.Set[int]
) -> typing.Iterable[types.Circle]:
    contained_powerset = itertools.chain.from_iterable(
        itertools.combinations(indexes, r) for r in range(len(indexes) + 1)
    )

    variants: typing.MutableSequence[types.Circle] = []
    for contained_list in contained_powerset:
        container_circle = types.Circle(
            index=circle.index,
            contains=frozenset(contained_list),
            intersects=circle.intersects,
        )
        variants.append(container_circle)

    return variants


def calculate_intersections(
    circle: types.Circle, indexes: typing.Set[int]
) -> typing.Iterable[types.Circle]:
    indexes = indexes.difference(circle.contains)

    intersections_powerset = itertools.chain.from_iterable(
        itertools.combinations(indexes, r) for r in range(len(indexes) + 1)
    )

    variants: typing.MutableSequence[types.Circle] = []
    for intersections_list in intersections_powerset:
        intersection_permutations = list(itertools.permutations(intersections_list))
        intersection_variants = [
            sum(x, tuple()) for x in itertools.product(*[intersection_permutations] * 2)
        ]
        for intersection_variant in intersection_variants:
            container_circle = types.Circle(
                index=circle.index,
                contains=circle.contains,
                intersects=intersection_variant,
            )
            variants.append(container_circle)

    return variants


def calculate_solutions(
    index: int, indexes: typing.Set[int]
) -> typing.Sequence[types.solution_T]:
    variants: typing.MutableSequence[types.Circle] = []

    # start with empty one
    circle = types.Circle(index=index, contains=frozenset(), intersects=tuple())

    # return the only solution if there is no other circles
    if not indexes:
        return [[circle]]

    # otherwise put it as the first variant
    variants.append(circle)

    # like the emty one but could contain any number of others
    variants.extend(calculate_contained(circle=circle, indexes=indexes))

    # could intersect any number of others which is not contained in
    extra_variants: typing.MutableSequence[types.Circle] = []
    for variant in variants:
        extra_variants.extend(calculate_intersections(circle=variant, indexes=indexes))
    variants.extend(extra_variants)

    # for each solution for each index combine with each variant
    # only possible solution should be considered
    solutions: typing.MutableSequence[types.solution_T] = []
    for variant in variants:

        solution_tails: typing.MutableSequence[types.solution_T] = []
        for index in indexes:
            if index in variant.contains:
                possible_indexes = (
                    set(variant.contains).union(variant.intersects).difference({index})
                )
            elif index in variant.intersects:
                possible_indexes = indexes.difference({index})
            else:
                possible_indexes = indexes.difference(
                    set(variant.contains).union({index})
                )
            solution_tails.extend(
                calculate_solutions(index=index, indexes=possible_indexes)
            )

        solutions.extend([variant] + solution_tail for solution_tail in solution_tails)

    return solutions


def calculate_circles(num_circles: int) -> typing.Set[typing.Tuple[types.Circle, ...]]:
    indexes = set(range(num_circles))
    index = indexes.pop()
    solutions = calculate_solutions(index=index, indexes=indexes)
    return {tuple(solution) for solution in solutions}
