module Example where

open import Data.Product
open import Relation.Binary.PropositionalEquality

lemma : {A B C : Set}
      → (A × B → C)
      → (A → (B → C))
lemma f = λ z z₁ → f (z , z₁)




-- A Hello world example?

-- Depends on our representation of integers
-- For now let's do natural numbers

data Nat : Set where
  Zero : Nat
  Succ : Nat -> Nat

-- Peano arithmetic
_+_ : Nat -> Nat -> Nat
Zero     + n = n
(Succ n) + m = Succ (n + m)

rightUnit : forall (n : Nat) -> n + Zero ≡ n
rightUnit Zero = refl
rightUnit (Succ n) =
 let ih = rightUnit n
 in cong Succ ih
