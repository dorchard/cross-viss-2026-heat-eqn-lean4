import numpy as np

import heat_lean


def run_numpy(u, r, steps):
    for _ in range(steps):
        u = u + r * (np.roll(u, 1) - 2 * u + np.roll(u, -1))
    return u


def test_matches_numpy():
    rng = np.random.default_rng(0)
    for n in [1, 2, 3, 10, 257]:
        u = rng.random(n)
        np.testing.assert_allclose(heat_lean.run(u, 0.3, 50), run_numpy(u, 0.3, 50), rtol=1e-12)


def test_conservation_approximately_holds():
    u = np.zeros(100)
    u[50] = 1.0
    v = heat_lean.run(u, 0.25, 1000)
    assert abs(v.sum() - u.sum()) < 1e-12


def test_edge_cases():
    assert heat_lean.run(np.array([]), 0.25, 10).size == 0
    u = np.arange(5.0)
    np.testing.assert_array_equal(heat_lean.run(u, 0.25, 0), u)
    # non-float64 / non-contiguous input is converted
    np.testing.assert_allclose(heat_lean.run(np.arange(10)[::2], 0.1, 3),
                               run_numpy(np.arange(10.0)[::2], 0.1, 3))


def test_many_steps_no_stack_overflow():
    heat_lean.run(np.ones(4), 0.25, 1_000_000)


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f(); print("ok", name)
