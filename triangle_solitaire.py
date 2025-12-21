# triangles
from enum import Enum
from typing import Any

MAX_DEGREE = 3
SIDE_LENGHTS = [5, 6, 8, 9]
MIN_SIDE_LENGTH = SIDE_LENGHTS[0]
NIMS = [1, 2, 3]


class GameStatus(Enum):
    START = 0
    PASS = 1
    FAIL = 2
    WIN = 3
    LOSE = 4


class TriangleSolitaire:
    @staticmethod
    def sum_of_n(n):
        return int(n * (n + 1) / 2)

    @classmethod
    def valid_marker(cls, marker) -> bool:
        n = cls.sum_of_n(marker)
        return marker >= 0 and marker < n

    @classmethod
    def initial_state(cls, marker):
        n = cls.sum_of_n(marker)
        b = 0
        for i in range(n - 1):
            b |= 1 << i
        return b

    def __init__(
        self,
        marker_configuration: int | None = None,
        size: int | None = None,
    ):
        """Generate game board from given binary number

        Args:
            marker_configuration (int): the binary number as an integer
            size (int): the number of markers (triangles) along one side of the
            board
        """
        if (marker_configuration is None and size is None) or (
            marker_configuration is not None and size is None
        ):
            raise Exception("misconfigured state")

        self.__board_row_size = size or MIN_SIDE_LENGTH
        # sum of n ints
        self.__num_of_markers = self.sum_of_n(size)
        self.__selected_marker = 0

        # initial configuration
        self.__binary_number_state = marker_configuration or self.initial_state(size)

        self.__markers = [
            bool(1 << k & self.__binary_number_state)
            for k in range(self.__num_of_markers)
        ]

        # configure marker data
        self.__nims = [
            [NIMS[(j + (size - i)) % MAX_DEGREE] for j in range(size - i)]
            for i in range(size)
        ]

        self.__adjacency = []
        k = 0
        for i in range(len(self.__nims)):
            for j in range(len(self.__nims[i])):
                self.__adjacency.append(
                    {
                        fn(k)
                        for fn, cond in map(
                            lambda fn, cond: (fn, cond),
                            [
                                lambda k: k + 1,
                                lambda k: k - 1,
                                lambda k: k + size - i,
                                lambda k: k - size + i,
                                lambda k: k + size - i - 1,
                                lambda k: k - size + i - 1,
                            ],
                            [
                                lambda i, j: j < len(self.__nims[i]) - 1,
                                lambda i, j: j > 0,
                                lambda i, j: i < len(self.__nims)
                                and j < len(self.__nims[i]) - 1,
                                lambda i, j: i > 0,
                                lambda i, j: i < len(self.__nims) and j > 0,
                                lambda i, j: i > 0,
                            ],
                        )
                        if cond(i, j)
                        and self.valid_marker(fn(k), self.__num_of_markers)
                    }
                )
                k += 1

    def __format__(self, format_spec: str):
        """Provide args {b} and {nims}"""
        bin_ = 0
        nims = 0
        for m in self.__markers:
            bin_ |= int(m)
            bin_ <<= 1
        for nim in self.__nims:
            nims |= nim
            nims <<= 2

        return format_spec.format(b=bin_, nims=nims)

    def select_marker(self, marker: int):
        self.__selected_marker = (
            marker if self.__valid(marker) else self.__selected_marker
        )

    def try_jump(self, selected_marker: int, target_marker: int) -> int | None:
        """Returns the jump marker if successful, else None"""
        target_neighbors = self.__adjacency[target_marker]
        selected_neighbors = self.__adjacency[selected_marker]

        if selected_marker in target_neighbors or self.__markers[target_marker]:
            return None

        for i in range(self.__num_of_markers):
            if i in target_neighbors and i in selected_neighbors:

                # compare Nim values
                tnim = self.get_nim_value(target_marker)
                snim = self.get_nim_value(selected_marker)
                jnim = self.get_nim_value(i)

                # nim rules: XOR all values should be 0
                nim = tnim ^ jnim ^ snim
                if nim == 0:
                    return i

        return None

    def attempt_jump(
        self, target_marker: int, selected_marker: int | None = None
    ) -> bool:
        selected = selected_marker or self.__selected_marker
        jump_marker = self.try_jump(selected, target_marker)

        if jump_marker is not None:
            self.__markers[target_marker] = True
            self.__markers[self.__selected_marker] = False
            self.__markers[jump_marker] = False
            self.__selected_marker = target_marker
            return True

        return False

    def has_legal_moves(self) -> bool:
        for i in range(self.__num_of_markers):
            if self.__markers[i]:
                for n in self.__adjacency[i]:
                    if self.__markers[n]:
                        for t in self.__adjacency[n]:
                            if self.try_jump(i, t) is not None:
                                return True

        return False

    def get_nim_value(self, marker: int) -> int:
        i, j = self.__get_loc(marker)
        return self.__nims[i][j]

    def has_marker(self, marker: int) -> bool:
        return self.__markers[marker] if self.__valid(marker) else False

    def set_marker(self, marker: int, value: bool):
        if self.__valid(marker):
            self.__markers[marker] = value

    def get_selected_marker(self) -> int:
        return self.__selected_marker

    def __get_loc(self, marker: int) -> tuple[int, int]:
        i = 0
        j = 0
        k = 0
        while k + len(self.__nims[i]) <= marker:
            k += len(self.__nims[i])
            i += 1
        j = marker - k
        return (i, j)

    def __valid(self, marker: int) -> bool:
        return self.valid_marker(marker, self.__num_of_markers)


if __name__ == "__main__":
    import json
    import sys

    json_str = sys.argv[1]
    req: dict[str, Any] = json.loads(json_str)

    size = req.get("size", MIN_SIDE_LENGTH)
    marker_config = req.get("markers")
    proposal = req.get("proposal")

    game = TriangleSolitaire(marker_configuration=int(marker_config), size=int(size))

    if proposal is not None:
        if game.attempt_jump(
            selected_marker=int(proposal["source"]),
            target_marker=int(proposal["target"]),
        ):
            res_dict = {
                "markers": "{b}",
                "size": size,
                "nims": "{nims}",
                "status": GameStatus.PASS.name,
            }
