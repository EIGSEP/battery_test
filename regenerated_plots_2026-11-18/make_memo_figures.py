"""Figures 7 and 8 of the EIGSEP battery memo. Usage: python make_memo_figures.py discharge_grid.png (also writes discharge_all.png)."""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = os.path.expanduser("~/Projects/battery_test")
OUT = sys.argv[1]
SCALE, WINDOW = 3.3 * 5, 41
TRIM = WINDOW // 2

NAMES = ["battery1", "battery1b", "battery2", "battery2b", "battery3", "battery4", "battery5",
         "battery6", "battery7", "battery8", "battery9", "battery10", "battery11",
         "battery12", "battery13", "battery14"]
TITLES = {"battery1b": "battery1 (2nd test)", "battery2b": "battery2 (2nd test)",
          "battery13": "battery13 (2S)", "battery14": "battery14 (4S)"}
AH = {**{f"battery{i}": "100 Ah" for i in (1, 2, 3, 4, 5)}, "battery1b": "100 Ah", "battery2b": "100 Ah",
      **{f"battery{i}": "20 Ah" for i in range(6, 12)}}


def load(path):
    t, v = [], []
    for line in open(path):
        try:
            ti, vi = map(float, line.split())
        except ValueError:
            continue
        if vi == 0.0:
            if t:
                break
            continue
        t.append(ti / 3600)
        v.append(vi * SCALE)
    t = np.array(t) - t[-1]
    fit = np.convolve(v, np.ones(WINDOW) / WINDOW, mode="valid")
    return t[::10][TRIM:], np.array(v)[::10][TRIM:], t[:len(fit)][::10][TRIM:], fit[::10][TRIM:]


plt.style.use("bmh")
fig, axes = plt.subplots(4, 4, figsize=(7.1, 7.6))
for ax, name in zip(axes.flat, NAMES):
    path = os.path.join(DATA, f"{name}_out.text")
    if name == "battery13":
        path = os.path.join(DATA, "regenerated_plots_2026-11-18", "battery13_recovered_out.text")
    t, v, ft, fv = load(path)
    ax.plot(t, v, ".", ms=1, color="royalblue")
    ax.plot(ft, fv, color="firebrick", lw=1)
    lo = 5.5 if name in ("battery12", "battery13") else 10
    ax.set_ylim(lo, lo + 4.5)
    ax.set_title(f"{TITLES.get(name, name)}" + (f", {AH[name]}" if name in AH else ""), fontsize=7)
    ax.tick_params(labelsize=6)
for ax in axes[-1]:
    ax.set_xlabel("Hours before end", fontsize=7)
for ax in axes[:, 0]:
    ax.set_ylabel("Voltage (V)", fontsize=7)
fig.tight_layout(pad=0.4)
fig.savefig(OUT, dpi=200)

# combined plot at printed width (7.1 in)
LABELS = {**TITLES, "battery13": "battery13 (2S)"}
fig, ax = plt.subplots(figsize=(7.1, 4.2))
colors = plt.cm.tab20(np.linspace(0, 1, len(NAMES)))
for c, name in zip(colors, NAMES):
    path = os.path.join(DATA, f"{name}_out.text")
    if name == "battery13":
        path = os.path.join(DATA, "regenerated_plots_2026-11-18", "battery13_recovered_out.text")
    t, v, ft, fv = load(path)
    ax.plot(ft, fv, color=c, lw=1.4, label=LABELS.get(name, name) + (f", {AH[name]}" if name in AH else ""))
ax.set_xlabel("Hours before end of discharge", fontsize=9)
ax.set_ylabel("Voltage (V)", fontsize=9)
ax.tick_params(labelsize=8)
ax.legend(fontsize=7, ncol=2, loc="lower left")
fig.tight_layout(pad=0.4)
fig.savefig(OUT.replace("discharge_grid", "discharge_all"), dpi=200)
