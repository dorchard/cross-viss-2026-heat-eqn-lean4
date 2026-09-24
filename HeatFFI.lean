import HeatCore

-- C-callable entry point for `run` at type `Float`, over arrays whose
-- length is only known at runtime (e.g. numpy arrays).

def runFloatArray (r : Float) (steps : Nat) (xs : FloatArray) : FloatArray :=
  if h : xs.size = 0 then xs else
  haveI : NeZero xs.size := ⟨h⟩
  let u : Vector Float xs.size := Vector.ofFn (fun i => xs[i])
  ⟨(run r steps u).toArray⟩

@[export heat_run_float_array]
def heatRunFloatArray (r : Float) (steps : USize) (xs : FloatArray) : FloatArray :=
  runFloatArray r steps.toNat xs
