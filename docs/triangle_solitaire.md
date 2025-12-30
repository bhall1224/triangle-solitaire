***
***

# System B: Triangle Solitaire

## Python script instruction

Send the ***TriangleProcessInput*** request as an escaped JSON string passed as a command-line argument.  It will be deserialized and processed by the script, which will return ***TriangleProcessOutput*** as an escaped JSON string

### TriangleProcessInput:


```yaml
size:
    type: int
    description: Number of markers/triangles along one side of the board
    Optional, default = 5

markers:    
    type: int
    description: Binary representation of marker placement on game board
    Optional, omit for initial state
    ex: 0b'00111111111111111' represents the opening configuration of the
    game board. 0b'0100000000000000' represents a perfect reconfiguration

proposal:
    type: object
    description: The source and target bit proposed, representing markers
    on the board
    - source:
        type: int
        description: Source bit from board
    - target:
        type: int
        description: Target bit from board
```

### TriangleProcessOutput:

```yaml
markers:
    type: int
    description: Binary representation of marker placement on game board
    ex: 0b'00111111111111111' represents the opening configuration of the game board.
    0b'01000000000000000' represents a perfect reconfiguration. Only N bits needed

nims:
    type: int 
    description: Binary representation of Nim values. Nim values are 1, 2, or 3;
    representing a color class of a 3-colorable graph. Used to calculate jumps.
    See Rules section
    ex: [1, 2, 3] => 011011

size:
    type: int
    description: Number of markers/triangles along one side of the board. 
    Boards of size 3(size) + 1 aren't solvable, and we limit the scope of 
    difficulty by allowing only these values
    ex: 5, 6, 8, or 9

status:
    type: enum
    description: START, PASS, FAIL, WIN, LOSE
    ex: Status of PASS or FAIL for jump proposals. WIN if only one marker remains
    LOSE otherwise. START for initial configurations
```


## Rules

* A board is given an initial configuration of markers

    - All but one board location is placed with a marker

* A series of transformations are applied to the marker configuration

    - A marker may "jump" another marker to an unoccupied space, and the "jump" marker is removed

* The game is complete when no more "jumps" are possible

* Try to figure out a series of transformations such that only one marker remains.

## Playing the game

Invoke the script with `python trianle_solitaire.py [args]`.

>       Accepts and returns JSON strings of the models defined above.
>       If no args are given, a size of 5 is assumed and a status of START is returned.
>       If the request is malformed, an error is raised

1. Use a request with null markers and given size to generate a game board.  Returns START status and opening marker configuration

2. Send a return request with the given marker config and size, with a jump proposal

3. Proposals are a source and target bit, and the process will return a new configuration and PASS if proposal is accepted, otherwise the provided configuration with a status of FAIL

4. The game is over when you no longer have legal moves available.  The number of markers left is your score.  If you have 1 left, you get a status of WIN! Otherwise it's a big ol' LOSE...

>       You will have to do some maths to figure out if your move is valid

## Maths

$\text{Let}\ \bm{\beta} = \text{some binary number,}\ \text{and}\ k = \text{some bit of}\ \beta$

$\bm{\beta}\ = \set{k_0,\ k_1,\ ...\ k_n}\ \text{for}\ \bm{n}\ \text{bits in}\ \beta$

$\bm{M}\ = \set{M(k_0),\ M(k_1),\ ...\ M(k_n)}$

$\text{A}\ \bm{Marker}\ \text{at position}\ \bm{k}\ \text{is occupied if bit}\ k=1\text{:}$

$M(k_i)\ = \text{is occupied}\ \iff\ \beta(k_i)\ = 1$

```
Let B = 0011111111111111

B:
    0
   1 1
  1 1 1
 1 1 1 1
1 1 1 1 1
```

$k\ \in\ \beta$

```
      14
    12  13
   9  10  11
 5   6   7   8
0  1   2   3  4
```

$M(k)\ \text{for}\ k\ \in\ \beta$

```
    F
   T T
  T T T
 T T T T
T T T T T
```

### Nim Arithmetic*

$\bm{Nims}\ = \set{p,\ q,\ r}$

$p,\ q,\ \&\ r\ \in\ \mathbb{Z}$

$p=1,\ q=2,\ \&\ r=3$

$p\ \hat +\ q\ \hat +\ r\ = 0$
$\text{defined as bitwise modulo 2 arithmetic, no carry}$

$\implies\ p=01,\ q=10,\ \&\ r=11$


$\implies\ p\ \hat +\ q\ \hat +\ r\ \equiv\ 01 \oplus\ 10 \oplus\ 11 = 0$


$\text{Let}\ \chi(k)\ \text{be a function of bit}\ k\text{:}$
$\chi(k)\ \in\ Nims$

$\text{then applying}\ \chi(k)\ \text{for each}\ k\ \text{in}\ \beta\text{:}$

```
    r
   p q
  q r p
 r p q r
p q r p q


    3
   1 2
  2 3 1
 3 1 2 3
1 2 3 1 2
```

$\text{Consider source bit}\ \bm{s},\ \text{jump bit}\ \bm{j},\ \text{and target bit}\ \bm{t}\text{:}$

$\bm{N}(k)\ = \text{markers adjacent to}\ M(k)$

$\text{A valid jump from}\ \bm{M(s)}\ \text{to}\ \bm{M(t)}\ \text{removes}\ \bm{M(j)}\ \iff$

$$
\beta(s)=1,\ \beta(j)=1,\ \beta(t)=0\\
j\ \in\ N(s),\ j\ \in\ N(t),\ s\ \notin\ N(t),\ \&\\
\chi(s)\ \hat +\ \chi(j)\ \hat +\ \chi(t)\ =\ 0
$$

#### Calculating Nim Values

$\forall\ k \in\ \beta,\ \exists\ nim\ \in\ Nims\..$

$$
\chi(k)\ = nim\\
\text{Let}\ i,\ j\ \in\ \mathbb{Z},\ \text{for board locations on row}\ i\ \text{and column}\ j\\
k = (\sum_{h=0}^{i - 1} \text{row length}_h) + j\\
nim = (i \mod 3) + (j \mod 3) + 1 = \chi(k)
$$

#### Bitwise Operations

```python
NIMS = [1, 2, 3]
n = total_number_of_bits
size = number_of_markers_on_side

initial_state = 0

for i in range(n - 1):
    initial_state |= 1 << i

# a string of the binary representation
marker_config = format(initial_state, "016b") 

# state processed
marker_state = [
    bool(1 << k & marker_config)
    for k in range(n)
]

nims_state = [
    [NIMS[(j + (size - i)) % MAX_DEGREE] for j in range(size - i)]
    for i in range(size)
]

# getting binary representation of game config
nims_config = 0

for i in range(size):
    for j in range(size - i):
        nims_config |= nim_state[i][j]
        nims <<= 2 # each nim is two bits long

for i in range(n):
    marker_config |= int(marker_state[i])
    marker_config <<= 1 
```

---

>*Read more: [Mathematical Games and How to Play Them](https://books.google.com/books?id=RinvAAAAMAAJ&source=gbs_book_other_versions_r&cad=2)

---
---
