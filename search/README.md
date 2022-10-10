# Assignments 2 and 3
[Scroll to Assignment 3](#assignment-3-sokoban)

## Assignment 2: Uniform-cost search and Pac-Man

This assignment consists of two parts — implementing uniform-cost search and agent for Pac-Man game.

### 1. Uniform-cost search
Write general-purpose implementation of uniform-cost search in [ucs.py](ucs.py). It should be able to search any problems implementing `Problem` interface, that can be found in [search_templates.py](search_templates.py). The search should return `Solution` instance if solution is found, otherwise `None`.

Search method could be used like this:
```python
problem: Problem = SomeProblem()
solution: Solution = ucs(problem)
```

You can test your implementation on `Problem` instances from [problems.py](problems.py) script by running script [ucs_test.py](ucs_test.py) as it is.

#### Hints
- Create `Node` data structure that will hold nodes for the search.
  - [Dataclass](https://docs.python.org/3/library/dataclasses.html) might come in handy.
- Create `Path` data structure that will hold paths to `Node`s in a way that it can be easily extended and partially shared.
  - E.g. some kind of linked list with more heads.
- Create `Frontier` data structure that will work as a priority queue.
  - Module [`heapq`](https://docs.python.org/3/library/heapq.html#module-heapq) might come in handy.
- Make sure `Node` is "*comparable*".
  - If you decide to use `heapq`, pay attention to the [implementation notes](https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes).
- For storing explored set use data structure that lets you check quickly whether state is in the set.
- Solve the situation when your algorithm discovers a new path to a state that is already in the frontier.
  - There are some possible approaches:
  1. Check whether new path is cheaper. If it is you want to record it, but you cannot simply update the existing `Node`, because you also need to to change its position in the priority queue. Instead, you can remove existing frontier node and add a new one that represents cheaper path. With this approach you will never have duplicit nodes in the queue, but you will spend a lot of time managing the queue.
  2. Check whether new path is cheaper. If it is, then add a new node, but leave the existing in queue as well, to avoid expensive remove operation. With this approach, there may be multiple nodes in the queue that represent the same state. Because of that, when you remove a node from the queue, you need to check whether its state was already explored (e.g. by checking explored set) and if so you should ignore the node.
  3. Always add a new node and handle duplicity as in approach (2). With this approach, you will have more duplicate nodes in the queue than in approach (2).
  - With approach (1) or (2), you will need some quick way to check whether a given state is already in the frontier (and to access its path cost). One way to do that is to use `dict` to keep a map from states to a needed information.


### 2. Pac-Man
In this part of the assignment, you write an agent that plays Pac-Man.

Continue to [Pac-Man info](pacman/README.md).


## Assignment 3: A* and Sokoban

This assignment consists of two parts — implementing A* search and agent for Sokoban game.

### 1. A* search

Write general-purpose implementation of A* search in [astar.py](astar.py). It should be able to search any problems implementing `HeuristicProblem` interface (can be found in [search_templates.py](search_templates.py)), that extends `Problem` from previous assignment by method `estimate`. The search should return `Solution` instance if solution is found, otherwise `None` (as in the previous assignment).

Search method could be used like this:
```python
problem: HeuristicProblem = SomeProblem()
solution: Solution = AStar(problem)
```

You can test your implementation on `HeuristicProblem` instances from [problems.py](problems.py) script by running script [astar_test.py](astar_test.py) as it is.

Note that it would be wise to ensure that your A* implementation returns optimal solutions to these test problems before you apply it to Sokoban. You should be able to solve second 15-puzzle instance from the test in about a minute. If it takes significantly longer, your A* implementation is not working as efficiently as it should.

#### Hints
- A* is a variation of UCS, so you will need to make only a few changes to your UCS implementation.
- Your `Node` data structure should be comparable by its f-cost, defined as $f(n) = g(n) + h(n)$, where $g(n)$ is the path cost and $h(n)$ is the heuristic estimate.
- Do not compute heuristic estimate on every comparison.
- For debugging, print out the number of explored nodes and compare it with comments in test script.

### 2. Sokoban
In this part of the assignment, you write an agent that plays Sokoban.

Continue to [Sokoban info](sokoban/README.md).
