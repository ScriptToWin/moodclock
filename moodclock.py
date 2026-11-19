#!/usr/bin/env python3
"""
mdc — terminal clock that becomes the weather / mood.
Clean ASCII art, fullscreen terminal layout, and animated coffee/weather.
"""

from __future__ import annotations

import argparse
import random
import shutil
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
# Themes + ASCII Atmospheres (No Emojis, Pure ASCII)
# ─────────────────────────────────────────────────────────────────────────────

THEMES: Dict[str, Dict] = {
    "clear": {
        "name": "[ Shiny Sparkle ]",
        "primary": "#FFB7B2",
        "accent":  "#FFDAC1",
        "muted":   "#E29578",
        "art": [
            "            \\  |  /            ",
            "          \\  .-.  /            ",
            "        --- ( * ) ---          ",
            "          /  '-'  \\            ",
            "            /  |  \\            ",
        ],
    },
    "sunny": {
        "name": "[ Kawaii Sunshine ]",
        "primary": "#FFB7B2",
        "accent":  "#FF9AA2",
        "muted":   "#E29578",
        "art": [
            "            \\  |  /            ",
            "          \\  .-.  /            ",
            "        --- ( v ) ---          ",
            "          /  '-'  \\            ",
            "            /  |  \\            ",
        ],
    },
    "cloudy": {
        "name": "[ Soft Fluffy Clouds ]",
        "primary": "#B5E2FA",
        "accent":  "#EDF6F9",
        "muted":   "#83C5BE",
        "art": [
            "                               ",
            "       .---.      .---.        ",
            "    .-(     ). .-(     ).      ",
            "   (___.___(_)_(___.___(_)     ",
            "                               ",
        ],
    },
    "rain": {
        "name": "[ Animated Melancholy Rain ]",
        "primary": "#A0C4FF",
        "accent":  "#BDB2FF",
        "muted":   "#9BF6FF",
        "is_animated_rain": True,
        "art": [
            "       .---.      .---.        ",
            "    .-(     ). .-(     ).      ",
            "   (___.___(_)_(___.___(_)     ",
            "    '  .  '  .  '  .  '  .       ",
            "   .  '  .  '  .  '  .  '  .     ",
        ],
    },
    "storm": {
        "name": "[ Thunder Spark ]",
        "primary": "#CAFFBF",
        "accent":  "#FFADAD",
        "muted":   "#FDFFB6",
        "is_animated_storm": True,
        "art": [
            "       .---.      .---.        ",
            "    .-(     ). .-(     ).      ",
            "   (___.___(_)_(___.___(_)     ",
            "    '  /\\  '  .  '  /\\  '  .     ",
            "   .  '  .  /\\  .  '  .  /\\  .   ",
        ],
    },
    "snow": {
        "name": "[ Magical Falling Snow ]",
        "primary": "#E4C1F9",
        "accent":  "#F694C1",
        "muted":   "#8AB6F9",
        "is_animated_snow": True,
        "art": [
            "       .---.      .---.        ",
            "    .-(     ). .-(     ).      ",
            "   (___.___(_)_(___.___(_)     ",
            "    *     .     *     .        ",
            " .     *     .     *     .     ",
        ],
    },
    "fog": {
        "name": "[ Dreamy Misty Fog ]",
        "primary": "#D8E2DC",
        "accent":  "#FFE5D9",
        "muted":   "#B7B7A4",
        "is_animated_fog": True,
        "art": [
            "                               ",
            "   ~  ~  ~  ~  ~  ~  ~  ~      ",
            "  ~  ~  ~  ~  ~  ~  ~  ~  ~    ",
            "   ~  ~  ~  ~  ~  ~  ~  ~      ",
            "                               ",
        ],
    },
    "night": {
        "name": "[ Starlit Dream Night ]",
        "primary": "#BDB2FF",
        "accent":  "#FFC6FF",
        "muted":   "#9B5DE5",
        "art": [
            "        *           .          ",
            "   .         *            *    ",
            "          .        ( )         ",
            "     *         .         *     ",
            "            .      *           ",
        ],
    },
    "dawn": {
        "name": "[ Early Morning Bloom ]",
        "primary": "#FFC6FF",
        "accent":  "#FFADAD",
        "muted":   "#FFD6A5",
        "art": [
            "                               ",
            "              .-.              ",
            "         --- ( @ ) ---         ",
            "      ~~~~~~~~~~~~~~~~~~~~     ",
            "                               ",
        ],
    },
    "evening": {
        "name": "[ Sunset Pastel Glow ]",
        "primary": "#FFADAD",
        "accent":  "#FFD6A5",
        "muted":   "#FDFFB6",
        "art": [
            "                               ",
            "              .-.              ",
            "         --- ( # ) ---         ",
            "      ~~~~~~~~~~~~~~~~~~~~     ",
            "                               ",
        ],
    },
    "calm": {
        "name": "[ Peaceful Matcha Tea ]",
        "primary": "#CAFFBF",
        "accent":  "#9BF6FF",
        "muted":   "#70C1B3",
        "art": [
            "                               ",
            "   ~     ~     ~     ~     ~   ",
            "      ~     ~     ~     ~      ",
            "   ~     ~     ~     ~     ~   ",
            "                               ",
        ],
    },
    "cozy": {
        "name": "[ Animated Cozy Cafe ]",
        "primary": "#FFD6A5",
        "accent":  "#FFADAD",
        "muted":   "#E29578",
        "is_animated_coffee": True,
        "art": [
            "             (  ) (  )         ",
            "              \\ \\ / /          ",
            "           .------------.      ",
            "           |   _    _   |\\     ",
            "           |  (o)  (o)  | ]    ",
            "           |    ___     |      ",
            "           \\            /      ",
            "            `----------'       ",
        ],
    },
    "focus": {
        "name": "[ Lo-Fi Study Beats ]",
        "primary": "#9BF6FF",
        "accent":  "#CAFFBF",
        "muted":   "#48CAE4",
        "art": [
            "                               ",
            "            .-.                ",
            "           ( oo )              ",
            "            `--'               ",
            "                               ",
        ],
    },
    "dreamy": {
        "name": "[ Magical Cutecore Vibe ]",
        "primary": "#FFC6FF",
        "accent":  "#E4C1F9",
        "muted":   "#BDB2FF",
        "art": [
            "        *     .      *         ",
            "   .         +          .      ",
            "       .          *            ",
            "   *        .         +        ",
            "            *     .            ",
        ],
    },
    "matrix": {
        "name": "[ Cute Cyber Matrix ]",
        "primary": "#CAFFBF",
        "accent":  "#9BF6FF",
        "muted":   "#70C1B3",
        "art": [
            "   + * + * + * + * + * + *     ",
            "   * + * + * + * + * + * +     ",
            "   + * + * + * + * + * + *     ",
            "   * + * + * + * + * + * +     ",
            "   + * + * + * + * + * + *     ",
        ],
    },
}

DIGITS = {
    "0": [" ████ ", "█    █", "█    █", "█    █", " ████ "],
    "1": ["  ██  ", "   █  ", "   █  ", "   █  ", " █████"],
    "2": [" ████ ", "     █", " ████ ", "█     ", " █████"],
    "3": [" ████ ", "     █", " ████ ", "     █", " ████ "],
    "4": ["█    █", "█    █", " █████", "     █", "     █"],
    "5": [" █████", "█     ", " ████ ", "     █", " ████ "],
    "6": [" ████ ", "█     ", " ████ ", "█    █", " ████ "],
    "7": [" █████", "     █", "    █ ", "   █  ", "  █   "],
    "8": [" ████ ", "█    █", " ████ ", "█    █", " ████ "],
    "9": [" ████ ", "█    █", " █████", "     █", " ████ "],
    ":": ["      ", "  ..  ", "      ", "  ..  ", "      "],
    " ": ["      ", "      ", "      ", "      ", "      "],
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
            r = requests.get(url, timeout=6, headers={"User-Agent": "mdc/1.0"})
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
        self.anim_tick = 0

        if theme and theme in THEMES:
            self.mode = "mood"
            self.manual_theme = theme
            mood_keys = list(THEMES.keys())
            if theme in mood_keys:
                self.mood_index = mood_keys.index(theme)

    def current_key(self) -> str:
        if self.mode == "mood" and self.manual_theme:
            return self.manual_theme
        if self.mode == "time":
            return get_time_theme(datetime.now().hour)
        if self.mode == "weather":
            return self.weather.condition()
        w = self.weather.condition()
        if w in ("rain", "storm", "snow", "fog"):
            return w
        return get_time_theme(datetime.now().hour)

    def build_frame(self) -> Panel:
        self.anim_tick += 1
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

        art_lines = list(theme.get("art", []))

        # Animierter Rauch für die größere Kaffeetasse
        if theme.get("is_animated_coffee"):
            phase = (self.anim_tick // 2) % 4
            if phase == 0:
                art_lines[0] = "             (  ) (  )         "
                art_lines[1] = "              \\ \\ / /          "
            elif phase == 1:
                art_lines[0] = "             ( )   ( )         "
                art_lines[1] = "              / / \\ \\          "
            elif phase == 2:
                art_lines[0] = "              ~ ~   ~ ~        "
                art_lines[1] = "             (  )   (  )       "
            else:
                art_lines[0] = "               ( )   ( )       "
                art_lines[1] = "              ~ ~   ~ ~        "

        elif theme.get("is_animated_snow"):
            shift = (self.anim_tick // 2) % 3
            if shift == 0:
                art_lines[3] = "    *     .     *     .        "
                art_lines[4] = " .     *     .     *     .     "
            elif shift == 1:
                art_lines[3] = "   *     .     *     .       "
                art_lines[4] = "     .     *     .     *     "
            else:
                art_lines[3] = "      .     *     .     *    "
                art_lines[4] = "   *     .     *     .       "

        elif theme.get("is_animated_rain"):
            shift = (self.anim_tick // 2) % 2
            if shift == 0:
                art_lines[3] = "    '  .  '  .  '  .  '  .    "
                art_lines[4] = "   .  '  .  '  .  '  .  '  .  "
            else:
                art_lines[3] = "   .  '  .  '  .  '  .  '  .  "
                art_lines[4] = "    '  .  '  .  '  .  '  .    "

        elif theme.get("is_animated_storm"):
            shift = (self.anim_tick // 2) % 2
            if shift == 0:
                art_lines[3] = "    '  /\\  '  .  '  /\\  '  .   "
                art_lines[4] = "   .  '  .  /\\  .  '  .  /\\  . "
            else:
                art_lines[3] = "    .  '  /\\  '  .  '  /\\  '   "
                art_lines[4] = "   /\\  .  '  .  /\\  .  '  .   "

        elif theme.get("is_animated_fog"):
            shift = (self.anim_tick // 3) % 2
            if shift == 0:
                art_lines[1] = "   ~  ~  ~  ~  ~  ~  ~  ~      "
                art_lines[2] = "  ~  ~  ~  ~  ~  ~  ~  ~  ~    "
            else:
                art_lines[1] = "  ~  ~  ~  ~  ~  ~  ~  ~  ~    "
                art_lines[2] = "   ~  ~  ~  ~  ~  ~  ~  ~      "

        art = Text()
        for i, line in enumerate(art_lines):
            if i:
                art.append("\n")
            art.append(line, style=theme["accent"])

        label = Text(theme["name"], style=theme["primary"])

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

        # Vollbild-Ansicht exakt nach Terminal-Größe
        term_size = shutil.get_terminal_size((80, 24))
        panel_width = term_size.columns
        panel_height = term_size.lines

        return Panel(
            body,
            width=panel_width,
            height=panel_height,
            border_style=theme["primary"],
            box=box.ROUNDED,
            padding=(1, 2),
            title="[bold] mdc [/]",
            title_align="center",
        )

    def cycle_mood(self):
        self.mode = "mood"
        mood_keys = list(THEMES.keys())
        self.mood_index = (self.mood_index + 1) % len(mood_keys)
        self.manual_theme = mood_keys[self.mood_index]

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
            with Live(self.build_frame(), console=self.console, refresh_per_second=6, screen=True) as live:
                while self.running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
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
            self.console.print("[dim]mdc stopped[/]")


def main():
    parser = argparse.ArgumentParser(description="mdc — time + atmosphere")
    parser.add_argument("-l", "--location", default=None, help="Location for weather detection")
    parser.add_argument("-m", "--mode", choices=["auto", "time", "weather", "mood"], default="auto")
    parser.add_argument("-t", "--theme", choices=list(THEMES.keys()), help="Force a theme")
    parser.add_argument("--12h", action="store_true", dest="twelve")
    parser.add_argument("--no-seconds", action="store_true")
    parser.add_argument("--list-themes", action="store_true")
    args = parser.parse_args()

    if args.list_themes:
        console = Console()
        console.print("\n[bold]Themes List[/]\n")
        for k, t in THEMES.items():
            console.print(f"  {k:12}  {t['name']}")
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
