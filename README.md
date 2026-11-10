# Moodclock

**Just time + atmosphere.**

No city. No degrees. Only the clock and the sky.

```
╭──────────────────────────── moodclock ────────────────────────────╮
│                                                                   │
│                        .--.      .--.                             │
│                     .-(    ). .-(    ).                           │
│                    (___.__)_) (___.__)_)                          │
│                     ʻ ʻ ʻ ʻ ʻ  ʻ ʻ ʻ ʻ                            │
│                    ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ                          │
│                                                                   │
│              ███   █   █     █████  █████                         │
│             █   █  █   █       █    █                             │
│             █████  █████       █    ███                           │
│             █   █      █       █    █                             │
│             █   █      █       █    █████                         │
│                                                                   │
│                              RAIN                                 │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
```

---

## Install

```bash
chmod +x install.sh && ./install.sh
```

Then open a new terminal and type:

```bash
moodclock
```

---

## Usage

```bash
moodclock                 # auto (weather + time)
moodclock -t rain         # force rain
moodclock -t night        # force night
moodclock -t snow
moodclock -t clear
moodclock -t calm         # mood
moodclock --list-themes
```

### Keys

| Key | Action          |
|-----|-----------------|
| `m` | Cycle moods     |
| `a` | Auto mode       |
| `t` | Time of day     |
| `w` | Live weather    |
| `s` | Toggle seconds  |
| `q` | Quit            |

---

## Atmospheres

**Weather**  
`clear` · `sunny` · `cloudy` · `rain` · `storm` · `snow` · `fog`

**Time**  
`dawn` · `evening` · `night`

**Mood**  
`calm` · `cozy` · `focus` · `dreamy` · `matrix`

Auto mode uses real weather when it’s interesting (rain, storm, snow, fog), otherwise follows the time of day.

---

Made for the terminal.
