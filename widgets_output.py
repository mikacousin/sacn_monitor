# Copyright (c) 2020 Mika Cousin <mika.cousin@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Output Widget"""

import math
from typing import Optional, Tuple
import cairo
from gi.repository import Gtk


def rounded_rectangle_fill(
    cr: cairo.Context, area: Tuple[int, int, int, int], radius: int
):
    """Draw a filled rounded box

    Args:
        cr: Cairo context
        area: Coordinates (top, bottom, left, right)
        radius: Arc's radius
    """
    a, b, c, d = area
    cr.arc(a + radius, c + radius, radius, 2 * (math.pi / 2), 3 * (math.pi / 2))
    cr.arc(b - radius, c + radius, radius, 3 * (math.pi / 2), 4 * (math.pi / 2))
    cr.arc(b - radius, d - radius, radius, 0 * (math.pi / 2), 1 * (math.pi / 2))
    cr.arc(a + radius, d - radius, radius, 1 * (math.pi / 2), 2 * (math.pi / 2))
    cr.close_path()
    cr.fill()


class OutputWidget(Gtk.DrawingArea):
    """Output widget

    Attributes:
        universe: Universe number (1-63999)
        output: Output number (1-512)
        level: Output level (0-255)
    """

    universe: int
    output: int
    level: int

    __gtype_name__ = "OutputWidget"

    def __init__(self, universe, output):
        super().__init__()

        self.universe = universe
        self.output = output
        self.level = 0

        self.set_size_request(32, 32)
        self.set_draw_func(self.draw, None)

    def draw(
        self,
        area: Gtk.DrawingArea,
        cr: cairo.Context,
        w: int,
        h: int,
        _data: Optional[object],
    ) -> None:
        """Draw widget

        Args:
            area: The Gtk.DrawingArea to redraw
            cr: Cairo context to draw to
            w: The actual width of the contents
            h: The actual height of the contents
            _data: User data
        """
        # Draw background
        area = (1, w - 2, 1, h - 2)
        cr.set_source_rgb(
            0.3 + (0.2 / 255 * self.level), 0.3, 0.3 - (0.3 / 255 * self.level)
        )
        rounded_rectangle_fill(cr, area, 5)
        # Draw output number
        self.draw_output_number(cr, w, h)
        # Draw Output level
        self.draw_output_level(cr, w, h)

    def draw_output_number(self, cr: cairo.Context, w: int, h: int) -> None:
        """Draw Output number

        Args:
            cr: Used to draw with cairo
            w: width
            h: height
        """
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.select_font_face(
            "Cantarell Regular", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
        )
        cr.set_font_size(8)
        text = f"{self.output}"
        (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
        cr.move_to(w / 2 - width / 2, h / 4 - (height - 20) / 4)
        cr.show_text(text)

    def draw_output_level(self, cr: cairo.Context, w: int, h: int) -> None:
        """Draw Output level

        Args:
            cr: Used to draw with cairo
            w: width
            h: height
        """
        if self.level:
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.select_font_face(
                "Cantarell Bold", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
            )
            cr.set_font_size(8)
            text = str(self.level)
            (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
            cr.move_to(w / 2 - width / 2, h / 2 - (height - 20) / 2)
            cr.show_text(text)
