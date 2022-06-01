# Assignments 2 and 3
[Scroll to Assignment 3](#assignment-3-sokoban)

## Assignment 2: Uniform-cost search and Pac-Man

This assignment consist of two parts — implementing uniform-cost search and agent for Pac-Man game.
### 1. Uniform-cost search
Write general-purpose implementation of uniform-cost search in [ucs.py](ucs.py). It should be able to search any problems implementing `Problem` interface, that can be found in [search_templates.py](search_templates.py). The search should return `Solution` instance if solution is found, otherwise null.

Search method could be used like this:
```python
problem: Problem = SomeProblem()
solution: Solution = ucs(problem)
```

You can test your implementation on `Problem` instances from [problems.py](problems.py) script by running script [ucs_test.py](ucs_test.py) as it is.

#### Hints
- Create `Node` data structure that will hold nodes for the search.
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
