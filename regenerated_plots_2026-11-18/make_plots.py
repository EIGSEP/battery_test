"""Regenerate the battery discharge plots (voltage vs time) as PNG files.

Same processing as ../plot_voltage.py and ../master_voltage_plotter.py:
reading x 3.3 x 5 (5:1 divider), stop at the first 0.0 reading after data starts,
time shifted so the end of the discharge is 0, 41-point moving average, every 10th point.
Only difference: legends use the file names instead of the position in the file list.

battery13 was overwritten in git commit b82b778 (2025-06-02); its data is read from
battery13_recovered_out.text (git show b82b778~1:battery13_out.text).
"""
import os
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
SCALE_FACTOR = 3.3 * 5
WINDOW = 41
TRIM = WINDOW // 2

# what each file is (from the git commit messages)
NOTES = {
    "battery12": "data combined for battery 12",
    "battery13": "cells #3 and #4 in series (2S)",
    "battery14": "4S",
    "battery1b": "second test of battery 1",
    "battery2b": "second test of battery 2",
}


def load(path):
    t, v = [], []
    with open(path) as f:
        for line in f:
            try:
                ti, vi = map(float, line.split())
            except ValueError:
                continue
            if vi == 0.0:
                if t:
                    break
                continue
            t.append(ti / 60)
            v.append(vi * SCALE_FACTOR)
    if len(t) <= WINDOW:
        return None
    t = np.array(t) - t[-1]
    fit = np.convolve(v, np.ones(WINDOW) / WINDOW, mode="valid")
    return t[::10], np.array(v)[::10], t[:len(fit)][::10], fit[::10]


files = {os.path.basename(p).replace("_out.text", ""): p
         for p in glob.glob(os.path.join(DATA, "battery*_out.text"))}
files["battery13"] = os.path.join(HERE, "battery13_recovered_out.text")


def sort_key(name):
    num = "".join(c for c in name[7:] if c.isdigit())
    return (int(num), name)


data = {}
for name in sorted(files, key=sort_key):
    d = load(files[name])
    if d is None:
        print(f"{name}: no usable data, skipped")
        continue
    data[name] = d

plt.style.use("bmh")


def label(name):
    return f"{name} ({NOTES[name]})" if name in NOTES else name


def xticks(max_time):
    ticks = np.linspace(-max_time, 0, num=10)
    plt.xticks(ticks, labels=[f"{int(abs(x))}" for x in ticks])


# one plot per battery
for name, (t, v, ft, fv) in data.items():
    plt.figure(figsize=(12, 5))
    plt.plot(t[TRIM:], v[TRIM:], marker=".", linestyle="-", color="royalblue", label="Voltage", lw=0.8)
    plt.plot(ft[TRIM:], fv[TRIM:], linestyle="-", color="firebrick", label="Voltage Fit (41-point moving average)", lw=1.2)
    plt.xlabel("Time before end of discharge (min)")
    plt.ylabel("Voltage (V)")
    plt.title(f"{label(name)}: Voltage Over Time")
    xticks(abs(t[0]))
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, f"voltage_{name}.png"), dpi=150)
    plt.close()

# all batteries on one plot (moving average only, as in master_voltage_plotter.py)
plt.figure(figsize=(12, 6))
colors = plt.cm.tab20(np.linspace(0, 1, len(data)))
max_time = 0
for c, (name, (t, v, ft, fv)) in zip(colors, data.items()):
    plt.plot(ft[TRIM:], fv[TRIM:], color=c, lw=2.0, label=label(name))
    max_time = max(max_time, abs(t[0]))
plt.xlabel("Time before end of discharge (min)")
plt.ylabel("Voltage (V)")
plt.title("Battery Voltage Over Time (41-point moving average)")
xticks(max_time)
plt.legend(fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(os.path.join(HERE, "voltage_all.png"), dpi=150)
plt.close()

for name, (t, v, ft, fv) in data.items():
    print(f"{name}: {abs(t[0]) / 60:.2f} h, start {v[0]:.2f} V, end {v[-1]:.2f} V")
