"""Visualise the verified heat-equation scheme from HeatCore.lean.

Every time step is computed by the Lean-compiled `run` (via heat_lean);
numpy/matplotlib are only used to set up the initial state and to plot.

    ./build.sh                     # once, to build libheat
    python3 visualise.py           # writes heat.png
    python3 visualise.py --gif     # also writes heat.gif (animation)
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

import heat_lean

# One-hue sequential ramp (light -> dark blue) for magnitude.
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
# Ordinal steps for the profile lines (lightest still clears 2:1 on the surface).
ORD = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def initial(n):
    x = np.arange(n) / n
    u = np.exp(-((x - 0.25) / 0.03) ** 2)            # a narrow hot spot
    u += 0.6 * ((x > 0.55) & (x < 0.75))              # a hot block with sharp edges
    return u


def simulate(u0, r, steps, every):
    """Space-time history: row k is the state after k*every Lean steps."""
    rows = [u0]
    u = u0
    for _ in range(steps // every):
        u = heat_lean.run(u, r, every)                # Lean `run r every u`
        rows.append(u)
    return np.array(rows)


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)


def plot(hist, r, every, path):
    n = hist.shape[1]
    t_max = (hist.shape[0] - 1) * every
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.8), facecolor=SURFACE,
                               gridspec_kw={"width_ratios": [1.15, 1]})
    fig.suptitle(f"1-D heat equation, FTCS scheme compiled from Lean  (n = {n}, r = {r}, periodic)",
                 color=INK, fontsize=12, x=0.01, ha="left")

    # Space-time heatmap.
    style(a)
    cmap = LinearSegmentedColormap.from_list("seq", SEQ)
    t = np.arange(hist.shape[0] + 1) * every        # row edges
    im = a.pcolormesh(np.arange(n + 1), t, hist, cmap=cmap, shading="flat", rasterized=True)
    # Diffusion spreads like sqrt(t), so a sqrt time axis shows it evenly.
    a.set_yscale("function", functions=(np.sqrt, np.square))
    a.set_ylim(0, t_max)
    a.set_xlabel("grid index j")
    a.set_ylabel("time step (sqrt scale)")
    a.set_title("Temperature over space and time", color=INK, fontsize=10, loc="left")
    cb = fig.colorbar(im, ax=a, pad=0.02)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=INK2, labelsize=8)
    cb.set_label("u", color=INK2)

    # Profiles at selected times.
    style(b)
    b.grid(axis="y", color=GRID, linewidth=0.8)
    b.set_axisbelow(True)
    idx = np.unique(np.round(np.geomspace(1, hist.shape[0], len(ORD)) - 1).astype(int))
    idx[0] = 0
    for c, k in zip(ORD, idx):
        b.plot(hist[k], color=c, linewidth=2, label=f"t = {k * every}")
    b.set_xlim(0, n - 1)
    b.set_xlabel("grid index j")
    b.set_ylabel("u")
    b.set_title("Profiles: heat spreads, peaks flatten", color=INK, fontsize=10, loc="left")
    leg = b.legend(frameon=False, fontsize=9, labelcolor=INK2)
    fig.text(0.99, 0.955, f"total heat Σu: {hist[0].sum():.9f} at t = 0,  {hist[-1].sum():.9f} at t = {t_max}",
             ha="right", fontsize=9, color=INK2)

    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    print("wrote", path)


def animate(hist, every, path):
    from matplotlib.animation import FuncAnimation, PillowWriter
    fig, ax = plt.subplots(figsize=(7, 3.6), facecolor=SURFACE)
    style(ax)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.plot(hist[0], color="#b5b4ad", linewidth=1.5, label="t = 0")   # reference
    (line,) = ax.plot(hist[0], color=ORD[2], linewidth=2, label="current")
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2, loc="upper right")
    ax.set_xlim(0, hist.shape[1] - 1)
    ax.set_ylim(-0.05, hist.max() * 1.08)
    ax.set_xlabel("grid index j")
    ax.set_ylabel("u")
    label = ax.set_title("Lean heat core, t = 0", color=INK, fontsize=10, loc="left")
    fig.tight_layout()

    frames = np.unique(np.round(np.geomspace(1, hist.shape[0], 120) - 1).astype(int))

    def update(k):
        line.set_ydata(hist[k])
        label.set_text(f"Lean heat core, t = {k * every}")
        return line, label

    FuncAnimation(fig, update, frames=frames, blit=False).save(path, writer=PillowWriter(fps=20))
    print("wrote", path)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=200, help="grid points")
    p.add_argument("--r", type=float, default=0.25, help="r = alpha dt / dx^2 (stable for r <= 0.5)")
    p.add_argument("--steps", type=int, default=5000, help="total time steps")
    p.add_argument("--every", type=int, default=5, help="record the state every this many steps")
    p.add_argument("--out", default="heat.png")
    p.add_argument("--gif", action="store_true", help="also write heat.gif")
    a = p.parse_args()

    hist = simulate(initial(a.n), a.r, a.steps, a.every)
    plot(hist, a.r, a.every, a.out)
    if a.gif:
        animate(hist, a.every, a.out.rsplit(".", 1)[0] + ".gif")
