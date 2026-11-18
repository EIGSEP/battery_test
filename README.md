# EIGSEP battery discharge tests

Bench discharge tests of the 12.8 V LiFePO4 batteries considered for EIGSEP (March–June 2025), and the
scripts used to take and plot the data. Author: Richard Rodriguez.

**Plots:** `regenerated_plots_2026-11-18/` (voltage vs time, one per battery plus `voltage_all.png`),
made by `regenerated_plots_2026-11-18/make_plots.py`.

## How the data were taken

A Raspberry Pi Pico read the battery voltage through a 5:1 resistor divider on ADC pin 28, once per second
(`usb_test.py`, `batt_test.py`), while the battery discharged into a 1.25 Ω load (four 5 Ω resistors in
parallel, as assumed in `battery_summary.py`), about 10 A at 13 V.

## Data files

`batteryN_out.text`: one line per second, `<timestamp> <reading>`.

- **reading** is the ADC value as a fraction of 3.3 V. **Battery voltage = reading × 3.3 × 5 = reading × 16.5.**
- **timestamp** is the Pico clock in seconds. The clock was not set for most tests (they start in January 2021),
  so use it for durations only.
- A reading of 0.0 means the load was cut off or the logger stopped; the scripts stop reading there.

| File | What it is |
|---|---|
| `battery1`–`battery5` | 100 Ah batteries |
| `battery6`–`battery11` | 20 Ah batteries |
| `battery1b`, `battery2b` | second tests of batteries 1 and 2 |
| `battery12` | 100 Ah, data combined from two runs (~6.3 V readings) |
| `battery13` | 2S: cells #3 and #4 in series. Overwritten in commit b82b778; full data in `regenerated_plots_2026-11-18/battery13_recovered_out.text` |
| `battery14` | 4S module (short run, not fully charged) |
| `battery15` | empty |

`battery_discharge_summary.csv`: discharge time and total Ah per battery (`battery_summary.py`).

`charge_controller_tests/`: MPPT and PWM charge-controller logs and RFI test scripts.

## Scripts

See `INSTRUCTIONS.md`. In short: `usb_test.py` logs data from the Pico; `battery_summary.py` makes the summary
table; `plot_voltage.py N`, `plot_Ah.py`, `plot_battery%.py` plot one battery; the `master_*_plotter.py`
scripts plot all of them (their legends number the curves by file order, not battery number; use
`regenerated_plots_2026-11-18/` for correctly labelled plots).
