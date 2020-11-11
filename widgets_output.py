"""Output Widget"""

import math
import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa:E402


def rounded_rectangle_fill(cr, area, radius):
    """Draw a filled rounded box

    Args:
        cr: cairo context
        area: coordinates (top, bottom, left, right)
        radius: arc's radius
    """
    a, b, c, d = area
    cr.arc(a + radius, c + radius, radius, 2 * (math.pi / 2), 3 * (math.pi / 2))
    cr.arc(b - radius, c + radius, radius, 3 * (math.pi / 2), 4 * (math.pi / 2))
    cr.arc(b - radius, d - radius, radius, 0 * (math.pi / 2), 1 * (math.pi / 2))
    cr.arc(a + radius, d - radius, radius, 1 * (math.pi / 2), 2 * (math.pi / 2))
    cr.close_path()
    cr.fill()


class OutputWidget(Gtk.Misc):
    """Output widget

    Attributes:
        universe (int): universe (1-63999)
        output (int): output number (1-512)
        level (int): output level (0-255)
        scale (float):
        width (int): widget width and height
    """

    __gtype_name__ = "OutputWidget"

    def __init__(self, universe, output):

        Gtk.Misc.__init__(self)

        self.universe = universe
        self.output = output
        self.level = 0

        self.scale = 1.0
        self.width = 32 * self.scale
        self.set_size_request(self.width, self.width)

    def do_draw(self, cr):
        """Draw widget"""
        self.width = 32 * self.scale
        self.set_size_request(self.width, self.width)
        allocation = self.get_allocation()
        # Draw background
        area = (1, allocation.width - 2, 1, allocation.height - 2)
        cr.set_source_rgb(
            0.3 + (0.2 / 255 * self.level), 0.3, 0.3 - (0.3 / 255 * self.level)
        )
        rounded_rectangle_fill(cr, area, 5)
        # Draw output number
        self._draw_output_number(cr, allocation)
        # Draw Output level
        self._draw_output_level(cr, allocation)

    def _draw_output_number(self, cr, allocation):
        """Draw Output number"""
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.select_font_face(
            "Cantarell Regular", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
        )
        cr.set_font_size(8 * self.scale)
        text = f"{self.output}.{self.universe}"
        (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
        cr.move_to(
            allocation.width / 2 - width / 2, allocation.height / 4 - (height - 20) / 4
        )
        cr.show_text(text)

    def _draw_output_level(self, cr, allocation):
        """Draw Output level"""
        if self.level:
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.select_font_face(
                "Cantarell Bold", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD
            )
            cr.set_font_size(8 * self.scale)
            text = str(self.level)
            (_x, _y, width, height, _dx, _dy) = cr.text_extents(text)
            cr.move_to(
                allocation.width / 2 - width / 2,
                allocation.height / 2 - (height - 20) / 2,
            )
            cr.show_text(text)