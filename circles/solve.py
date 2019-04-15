import collections
import itertools
import typing

from . import types


def calculate_contained(
    *, circle: types.Circle, indexes: typing.Set[int]
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
    *, circle: types.Circle, indexes: typing.Set[int]
) -> typing.Iterable[types.Circle]:
    indexes = indexes.difference(circle.contains)

    intersections_powerset = itertools.chain.from_iterable(
        itertools.combinations(indexes, r) for r in range(len(indexes) + 1)
    )

    variants: typing.MutableSequence[types.Circle] = []
    for intersections_list in intersections_powerset:
        intersection_permutations = list(itertools.permutations(intersections_list * 2))
        for intersection_permutation in intersection_permutations:
            container_circle = types.Circle(
                index=circle.index,
                contains=circle.contains,
                intersects=intersection_permutation,
            )
            variants.append(container_circle)

    return variants


def calculate_solutions(
    *, index: int, indexes: typing.Set[int]
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


def normalize_intersection(
    *, intersects: typing.Tuple[int, ...]
) -> typing.Tuple[int, ...]:
    rotor = collections.deque(intersects)
    rotations = []
    for i in range(len(intersects)):
        rotations.append(tuple(rotor))
        rotor.rotate(1)
    return intersects and min(rotations)


def normalize_solution(*, solution: types.solution_T) -> types.solution_T:
    normalized_solution: types.solution_T = []
    index_map: typing.MutableMapping[int, int] = {}
    next_index = 0

    def _push(index: int) -> None:
        nonlocal next_index
        if index in index_map:
            return
        index_map[index] = next_index
        next_index += 1

    for circle in sorted(
        solution, key=lambda x: (len(x.intersects), len(x.contains)), reverse=True
    ):
        for index in circle.intersects:
            _push(index=index)
        for index in circle.contains:
            _push(index=index)
        _push(index=circle.index)

        normalized_solution.append(
            types.Circle(
                index=index_map[circle.index],
                contains=frozenset(index_map[index] for index in circle.contains),
                intersects=normalize_intersection(
                    intersects=tuple(index_map[index] for index in circle.intersects)
                ),
            )
        )

    normalized_solution.sort(key=lambda x: x.index)

    return normalized_solution


def is_valid_solution(*, solution: types.solution_T):
    require_intersections = set()

    for circle in solution:

        intersection_stack = []
        for index in circle.intersects:
            intersection_stack.append(index)
            if len(intersection_stack) < 2:
                continue

            if intersection_stack[-1] == intersection_stack[-2]:
                del intersection_stack[-2:]
            else:
                require_intersections.add(tuple(sorted(intersection_stack[-2:])))

    print(require_intersections)

    for circle in solution:
        for index in circle.intersects:
            require_intersections.discard(tuple(sorted((circle.index, index))))

    print(require_intersections)

    return not require_intersections


def normalize_solutions(
    *, solutions: typing.Sequence[types.solution_T]
) -> types.result_T:
    return {
        tuple(normalize_solution(solution=solution))
        for solution in sorted(solutions)
        if is_valid_solution(solution=solution)
    }


def calculate_circles(*, num_circles: int) -> types.result_T:
    indexes = set(range(num_circles))
    index = indexes.pop()
    return normalize_solutions(
        solutions=calculate_solutions(index=index, indexes=indexes)
    )
