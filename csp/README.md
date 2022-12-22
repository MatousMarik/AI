# Assignment 5: Minesweeper

This assignment has two parts — implementation of BooleanCSP solver and implementation of Minesweeper agent.

[SKIP TO MINESWEEPER](#2-minesweeper)

## 1. CSP solver

Implement CSP solver.

### Boolean constraint satisfaction problem

You will be solving a constraint satisfaction problem of the following nature:
- There is a set of variables $X = {X_0, ..., X_{n-1}}$.
- All variables are boolean — their domains are $\lbrace True, False \rbrace$
- There is a set of constraints, where each constraint $C_i$ consists of:
  - A subset of variables that participate in the constraint.
  - An integer $k$ indicating that **exactly** $k$ of these variables are $True$

For example, here is one such problem:
- 4 variables $X_0 ... X_3$
- 4 constraints:
  - $\lbrace X_0, X_1 \rbrace$: 1
  - $\lbrace X_1, X_2 \rbrace$: 1
  - $\lbrace X_2, X_3 \rbrace$: 1
  - $\lbrace X_0, X_2, X_3 \rbrace$: 2

It is not difficult to see that this problem has an unique solution:
- $X_0 = True, X_1 = False, X_2 = True, X_3 = False$

In this part of the assignment, you will write a solver for this kind of CSP.

The problems are implemented through the `BooleanCSP` class and the constraint through `Constraint`, both in [csp_templates.py](csp_templates.py).

The CSP is defined by:
- *num_vars* — the number of variables in the problem, numbered 0 to (*num_vars* - 1)
- *value[v]* — is initially `None` for all variables *v*, meaning their value is unknown. Solver will assign `True` or `False` values to variables by storing them in this list.
- *constraints* — the current set of constraints. Constraints may be added over time (which will be useful in solving Minesweeper).

You solver can also use:
- *var_constraint* — maps variable identifying numbers to a set of constraints that affect the respective variables.
- *unchecked* — a queue that contains all constraints that have not yet been **forward checked**, 	i.e. constraints from which you may be able to immediately infer variable values.

`BooleanCSP` also contains these methods:
- *add_constraint* — add a new constraint to the problem (and to *unchecked*).
- *set* — set a variable's value and add its constraints to *unchecked*

### Task
Your task is to implement a CSP solver in [solver.py](solver.py), that consists of three methods:

#### `forward_check`
This method should infer as many variable values as possible by performing **constraint propagation** as described in section 6.2 of the Russell & Norvig textbook ("Constraint Propagation: Inference in CSPs"). Its implementation will be loosely similar to the AC-3 algorithm described in the text. However, AC-3 handles binary constraints, and so `forward_check` will infer variable values differently because the constraints in a BooleanCSP are of a different nature.

Specifically, this method should check the queue of constraints in csp.unchecked to see if it can infer any variable values from any single constraint. As new variable values are discovered, those variables' constraints will join the queue to be checked in turn. The constraint propagation process will complete when the queue is empty. This method should return a list of variables whose values were inferred. If it realizes that some constraint can not be satisfied, that means that a contradiction has been reached and the entire system is unsolvable. In this case, `forward_check` should **reset any variables that it has set** and return `None`.

As an example of how constraint propagation might work, suppose that the queue initially contains three constraints: 1 of {0 1 2}, 1 of {2 3}, and 0 of {3}. And suppose that at the beginning, no values are known, i.e. every variable's domain is {true, false}. You will first remove '1 of {0 1 2}' from the queue and examine it. You can't infer any values from this constraint alone, so you will ignore it and move on. You'll next look at '1 of {2 3}'. Again, you can't infer anything from this constraint in isolation, so it simply falls out of the queue.

Now the queue contains only '0 of {3}'. From looking at this constraint, you immediately know that 3 = false. You now re‑add '1 of {2 3}' to the queue, since it is a constraint that involves variable 3. Now the queue contains only '1 of {2 3}'. From looking at this constraint, you now know that 2 = true since exactly 1 of {2 3} is true, but 3 is false. So you will now re‑add '1 of {0 1 2}' to the queue, since it is a constraint that involves variable 2, which you just inferred.

Now you'll examine '1 of {0 1 2}'. Since 2 is known to be true, this constraint now tells you that 0 = false and 1 = false. Now the queue is empty. You were able to infer the values of all variables through constraint propagation alone - you didn't need to perform any backtracking.

#### `solve`

Should attempt to find **any** solution to the CSP by performing a **backtracking search** as described in section 6.3 "Backtracking Search for CSPs". If it finds a solution, it should set values for all variables in the solution and return a list of those variables. If it determines that the system is unsolvable, it should **reset any variables that it has set** and return `None`.

For selecting the next variable to try in the backtracking search (i.e. the Select-Unassigned-Variable() step in the pseudocode in the text), I recommend using the **degree heuristic** described in section 6.3.1 "Variable and value ordering".

During the backtracking search, for efficiency you should perform forward checking as described in section 6.3.2 "Interleaving search and inference" in the text. (This is the Inference() step in the backtracking pseudocode). Specifically, you will want to use the technique that the textbook calls **maintaining arc consistency**, i.e. performing full constraint propagation after you select a variable value to try. You can do this by calling the `forward_check` method that you wrote before.

For efficiency, `solve` should ignore any variables that do not belong to any constraint (these variables may have any value, of course).

#### `infer_var`
This method should attempt to infer the value of any single variable in the CSP using a **proof by contradiction**, which works as follows. For each variable in turn, the method should set the variable's value to True and then call `solve` to test whether the resulting system has any solution. If the system is unsolvable, the method can infer that the variable **must be False** in any solution. Otherwise, it can try setting the variable to False; if that yields an unsolvable system, the method will infer that the variable must be True. As soon as a value is inferred for any variable, the method should stop the search process and return the index of that variable. If no value can be inferred for any variable, return -1. This method should not set values for any variables other than the variable that is returned (if any).

In this method, I recommend trying all variables in descending order of the number of constraints they belong to (this is the degree heuristic again). Do not bother to try to infer values for values with no constraints; that will never succeed.

To illustrate the use of these methods, we create a `BooleanCSP` instance of the problem above:
```python
csp = BooleanCSP(4)
csp.add_constraint(Constraint(1, [0, 1]))
csp.add_constraint(Constraint(1, [1, 2]))
csp.add_constraint(Constraint(1, [2, 3]))
csp.add_constraint(Constraint(2, [0, 2, 3]))
```

Let's attempt to infer values by constraint propagation alone:
```python
solver = Solver()
variables = solver.forward_check(csp)
print(variables)
```

This will print "`[]`" since no values can be inferred from any individual constraint. In other words, the system is **locally consistent** with respect to individual constraints.

So if we'd like to infer a variable value, we need to use a more powerful tool:
```python
var = solver.infer_var(csp)
print(f"var = {var}, value = {csp.value[var]}")
```

Which might print 

    var = 2, value = True

Now that we have inferred one value, constraint propagation can easily find the rest:

    variables2 = solver.forward_check(csp)
    for vi, v in enumerate(csp.value):
        print(f"var = {vi}, value = {v}")

That should print:

    var = 0, value = True
    var = 1, value = False
    var = 2, value = True
    var = 3, value = False

Alternatively, we could have called `solve`, which would find the same solution. However, note an important difference between these approaches. `solve` searches for any solution to a CSP and returns it. By contrast, `forward_check` and `infer_var` infer variable values that must be true in every solution of a CSP. And so our calls to `forward_check` and `infer_var` have proven that the above solution is unique.

#### Hint
- Whenever you set a variable's value, call csp.set() so that the variable's constraints will be added to the unchecked queue.
  
#### Testing
- Running script [solver_test.py](solver_test.py) will test your implementation of `forward_check`, `solve` and `infer_var` on a number of constraint satisfaction problems (including some that were derived from Minesweeper game boards).

## 2. Minesweeper
![minesweeper](minesweeper/mine.png)

Write an agent that plays Minesweeper. As always in this tutorial you may use any technique you like, but probably it will be easiest to use the CSP solver you just wrote. 

Before you start implementing, you should check [documentation](minesweeper/game/doc.md).

You have to implement your agent as a subclass of `ArtificialAgent` — implement its core logic in `think_impl`. Note that you should not change any existing functionality. You can use the prepared script [minesweeper/agents/agent.py](minesweeper/agents/agent.py).

To evaluate your agent run [minsweeper/play_mine.py](minesweeper/play_mine.py) with selected options. Your agent should be able to solve randomly generated boards of size 50x50 with 500 mines in less than 3 seconds (can differ greatly since its Python) and asking for about 5 hints on average. You can test that by running:

    python3 play_mine.py -a Agent -s 20 --impossible

For board 50x50 you will typically need 1-10 hints but occasionally even 20.

### Hints
- Create a `BooleanCSP` instance with one variable for each tile.
- The first time you see any free tile, call `csp.set()` to set its value to False, since you know there is no mine there. Also, if the tile has a non-zero number, create a Constraint representing the mines around it and call `add_constraint()` to add it to your CSP.
- To infer variable values, first try forward checking. If that returns a set of variable assignments, remember them so that you can return one on each subsequent call to `think_impl()`. If forward checking fails, try calling `infer_var()` which is more powerful but slower. Remember that after `infer_var()` succeeds, forward checking can often find more variable values quickly, using the newly inferred value as a starting point. If `infer_var()` fails, you will have to ask for a hint.
- First test your solver on tiny boards (e.g. 3 x 3 or 4 x 4). Once you are confident it works there, proceed gradually to larger boards in your testing.
- Here are the minimum numbers of hints required for the first 5 random seeds on several small board sizes. If your solver asks for more hints than these, it is not inferring as much as it could. (Method main is called with `["-a=Agent", "-s=5", "--seed=0", "-v=1"]` as argument.)

        $ python3 play_mine.py --size 3
        board size is 3 x 3, 2 mines
        seed 0: solved in 0.000 s, hints = 1
        seed 1: solved in 0.000 s, hints = 1
        seed 2: solved in 0.000 s, hints = 1
        seed 3: solved in 0.001 s, hints = 2
        seed 4: solved in 0.001 s, hints = 3

        $ python3 play_mine.py --size 5
        board size is 5 x 5, 5 mines
        seed 0: solved in 0.002 s, hints = 3
        seed 1: solved in 0.000 s, hints = 1
        seed 2: solved in 0.001 s, hints = 1
        seed 3: solved in 0.007 s, hints = 6
        seed 4: solved in 0.001 s, hints = 3

        $ python3 play_mine.py --size 7
        board size is 7 x 7, 10 mines
        seed 0: solved in 0.006 s, hints = 3
        seed 1: solved in 0.012 s, hints = 6
        seed 2: solved in 0.001 s, hints = 1
        seed 3: solved in 0.004 s, hints = 2
        seed 4: solved in 0.008 s, hints = 6

        $ python3 play_mine.py --size 9
        board size is 9 x 9, 16 mines
        seed 0: solved in 0.038 s, hints = 3
        seed 1: solved in 0.002 s, hints = 1
        seed 2: solved in 0.011 s, hints = 4
        seed 3: solved in 0.003 s, hints = 3
        seed 4: solved in 0.002 s, hints = 1

### Game controls
During visualization you can show the next move by *mouse-click*. When playing, you use *left-click* to uncover a tile, *right-click* to flag/unflag a tile and *H* for hint.

### ReCodEx testing
You are expected to submit two files. Your implementation of the CSP solver in solver.py and an agent playing the minesweeper game.

The first set of tests examines your CSP implementation, namely all three functions you are tasked to implement. The tests are the same as the tests available in solver_test.py. 

The second test plays 25 rounds of the minesweeper game on hard difficulty ("--hard"). Your implementation needs to be able to play fast enough to pass the recodex time limits and also good enough that it does not ask for too many hints. If the average number of hints from the 25 games is less or equal to 5, you receive full points. If the average number of hints from the 25 games is more than 8, you receive no points. In other cases, the number of points is scaled.

