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

import cProfile
import os
import sys
import gi
import sacn

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk  # noqa:E402
from widgets_output import OutputWidget  # noqa:E402

App = Gio.Application.get_default


def callback(packet):
    """Callback function to update outputs levels

    Args:
        packet (sacn.DataPacket): DMX data
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
        try:
            App().win.outputs[univ, output].level = level
            GLib.idle_add(App().win.outputs[univ, output].queue_draw)
        except AttributeError:
            pass
    old_dmx_data[univ] = dmx_data


class Window(Gtk.ApplicationWindow):
    """Window with monitored universes

    Attributes:
        flowbox (list[Gtk.FlowBox]): One flowbox by monitored universe
        outputs (dict{int, int}): Output widgets
    """

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, title="sACN monitor", application=app)
        self.set_default_size(400, 400)
        self.set_border_width(1)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox = Gtk.VBox()
        self.flowbox = []
        self.outputs = {}
        for univ in UNIVERSES:
            vbox.pack_start(Gtk.Label(label=f"Universe {univ}"), True, True, 0)
            self.flowbox.append(Gtk.FlowBox())
            self.flowbox[-1].set_valign(Gtk.Align.START)
            self.flowbox[-1].set_max_children_per_line(512)
            self.flowbox[-1].set_selection_mode(Gtk.SelectionMode.NONE)
            for output in range(512):
                self.outputs[univ, output] = OutputWidget(univ, output + 1)
                self.flowbox[-1].add(self.outputs[univ, output])
            vbox.pack_start(self.flowbox[-1], True, True, 0)
        scrolled.add(vbox)
        self.add(scrolled)


class Application(Gtk.Application):
    """Application"""

    def __init__(self):
        Gtk.Application.__init__(self)
        self.win = None
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

    def do_activate(self):
        self.win = Window(self)
        self.win.show_all()

    def do_startup(self):
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
    res = prof.runcall(run_monitor)
    prof.dump_stats("sacn_monitor-runstats")
else:
    run_monitor()
