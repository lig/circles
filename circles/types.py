import typing

import attr


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Circle:
    index: int
    contains: typing.FrozenSet[int] = attr.ib()
    intersects: typing.Tuple[int, ...] = attr.ib()

    @contains.validator
    def _check_contains(
        self, attribute: attr.Attribute, value: typing.Set[int]
    ) -> None:
        # cannot contain itself
        assert self.index not in value

    @intersects.validator
    def _check_intersects(
        self, attribute: attr.Attribute, value: typing.Iterable[int]
    ) -> None:
        # cannot intersect itself
        assert self.index not in value

        # is a list of paired unique indexes
        assert sorted(list(set(value)) * 2) == sorted(value)


solution_T = typing.List[Circle]
