"""Page-slicing for the list screens.

Kept out of the repository on purpose: the row counts here are small enough
that fetching the list and slicing it is honest and keeps every query in
`repository` returning a plain list. If a table ever grows past a few thousand
rows, move the LIMIT/OFFSET into the SQL and change `Page.of` to take a count.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

DEFAULT_PER_PAGE = 25
PER_PAGE_CHOICES = (10, 25, 50, 100)


@dataclass(frozen=True)
class Page:
    """One slice of a list, plus everything a pager needs to render."""

    items: list
    number: int
    per_page: int
    total: int

    @classmethod
    def of(
        cls,
        rows: Sequence,
        number: object = 1,
        per_page: object = DEFAULT_PER_PAGE,
    ) -> "Page":
        """Slice `rows`, clamping the page number and size to something sane."""
        size = _coerce(per_page, DEFAULT_PER_PAGE)
        if size not in PER_PAGE_CHOICES:
            size = DEFAULT_PER_PAGE

        total = len(rows)
        pages = max(1, -(-total // size))
        current = min(max(_coerce(number, 1), 1), pages)
        start = (current - 1) * size
        return cls(list(rows[start : start + size]), current, size, total)

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.per_page))

    @property
    def has_previous(self) -> bool:
        return self.number > 1

    @property
    def has_next(self) -> bool:
        return self.number < self.pages

    @property
    def first_index(self) -> int:
        """1-based index of the first row on this page, 0 when empty."""
        return 0 if not self.total else (self.number - 1) * self.per_page + 1

    @property
    def last_index(self) -> int:
        return min(self.number * self.per_page, self.total)

    @property
    def needed(self) -> bool:
        """False when everything fits on one page, so the pager can be hidden."""
        return self.total > min(PER_PAGE_CHOICES)

    def numbers(self, window: int = 2) -> list[int | None]:
        """Page numbers to show, with None standing in for a gap."""
        if self.pages <= 7:
            return list(range(1, self.pages + 1))

        wanted = {1, self.pages}
        wanted.update(
            n for n in range(self.number - window, self.number + window + 1)
            if 1 <= n <= self.pages
        )
        out: list[int | None] = []
        previous = 0
        for n in sorted(wanted):
            if previous and n - previous > 1:
                out.append(None)
            out.append(n)
            previous = n
        return out


def _coerce(value: object, fallback: int) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return fallback


__all__ = ["DEFAULT_PER_PAGE", "PER_PAGE_CHOICES", "Page"]
