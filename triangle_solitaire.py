import os
from enum import Enum, auto

UNSELECTED_MARKER = -1

# triangles
MAX_DEGREE = 3
SIDE_LENGHTS = [5, 6, 8, 9]
MIN_SIDE_LENGTH = SIDE_LENGHTS[0]
NIMS = [1, 2, 3]


class GameStatus(Enum):
    START = 0
    PASS = auto()
    FAIL = auto()
    WIN = auto()
    LOSE = auto()


class TriangleSolitaire:
    @staticmethod
    def __pack_bits(markers: list[bool]) -> int:
        b = 0
        for i, m in enumerate(markers):
            b |= int(m) << i
        return b

    @staticmethod
    def __unpack_bits(marker_config: int, n: int) -> list[bool]:
        return [bool(1 << i & marker_config) for i in range(n)]

    @staticmethod
    def __sum_of_n(n):
        return int(n * (n + 1) / 2)

    @classmethod
    def __valid_marker(cls, marker, n) -> bool:
        return marker >= 0 and marker < n

    @classmethod
    def __initial_state(cls, n):
        b = 0
        for i in range(n - 1):
            b |= 1 << i
        return b

    def __init__(
        self,
        size: int = MIN_SIDE_LENGTH,
        marker_configuration: int | None = None,
    ):
        """Generate game board from given binary number

        Args:
            marker_configuration (int): the binary number as an integer
            size (int): the number of markers (triangles) along one side of the
            board
        """
        # sum of n ints
        self.__num_of_markers = self.__sum_of_n(size)
        self.__selected_marker = UNSELECTED_MARKER

        # initial configuration
        self.__binary_number_state = marker_configuration or self.__initial_state(
            self.__num_of_markers
        )

        self.__markers = self.__unpack_bits(
            self.__binary_number_state, self.__num_of_markers
        )

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
                        and self.__valid_marker(fn(k), self.__num_of_markers)
                    }
                )
                k += 1

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
        return self.__valid_marker(marker, self.__num_of_markers)

    def select_marker(self, marker: int):
        self.__selected_marker = (
            marker if self.__valid(marker) else self.__selected_marker
        )

    def unselect_marker(self):
        self.__selected_marker = UNSELECTED_MARKER

    def try_jump(self, selected_marker: int, target_marker: int) -> int | None:
        """Returns the jump marker if successful, else None"""
        target_neighbors = self.__adjacency[target_marker]
        selected_neighbors = self.__adjacency[selected_marker]

        if (
            selected_marker in target_neighbors
            or not self.has_marker(selected_marker)
            or self.has_marker(target_marker)
        ):
            return None

        for i in range(self.__num_of_markers):
            if i in target_neighbors and i in selected_neighbors and self.has_marker(i):

                # compare Nim values
                tnim = self.get_nim_value(target_marker)
                snim = self.get_nim_value(selected_marker)
                jnim = self.get_nim_value(i)

                # nim rules: XOR all values should be 0
                nim = tnim ^ jnim ^ snim
                if nim == 0:
                    return i

    def attempt_jump(
        self, target_marker: int, selected_marker: int | None = None
    ) -> bool:
        selected = selected_marker or self.__selected_marker
        jump_marker = self.try_jump(selected, target_marker)

        if jump_marker is not None:
            self.__markers[target_marker] = True
            self.__markers[selected] = False
            self.__markers[jump_marker] = False
            self.__selected_marker = selected
            self.__binary_number_state = self.__pack_bits(self.__markers)
            return True

        return False

    def has_legal_moves(self) -> bool:
        # TODO: better as bfs
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

    def get_score(self) -> int:
        return sum([int(i) for i in self.__markers])

    def get_state(self) -> tuple[int, int]:
        """Returns the current marker configuration and nims as integers"""

        bin_num_board = 0
        nims = 0
        for i in range(self.__num_of_markers):
            bin_num_board |= int(self.has_marker(i)) << i
            nims |= self.get_nim_value(i) << (2 * i)
        return (bin_num_board, nims)


def return_json(res_dict):
    # for now, just return to std out
    print(json.dumps(res_dict))


# for use as an external API
if __name__ == "__main__":
    import json
    import sys

    json_req = sys.argv[1]
    req_dict = json.loads(json_req)

    size = req_dict.get("size", MIN_SIDE_LENGTH)
    marker_config = req_dict.get("markers")
    proposal = req_dict.get("proposal")

    if proposal is not None:
        game = TriangleSolitaire(
            marker_configuration=int(marker_config), size=int(size)
        )

        if game.attempt_jump(
            selected_marker=int(proposal["source"]),
            target_marker=int(proposal["target"]),
        ):
            status = GameStatus.PASS
        else:
            status = GameStatus.FAIL

        if not game.has_legal_moves():
            score = game.get_score()
            status = GameStatus.LOSE if score > 1 else GameStatus.WIN
    else:
        game = TriangleSolitaire(size=size)
        status = GameStatus.START

    b, nims = game.get_state()

    res_dict = {
        "markers": b,
        "size": size,
        "nims": nims,
        "status": status.value,
    }

    return_json(res_dict)
