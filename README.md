# heat

A verified finite-difference scheme for the 1-D heat equation, written in Lean 4.
The same Lean code is both proved correct and compiled for use from Python.

The scheme is FTCS (forward time, centred space) with periodic boundaries:

    u'[i] = u[i] + r * (u[i-1] - 2*u[i] + u[i+1])

where `r = α Δt / Δx²`. It is stable for `r ≤ 0.5`.

## Components

| File | What it is |
|---|---|
| [HeatCore.lean](HeatCore.lean) | The executable scheme: `ftcs_stencil`, `scheme` (one step over the whole grid) and `run` (many steps). It is generic over any numeric type and uses `Vector a n` indexed by `Fin n`, so periodic wrap-around comes from `Fin` arithmetic. It also proves that the tail-recursive `runTR` equals `run`, and tells the compiler to use `runTR` via `@[csimp]`, so long runs don't overflow the stack. It doesn't depend on Mathlib. |
| [heat.lean](heat.lean) | Proofs about the scheme, using Mathlib: `scheme_conserves` and `run_conserves` show that total heat `∑ u[i]` is conserved exactly, over any commutative ring. |
| [HeatFFI.lean](HeatFFI.lean) | Specialises `run` to `Float` on a `FloatArray` whose length is only known at run time, and exports it to C as `heat_run_float_array`. |
| [python/heat_shim.c](python/heat_shim.c) | A small C layer that starts the Lean runtime (`heat_init`) and copies arrays in and out of Lean (`heat_run`). |
| [python/build.sh](python/build.sh) | Builds `HeatCore` + `HeatFFI` as a static library and links it with the shim and the Lean runtime into `python/libheat.dylib` (macOS) or `python/libheat.so` (Linux). |
| [python/heat_lean.py](python/heat_lean.py) | Python bindings (ctypes + numpy): `heat_lean.run(u, r, steps)`. |
| [python/test_heat_lean.py](python/test_heat_lean.py) | Tests: checks the Lean output against a numpy implementation, checks conservation, edge cases (empty and non-contiguous arrays), and 10⁶ steps without stack overflow. |
| [python/visualise.py](python/visualise.py) | Plots a simulation computed by the Lean code: a space-time heatmap and profiles over time (`heat.png`), plus an optional animation (`heat.gif`). |
| [lakefile.toml](lakefile.toml) | Lake build config. Defines two libraries: `heat` (the proofs, the default target) and `HeatFFI` (the executable core for the bindings). |
| [Example.agda](Example.agda) | A small standalone Agda example. It isn't part of the build. |

Because the Python bindings call the compiled Lean `run` itself, the code that
runs is the code the proofs are about. The trust gap is the usual one: `Float`
arithmetic is IEEE-754, not exact, so `run_conserves` (proved over rings) holds
for `Float` only up to rounding.

## Dependencies

- **Lean 4** via [elan](https://github.com/leanprover/elan). The toolchain
  version is pinned in [lean-toolchain](lean-toolchain) (`v4.34.0`), and elan
  installs it automatically.
- **Mathlib** `v4.34.0`, fetched by Lake. Only the proofs in `heat.lean` need it,
  but Lake downloads it the first time you build either target.
- **A C compiler** (`cc`: clang on macOS, gcc on Linux) for the Python shared library.
- **Python 3.8+** with the packages in [python/requirements.txt](python/requirements.txt)
  (numpy, matplotlib).

## Building and running

### 1. Check the proofs

```sh
lake exe cache get   # download prebuilt Mathlib (saves a very long build)
lake build           # builds and checks heat.lean + HeatCore.lean
```

If the build succeeds, every proof has been checked.

### 2. Build the Python library

```sh
./python/build.sh    # -> python/libheat.dylib or python/libheat.so
```

This runs `lake build HeatFFI:static` and then links the result into one
self-contained shared library, which includes the Lean runtime. Re-run it after
changing `HeatCore.lean` or `HeatFFI.lean`.

### 3. Set up Python

```sh
cd python
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
```

### 4. Use, test, visualise

All from inside `python/`:

```sh
python3 -c "import numpy as np, heat_lean; print(heat_lean.run(np.array([0., 0., 1., 0., 0.]), r=0.25, steps=1))"
# [0.   0.25 0.5  0.25 0.  ]

python3 test_heat_lean.py     # or: pytest (if installed)

python3 visualise.py          # writes heat.png
python3 visualise.py --gif    # also writes heat.gif
python3 visualise.py --n 400 --r 0.4 --steps 20000 --every 20
```

`visualise.py` options: `--n` grid points (default 200), `--r` coefficient
(0.25), `--steps` total time steps (5000), `--every` steps between recorded
snapshots (5), `--out` output file (`heat.png`).

## GitHub configuration

To set up your new GitHub repository, follow these steps:

* Under your repository name, click **Settings**.
* In the **Actions** section of the sidebar, click "General".
* Check the box **Allow GitHub Actions to create and approve pull requests**.
* Click the **Pages** section of the settings sidebar.
* In the **Source** dropdown menu, select "GitHub Actions".

After following the steps above, you can remove this section from the README file.
