# sACN Monitor

Simple application to monitor sACN universes.

Tested on Archlinux and Windows 10 (with [MSYS2](https://www.msys2.org)).

![Screenshot](../assets/sacn_monitor.png?raw=true)

## Depends on

- python3
- Gtk
- [sACN](https://github.com/Hundemeier/sacn) module

For Windows 10, see [PyGobject](https://pygobject.readthedocs.io/en/latest/getting_started.html#windows-getting-started).

## Usage

Monitored universes are define with UNIVERSES in monitor.py

```bash
$ git clone https://github.com/mikacousin/sacn_monitor.git
$ cd sacn_monitor
$ python monitor.py
```

## Profiling

Simply set the `SACN_MONITOR_PROFILING` environment variable to 1, like so:

```bash
$ SACN_MONITOR_PROFILING=1 python monitor.py
```

A file named `sacn_monitor-runstats` will be created in the current directory, a handy tool to examine it is `gprof2dot.py`. After install it, run:

```bash
$ gprof2dot -n0 -e0 -f pstats sacn_monitor-runstats | dot -Tsvg -o callgraph.svg
$ xdg-open callgraph.svg
```
