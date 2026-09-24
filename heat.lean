import Mathlib

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

-- Shifting the index is a bijection on Fin n, so it does not change the sum
lemma sum_shift [AddCommMonoid a] [NeZero n] (u : Vector a n) (k : Fin n) :
    ∑ i : Fin n, u[i + k] = ∑ i : Fin n, u[i] :=
  Equiv.sum_comp (Equiv.addRight k) (fun i => u[i])

lemma sum_shift_sub [AddCommMonoid a] [NeZero n] (u : Vector a n) (k : Fin n) :
    ∑ i : Fin n, u[i - k] = ∑ i : Fin n, u[i] :=
  Equiv.sum_comp (Equiv.subRight k) (fun i => u[i])

-- Conservation of energy for a single step
theorem scheme_conserves [CommRing a] [NeZero n] (r : a) (u : Vector a n) :
    ∑ i : Fin n, (scheme r u)[i] = ∑ i : Fin n, u[i] := by
  simp only [scheme, ftcs_stencil, Fin.getElem_fin, Vector.getElem_ofFn]
  rw [Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_add_distrib,
      Finset.sum_sub_distrib, ← Finset.mul_sum]
  have h1 := sum_shift_sub u 1
  have h2 := sum_shift u 1
  simp only [Fin.getElem_fin] at h1 h2
  rw [h1, h2]
  ring

-- Conservation of energy for any number of steps
theorem run_conserves [CommRing a] [NeZero n] (r : a) (m : Nat) (u : Vector a n) :
    ∑ i : Fin n, (run r m u)[i] = ∑ i : Fin n, u[i] := by
  induction m with
  | zero => rfl
  | succ m ih => rw [run, scheme_conserves, ih]
