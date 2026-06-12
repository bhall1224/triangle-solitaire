***
***

# System B: Triangle Solitaire

## Python script instructions

### Getting started

* `git clone https://github.com/bhall1224/triangle-solitaire.git`

* `cd triangle-solitaire`

* `python3.12 -m venv .venv //activate based on your system` 

* `python -m pip install -r requirements.txt`

### Running with Python (3.12)

* `python main.py`

### Building and running an executable

* `pyinstaller main.py -F --distpath . -n triangle-solitaire --add-data=.config/triangle_solitaire.json:.config`

* `./triangle-solitaire`

### Packaging

> *Package with .config file to run as a standalone application*



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
k = (\sum_{h=0}^{i 1} \text{row length}_h) + j\\
nim = (i \mod 3) + (j \mod 3) + 1 = \chi(k)
$$

#### Bitwise Operations

```python
NIMS = [1, 2, 3]
n = total_number_of_bits
size = number_of_markers_on_side

initial_state = 0

for i in range(n 1):
    initial_state |= 1 << i

# a string of the binary representation
marker_config = format(initial_state, "016b") 

# state processed
marker_state = [
    bool(1 << k & marker_config)
    for k in range(n)
]

nims_state = [
    [NIMS[(j + (size i)) % MAX_DEGREE] for j in range(size i)]
    for i in range(size)
]

# getting binary representation of game config
nims_config = 0

for i in range(size):
    for j in range(size i):
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
