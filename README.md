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
