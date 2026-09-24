"""Python bindings for the verified heat-equation scheme in HeatCore.lean.

Build the shared library first with ./build.sh. Then:

    import numpy as np, heat_lean
    u = heat_lean.run(np.array([0., 0., 1., 0., 0.]), r=0.25, steps=10)
"""
import ctypes
import os
import sys

import numpy as np

_ext = "dylib" if sys.platform == "darwin" else "so"
_lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"libheat.{_ext}"))

_lib.heat_init.restype = ctypes.c_int
_lib.heat_init.argtypes = []
_lib.heat_run.restype = ctypes.c_int
_lib.heat_run.argtypes = [
    ctypes.c_double,
    ctypes.c_size_t,
    np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS"),
    np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS"),
    ctypes.c_size_t,
]

if _lib.heat_init() != 0:
    raise RuntimeError("failed to initialise the Lean runtime")


def run(u, r, steps):
    """Apply `steps` FTCS steps (periodic boundaries) with coefficient r to a 1-D array.

    Calls the Lean function `run` at type Float. Returns a new float64 array.
    """
    if steps < 0:
        raise ValueError("steps must be non-negative")
    u = np.ascontiguousarray(u, dtype=np.float64)
    if u.ndim != 1:
        raise ValueError(f"expected a 1-D array, got shape {u.shape}")
    out = np.empty_like(u)
    if _lib.heat_run(float(r), int(steps), u, out, u.size) != 0:
        raise RuntimeError("heat_run failed")
    return out
