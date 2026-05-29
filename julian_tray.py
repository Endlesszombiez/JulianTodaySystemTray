"""Show today's Julian date in the system tray.

This uses the common date-code meaning of "Julian date": YYYY-DDD, where
DDD is the day of year. For example, January 1, 2026 is 2026-001.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import threading
from pathlib import Path
from typing import Optional, TYPE_CHECKING

import startup

if TYPE_CHECKING:
    import pystray
    from PIL import Image


APP_NAME = "Julian Today"
ICON_SIZE = 64
ICON_PNG = "assets/calendar-icon.png"


class JulianTrayApp:
    def __init__(self) -> None:
        self.icon: Optional["pystray.Icon"] = None
        self._refresh_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def run(self) -> None:
        import pystray

        self.icon = pystray.Icon(
            APP_NAME,
            icon=create_icon_image(),
            title=self._tooltip(),
            menu=self._build_menu(),
        )
        self._schedule_midnight_refresh()
        self.icon.run()

    def copy_date(self, _icon: "pystray.Icon", _item: "pystray.MenuItem") -> None:
        import pyperclip

        pyperclip.copy(current_julian_date())

    def add_to_startup(self, _icon: "pystray.Icon", _item: "pystray.MenuItem") -> None:
        startup.add_to_startup()
        self.refresh()

    def remove_from_startup(self, _icon: "pystray.Icon", _item: "pystray.MenuItem") -> None:
        startup.remove_from_startup()
        self.refresh()

    def quit(self, icon: "pystray.Icon", _item: "pystray.MenuItem") -> None:
        with self._lock:
            if self._refresh_timer is not None:
                self._refresh_timer.cancel()
                self._refresh_timer = None
        icon.stop()

    def refresh(self) -> None:
        if self.icon is None:
            return

        self.icon.title = self._tooltip()
        self.icon.icon = create_icon_image()
        self.icon.menu = self._build_menu()
        self._schedule_midnight_refresh()

    def _build_menu(self) -> "pystray.Menu":
        import pystray

        julian_date = current_julian_date()
        return pystray.Menu(
            pystray.MenuItem(f"Julian date: {julian_date}", None, enabled=False),
            pystray.MenuItem("Copy date", self.copy_date),
            pystray.MenuItem(
                "Add to Startup",
                self.add_to_startup,
                enabled=startup.is_startup_supported() and not startup.is_startup_enabled(),
            ),
            pystray.MenuItem(
                "Remove from Startup",
                self.remove_from_startup,
                enabled=startup.is_startup_supported() and startup.is_startup_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit),
        )

    def _tooltip(self) -> str:
        return f"{APP_NAME}: {current_julian_date()}"

    def _schedule_midnight_refresh(self) -> None:
        delay_seconds = seconds_until_next_midnight()

        with self._lock:
            if self._refresh_timer is not None:
                self._refresh_timer.cancel()

            self._refresh_timer = threading.Timer(delay_seconds, self.refresh)
            self._refresh_timer.daemon = True
            self._refresh_timer.start()


def current_julian_date(today: Optional[dt.date] = None) -> str:
    date = today or dt.date.today()
    return f"{date.year}-{date.timetuple().tm_yday:03d}"


def seconds_until_next_midnight(now: Optional[dt.datetime] = None) -> float:
    current = now or dt.datetime.now()
    tomorrow = current.date() + dt.timedelta(days=1)
    next_midnight = dt.datetime.combine(tomorrow, dt.time.min)
    return max((next_midnight - current).total_seconds(), 1.0)


def create_icon_image() -> "Image.Image":
    from PIL import Image, ImageDraw

    icon_path = resource_path(ICON_PNG)
    if icon_path.exists():
        return Image.open(icon_path).convert("RGBA").resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)

    image = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (28, 36, 44, 255))
    draw = ImageDraw.Draw(image)

    day_of_year = dt.date.today().timetuple().tm_yday
    text = f"{day_of_year:03d}"

    font = load_font(24)
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    text_position = ((ICON_SIZE - text_width) / 2, (ICON_SIZE - text_height) / 2 - 2)

    draw.rounded_rectangle((4, 4, 60, 60), radius=12, fill=(247, 249, 251, 255))
    draw.rectangle((4, 4, 60, 19), fill=(55, 113, 200, 255))
    draw.text(text_position, text, font=font, fill=(23, 31, 38, 255))

    return image


def load_font(size: int) -> "ImageFont.ImageFont":
    from PIL import ImageFont

    preferred_fonts = ("arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf")
    for font_name in preferred_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show today's Julian date in the system tray.")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print today's Julian date and exit without starting the tray app.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.print:
        print(current_julian_date())
        return

    JulianTrayApp().run()


if __name__ == "__main__":
    main()
