
# Mixxx Playlist Scheduler

Created by **elcalifornio**

A Python utility designed for **Mixxx** DJs to estimate when specific tracks will be played during an **AutoDJ** session. This tool is especially helpful for planning transition points, ensuring peak-hour tracks hit at the right time, or managing a timed set.

## Features

* **Accurate Scheduling:** Calculates start times based on track duration and crossfade settings.
* **Flexible Start Times:** Supports multiple formats (e.g., `21`, `21:30`, or `2026-04-09 21:30`).
* **Automatic Path Detection:** Automatically looks for the Mixxx database on **macOS** and **Linux**.
* **Hour Markers:** Visually identifies the start of the "Second Hour," "Third Hour," etc., to help pace your set.
* **Time Rounding:** Groups the initial start time to the nearest 5-minute block by default for a cleaner schedule.

## Prerequisites

* **Python 3.x**
* **Mixxx** installed on your system

## Installation

1.  Clone this repository or download `mix_playlist_schedule.py`.
2.  Ensure you have read access to your `mixxxdb.sqlite` file.

## Usage

Run the script from your terminal using the following syntax:

```bash
python mix_playlist_schedule.py -p "Your Playlist Name" -t 21:00 -c 5
```

### Argument Options

| Flag | Name | Description | Default |
| :--- | :--- | :--- | :--- |
| `-d` | `--db` | Manual path to the Mixxx SQLite database | Auto-detected |
| `-p` | `--playlist` | The name of the Mixxx playlist to analyze | "Auto DJ" |
| `-t` | `--start` | The time AutoDJ begins (HH, HH:MM, or YYYY-MM-DD HH:MM) | Current time |
| `-c` | `--crossfade` | Crossfade duration in seconds | 0 |
| `--round-minutes` | N/A | Round start time to nearest N minutes | 5 |
| `--hide-hour-labels` | N/A | Suppress the "Second Hour," etc., labels | False |

## Example Output

```text
AutoDJ Schedule for playlist: 'Salsa Night'
Start time: 21:00 on 2026-04-09
Crossfade: 5 seconds

Pos | Starts | Elapsed | Length | Comment | Track Title | Artist
----|--------|--------|-------|---------|------------|-------
01 | 21:00 | 0:00 | 4:15 | Intro | Cali Pachanguero | Grupo Niche
02 | 21:04 | 4:10 | 3:50 | Energy | Idilio | Willie Colón
```

## License

This project is open-source and available for the Mixxx community to use and improve.
