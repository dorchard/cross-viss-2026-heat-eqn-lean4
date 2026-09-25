/-!
  Machine-checked proof that the `add` function from `add.py`
  correctly adds two integers.
  `addFn` below is a 1-to-1 formal model of the Python function
      def add(a: int, b: int) -> int:
          return a + b
  Lean's `Int` is the set of mathematical integers ℤ (arbitrary
  precision), exactly matching Python's `int`, which also implements
  exact, unbounded integer arithmetic. Because addition in `add.py`
  is literally `a + b`, correctness of the model below carries over
  to the Python function. The only trusted link (as in any
  model-based verification) is that CPython's `int.__add__`
  implements exact ℤ addition.
-/

/-- Formal model of `add(a, b)` from `add.py`: returns the sum of two integers. -/
def addFn (a b : Int) : Int := a + b

/-- **Correctness.** For *all* integers `a` and `b`, `addFn` returns the
    integer sum of its arguments. Proved by definitional unfolding:
    the function *is* integer addition. -/
theorem addFn_correct (a b : Int) : addFn a b = a + b := rfl

/-- Commutativity: the order of arguments does not matter. -/
theorem addFn_comm (a b : Int) : addFn a b = addFn b a := Int.add_comm a b

/-- Associativity: nested calls can be regrouped freely. -/
theorem addFn_assoc (a b c : Int) : addFn (addFn a b) c = addFn a (addFn b c) :=
  Int.add_assoc a b c

/-- Right identity: adding `0` returns the argument unchanged. -/
theorem addFn_zero (a : Int) : addFn a 0 = a := Int.add_zero a

/-- Left identity: `0` added to anything returns it unchanged. -/
theorem addFn_left_zero (a : Int) : addFn 0 a = a := Int.zero_add a

/-- Additive inverse: `a + (-a) = 0`. -/
theorem addFn_neg (a : Int) : addFn a (-a) = 0 := Int.add_right_neg a

/-- Concrete check matching the demo in `add.py`: `add(3, 5)` is `8`. -/
theorem addFn_demo : addFn 3 5 = 8 := by decide

theorem add_congruence :
   (a <= b) → (c <= d) → (addFn a c) <= (addFn b d) := by
    intros pre1 pre2
    unfold addFn
    apply Int.add_le_add
    . exact pre1
    . exact pre2

-- Executable cross-check; expected output: `8`.
#eval addFn 3 5

-- Axiom report: a sound proof must not depend on any axioms (no `sorry`).
#print axioms addFn_correct
