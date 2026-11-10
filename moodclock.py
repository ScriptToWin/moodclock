#!/usr/bin/env python3
"""
Moodclock — terminal clock that becomes the weather / mood.
Just time + atmosphere. No city, no degrees.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    from rich.console import Console, Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    print("Missing dependency: rich\n  pip install rich")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Missing dependency: requests\n  pip install requests")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Themes + ASCII atmospheres
# ─────────────────────────────────────────────────────────────────────────────

THEMES: Dict[str, Dict] = {
    "clear": {
        "name": "Clear",
        "primary": "#FFD166",
        "accent":  "#F4A261",
        "muted":   "#E9C46A",
        "art": [
            "            \\  |  /            ",
            "          \\  .-.  /            ",
            "        — (  ☼  ) —            ",
            "          /  '-'  \\            ",
            "            /  |  \\            ",
        ],
    },
    "sunny": {
        "name": "Sunny",
        "primary": "#FFBE0B",
        "accent":  "#FB5607",
        "muted":   "#FFD166",
        "art": [
            "            \\  |  /            ",
            "          \\  .-.  /            ",
            "        — (  ☼  ) —            ",
            "          /  '-'  \\            ",
            "            /  |  \\            ",
        ],
    },
    "cloudy": {
        "name": "Cloudy",
        "primary": "#8D99AE",
        "accent":  "#A8DADC",
        "muted":   "#6C757D",
        "art": [
            "                               ",
            "       .--.      .--.          ",
            "    .-(    ). .-(    ).        ",
            "   (___.__)_) (___.__)_)       ",
            "                               ",
        ],
    },
    "rain": {
        "name": "Rain",
        "primary": "#4A90A4",
        "accent":  "#6BCB77",
        "muted":   "#7BA3B5",
        "art": [
            "       .--.      .--.          ",
            "    .-(    ). .-(    ).        ",
            "   (___.__)_) (___.__)_)       ",
            "    ʻ ʻ ʻ ʻ ʻ  ʻ ʻ ʻ ʻ         ",
            "   ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ       ",
        ],
    },
    "storm": {
        "name": "Storm",
        "primary": "#5E5CE6",
        "accent":  "#FF6B6B",
        "muted":   "#8B8BAE",
        "art": [
            "       .--.      .--.          ",
            "    .-(    ). .-(    ).        ",
            "   (___.__)_) (___.__)_)       ",
            "    ʻ ʻ ⚡ ʻ ʻ  ʻ ⚡ ʻ ʻ         ",
            "   ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ ʻ       ",
        ],
    },
    "snow": {
        "name": "Snow",
        "primary": "#E0F7FA",
        "accent":  "#81D4FA",
        "muted":   "#B0BEC5",
        "art": [
            "       .--.      .--.          ",
            "    .-(    ). .-(    ).        ",
            "   (___.__)_) (___.__)_)       ",
            "    *  *  *  *  *  *  *        ",
            "   *  *  *  *  *  *  *  *      ",
        ],
    },
    "fog": {
        "name": "Fog",
        "primary": "#ADB5BD",
        "accent":  "#CED4DA",
        "muted":   "#6C757D",
        "art": [
            "                               ",
            "   ~  ~  ~  ~  ~  ~  ~  ~      ",
            "  ~  ~  ~  ~  ~  ~  ~  ~  ~    ",
            "   ~  ~  ~  ~  ~  ~  ~  ~      ",
            "                               ",
        ],
    },
    "night": {
        "name": "Night",
        "primary": "#9B5DE5",
        "accent":  "#00BBF9",
        "muted":   "#7B6B8A",
        "art": [
            "        *           .          ",
            "   .         *            *    ",
            "          .        ☾           ",
            "     *         .         *     ",
            "            .      *           ",
        ],
    },
    "dawn": {
        "name": "Dawn",
        "primary": "#FF9A76",
        "accent":  "#FF6B6B",
        "muted":   "#E8C4A8",
        "art": [
            "                               ",
            "              .-.              ",
            "         — — (   ) — —         ",
            "      ~~~~~~~~~~~~~~~~~~~~     ",
            "                               ",
        ],
    },
    "evening": {
        "name": "Evening",
        "primary": "#E07A5F",
        "accent":  "#F2CC8F",
        "muted":   "#C9ADA7",
        "art": [
            "                               ",
            "              .-.              ",
            "         — — (   ) — —         ",
            "      ~~~~~~~~~~~~~~~~~~~~     ",
            "                               ",
        ],
    },
    "calm": {
        "name": "Calm",
        "primary": "#88C0D0",
        "accent":  "#81A1C1",
        "muted":   "#5E81AC",
        "art": [
            "                               ",
            "   ~     ~     ~     ~     ~   ",
            "      ~     ~     ~     ~      ",
            "   ~     ~     ~     ~     ~   ",
            "                               ",
        ],
    },
    "cozy": {
        "name": "Cozy",
        "primary": "#E07A5F",
        "accent":  "#F2CC8F",
        "muted":   "#C9ADA7",
        "art": [
            "                               ",
            "            (  (               ",
            "           )  )  )             ",
            "         (________)            ",
            "                               ",
        ],
    },
    "focus": {
        "name": "Focus",
        "primary": "#A3BE8C",
        "accent":  "#EBCB8B",
        "muted":   "#8FBCBB",
        "art": [
            "                               ",
            "            ┌───┐              ",
            "            │ · │              ",
            "            └───┘              ",
            "                               ",
        ],
    },
    "dreamy": {
        "name": "Dreamy",
        "primary": "#C77DFF",
        "accent":  "#E0AAFF",
        "muted":   "#9D4EDD",
        "art": [
            "        *     .      *         ",
            "   .         ✦          .      ",
            "       .          *            ",
            "   *        .         ✦        ",
            "            *     .            ",
        ],
    },
    "matrix": {
        "name": "Matrix",
        "primary": "#00FF41",
        "accent":  "#008F11",
        "muted":   "#003B00",
        "art": [
            "   1 0 1 0 1 0 1 0 1 0 1 0     ",
            "   0 1 0 1 0 1 0 1 0 1 0 1     ",
            "   1 0 1 0 1 0 1 0 1 0 1 0     ",
            "   0 1 0 1 0 1 0 1 0 1 0 1     ",
            "   1 0 1 0 1 0 1 0 1 0 1 0     ",
        ],
    },
}

WEATHER_KEYS = ["clear", "sunny", "cloudy", "rain", "storm", "snow", "fog"]
TIME_KEYS    = ["dawn", "clear", "evening", "night"]
MOOD_KEYS    = ["calm", "cozy", "focus", "dreamy", "matrix"]

DIGITS = {
    "0": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "1": ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    "2": ["████ ", "    █", " ███ ", "█    ", "█████"],
    "3": ["████ ", "    █", " ███ ", "    █", "████ "],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "████ ", "    █", "████ "],
    "6": [" ███ ", "█    ", "████ ", "█   █", " ███ "],
    "7": ["█████", "    █", "   █ ", "  █  ", "  █  "],
    "8": [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    "9": [" ███ ", "█   █", " ████", "    █", " ███ "],
    ":": ["     ", "  ·  ", "     ", "  ·  ", "     "],
    " ": ["     ", "     ", "     ", "     ", "     "],
}


def render_big_time(timestr: str, style: str) -> Text:
    lines = ["", "", "", "", ""]
    for ch in timestr:
        digit = DIGITS.get(ch, DIGITS[" "])
        for i in range(5):
            lines[i] += digit[i] + "  "
    result = Text()
    for i, line in enumerate(lines):
        if i:
            result.append("\n")
        result.append(line.rstrip(), style=style)
    return result


def get_time_theme(hour: int) -> str:
    if 5 <= hour < 8:
        return "dawn"
    elif 8 <= hour < 17:
        return "clear"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def weather_to_key(desc: str) -> str:
    d = desc.lower()
    if any(w in d for w in ("thunder", "storm", "lightning")):
        return "storm"
    if any(w in d for w in ("snow", "sleet", "blizzard", "ice")):
        return "snow"
    if any(w in d for w in ("rain", "drizzle", "shower")):
        return "rain"
    if any(w in d for w in ("fog", "mist", "haze")):
        return "fog"
    if any(w in d for w in ("cloud", "overcast")):
        return "cloudy"
    if any(w in d for w in ("sun", "clear", "fair")):
        return "sunny"
    return "clear"


class WeatherCache:
    def __init__(self, location: Optional[str] = None, ttl: int = 600):
        self.location = location or ""
        self.ttl = ttl
        self._data = None
        self._fetched_at = 0.0

    def fetch(self):
        now = time.time()
        if self._data and (now - self._fetched_at) < self.ttl:
            return self._data
        try:
            url = f"https://wttr.in/{self.location}?format=j1"
            r = requests.get(url, timeout=6, headers={"User-Agent": "moodclock/1.0"})
            r.raise_for_status()
            self._data = r.json()
            self._fetched_at = now
            return self._data
        except Exception:
            return self._data

    def condition(self) -> str:
        data = self.fetch()
        if not data:
            return "clear"
        try:
            desc = data["current_condition"][0]["weatherDesc"][0]["value"]
            return weather_to_key(desc)
        except Exception:
            return "clear"


class MoodClock:
    def __init__(
        self,
        location: Optional[str] = None,
        mode: str = "auto",
        theme: Optional[str] = None,
        show_seconds: bool = True,
        twelve_hour: bool = False,
    ):
        self.console = Console()
        self.weather = WeatherCache(location)
        self.mode = mode
        self.manual_theme = theme
        self.show_seconds = show_seconds
        self.twelve_hour = twelve_hour
        self.running = True
        self.mood_index = 0

        if theme and theme in THEMES:
            self.mode = "mood"
            self.manual_theme = theme
            if theme in MOOD_KEYS:
                self.mood_index = MOOD_KEYS.index(theme)

    def current_key(self) -> str:
        if self.mode == "mood" and self.manual_theme:
            return self.manual_theme
        if self.mode == "time":
            return get_time_theme(datetime.now().hour)
        if self.mode == "weather":
            return self.weather.condition()
        # auto
        w = self.weather.condition()
        if w in ("rain", "storm", "snow", "fog"):
            return w
        return get_time_theme(datetime.now().hour)

    def build_frame(self) -> Panel:
        now = datetime.now()
        key = self.current_key()
        theme = THEMES.get(key, THEMES["night"])

        if self.twelve_hour:
            fmt = "%I:%M:%S" if self.show_seconds else "%I:%M"
            timestr = now.strftime(fmt).lstrip("0")
        else:
            fmt = "%H:%M:%S" if self.show_seconds else "%H:%M"
            timestr = now.strftime(fmt)

        clock = render_big_time(timestr, style=theme["primary"])

        art_lines = theme.get("art", [])
        art = Text()
        for i, line in enumerate(art_lines):
            if i:
                art.append("\n")
            art.append(line, style=theme["accent"])

        label = Text(theme["name"].upper(), style=theme["primary"])

        help_text = Text(
            "  m mood   a auto   t time   w weather   s sec   q quit  ",
            style=theme["muted"],
        )

        body = Group(
            Text(""),
            Align.center(art),
            Text(""),
            Align.center(clock),
            Text(""),
            Align.center(label),
            Text(""),
            Align.center(help_text),
        )

        return Panel(
            body,
            border_style=theme["primary"],
            box=box.ROUNDED,
            padding=(0, 2),
            title=f"[bold {theme['accent']}]moodclock[/]",
            title_align="center",
        )

    def cycle_mood(self):
        self.mode = "mood"
        self.mood_index = (self.mood_index + 1) % len(MOOD_KEYS)
        self.manual_theme = MOOD_KEYS[self.mood_index]

    def handle_key(self, key: str):
        key = key.lower()
        if key == "q":
            self.running = False
        elif key == "m":
            self.cycle_mood()
        elif key == "a":
            self.mode = "auto"
            self.manual_theme = None
        elif key == "t":
            self.mode = "time"
            self.manual_theme = None
        elif key == "w":
            self.mode = "weather"
            self.manual_theme = None
        elif key == "s":
            self.show_seconds = not self.show_seconds
        elif key == "h":
            self.twelve_hour = not self.twelve_hour

    def run(self):
        self.weather.fetch()
        interactive = sys.stdin.isatty() and sys.stdout.isatty()

        if not interactive:
            self.console.print(self.build_frame())
            return

        import select
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            with Live(self.build_frame(), console=self.console, refresh_per_second=4, screen=True) as live:
                while self.running:
                    if select.select([sys.stdin], [], [], 0.15)[0]:
                        ch = sys.stdin.read(1)
                        self.handle_key(ch)
                    live.update(self.build_frame())
        except KeyboardInterrupt:
            pass
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass
            self.console.clear()
            self.console.print("[dim]moodclock stopped[/]")


def main():
    parser = argparse.ArgumentParser(description="Moodclock — time + atmosphere")
    parser.add_argument("-l", "--location", default=None, help="Location for weather detection")
    parser.add_argument("-m", "--mode", choices=["auto", "time", "weather", "mood"], default="auto")
    parser.add_argument("-t", "--theme", choices=list(THEMES.keys()), help="Force a theme")
    parser.add_argument("--12h", action="store_true", dest="twelve")
    parser.add_argument("--no-seconds", action="store_true")
    parser.add_argument("--list-themes", action="store_true")
    args = parser.parse_args()

    if args.list_themes:
        console = Console()
        console.print("\n[bold]Themes[/]\n")
        for k, t in THEMES.items():
            console.print(f"  {k:10}  {t['name']}")
        console.print()
        return

    app = MoodClock(
        location=args.location,
        mode=args.mode if not args.theme else "mood",
        theme=args.theme,
        show_seconds=not args.no_seconds,
        twelve_hour=args.twelve,
    )
    app.run()


if __name__ == "__main__":
    main()
