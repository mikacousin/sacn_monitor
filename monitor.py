"""sACN monitor"""

import sys
import gi
import sacn

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib  # noqa:E402
from widgets_output import OutputWidget  # noqa:E402


def callback(packet):
    """Callback function to update outputs levels"""
    for output, level in enumerate(packet.dmxData):
        try:
            univ = packet.universe
            app_monitor.win.outputs[univ, output].level = level
            GLib.idle_add(app_monitor.win.outputs[univ, output].queue_draw)
        except AttributeError:
            pass


class Window(Gtk.ApplicationWindow):
    """Window with 512 DMX outputs"""

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


# sACN monitored universes (1-63999)
UNIVERSES = [1, 2, 4]

app_monitor = Application()
receiver = sacn.sACNreceiver()
receiver.start()
for universe in UNIVERSES:
    receiver.join_multicast(universe)
    receiver.register_listener("universe", callback, universe=universe)

exit_status = app_monitor.run(sys.argv)
receiver.stop()
sys.exit(exit_status)
