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

"""sACN monitor"""

from typing import Dict, List
import cProfile
import os
import sys
import gi
import sacn

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk  # noqa:E402
from widgets_output import OutputWidget  # noqa:E402

App = Gio.Application.get_default


def callback(packet: sacn.DataPacket) -> None:
    """Callback function to update outputs levels

    Args:
        packet: DMX data
    """
    univ = packet.universe
    dmx_data = list(packet.dmxData)
    # Create a list with only changed level outputs to not redraw all universe
    diff = [
        (index, e1)
        for index, (e1, e2) in enumerate(zip(dmx_data, old_dmx_data[univ]))
        if e1 != e2
    ]
    for output, level in diff:
        App().win.outputs[univ, output].level = level
        GLib.idle_add(App().win.outputs[univ, output].queue_draw)
    old_dmx_data[univ] = dmx_data


class Window(Gtk.ApplicationWindow):
    """Window with monitored universes

    Attributes:
        flowbox: One flowbox by monitored universe
        outputs: Output widgets
    """

    flowbox: List[Gtk.FlowBox]
    outputs: Dict[int, int]

    def __init__(self, app):
        super().__init__(title="sACN monitor", application=app)
        self.set_default_size(400, 400)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.flowbox = []
        self.outputs = {}
        for univ in UNIVERSES:
            vbox.append(Gtk.Label(label=f"Universe {univ}"))
            self.flowbox.append(Gtk.FlowBox())
            self.flowbox[-1].set_valign(Gtk.Align.START)
            self.flowbox[-1].set_max_children_per_line(512)
            self.flowbox[-1].set_selection_mode(Gtk.SelectionMode.NONE)
            for output in range(512):
                self.outputs[univ, output] = OutputWidget(univ, output + 1)
                self.flowbox[-1].append(self.outputs[univ, output])
            vbox.append(self.flowbox[-1])
        scrolled.set_child(vbox)
        self.set_child(scrolled)


class Application(Adw.Application):
    """Application"""

    win: Window

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.win = None
        self.get_style_manager().set_color_scheme(Adw.ColorScheme.PREFER_DARK)

    def do_activate(self) -> None:
        self.win = Window(self)
        self.win.present()

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)


def run_monitor():
    """Start application"""
    app_monitor = Application()
    receiver = sacn.sACNreceiver()
    receiver.start()
    for univ in UNIVERSES:
        receiver.join_multicast(univ)
        receiver.register_listener("universe", callback, universe=univ)
    app_monitor.run(sys.argv)
    receiver.stop()


# sACN monitored universes (1-63999)
UNIVERSES = [1, 2, 4]
old_dmx_data = {}
for universe in UNIVERSES:
    old_dmx_data[universe] = [0] * 512

run_profile = os.environ.get("SACN_MONITOR_PROFILING", False)

if run_profile:
    prof = cProfile.Profile()
    RES = prof.runcall(run_monitor)
    prof.dump_stats("sacn_monitor-runstats")
else:
    run_monitor()
