-- Executable definitions for the heat equation scheme.
-- Kept free of Mathlib so that they can be compiled and linked
-- (e.g. into a Python extension) without pulling in Mathlib.

class abbrev Numerical (a : Type u) := Add a, Sub a, Mul a, OfNat a 2

def get (u : Vector a n) (j : Fin n) : a :=
  u[j]

-- Single step stencil
-- with periodic boundaries automatic by the use
-- of Fin n.
def ftcs_stencil [Numerical a] [NeZero n]
  (r : a) (u : Vector a n) (i : Fin n) : a :=
  u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1])

-- Applying it everywhere spatially
def scheme [Numerical a] [NeZero n]
   (r : a) (u : Vector a n) : Vector a n :=
   Vector.ofFn (fun j => ftcs_stencil r u j)

-- Apply it temporally
def run [Numerical a] [NeZero n]
  (r : a) : Nat -> (u : Vector a n) -> Vector a n
  | 0    , u => u
  | m + 1, u => scheme r (run r m u)

-- Tail-recursive version of `run`, used for compiled code so that
-- a large number of steps does not overflow the stack.
def runTR [Numerical a] [NeZero n]
  (r : a) : Nat -> (u : Vector a n) -> Vector a n
  | 0    , u => u
  | m + 1, u => runTR r m (scheme r u)

theorem run_scheme [Numerical a] [NeZero n] (r : a) (m : Nat) (u : Vector a n) :
    run r m (scheme r u) = scheme r (run r m u) := by
  induction m with
  | zero => rfl
  | succ m ih => simp only [run, ih]

theorem runTR_eq_run [Numerical a] [NeZero n] (r : a) (m : Nat) (u : Vector a n) :
    runTR r m u = run r m u := by
  induction m generalizing u with
  | zero => rfl
  | succ m ih => simp only [runTR, run, ih, run_scheme]

-- The compiler replaces `run` by the (proven equal) `runTR`.
@[csimp] theorem run_eq_runTR : @run = @runTR := by
  funext a _ n _ r m u
  exact (runTR_eq_run r m u).symm
