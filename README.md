# Reactive I/O

-----

[![license](https://img.shields.io/github/license/jorenham/rxio?style=flat-square)](https://github.com/jorenham/rxio/blob/dev/LICENSE?)
[![CI](https://github.com/jorenham/rxio/actions/workflows/CI.yml/badge.svg)](https://github.com/jorenham/rxio/actions/workflows/CI.yml)

-----

**RxIO is an experimental project and has no stable interface.**

RxIO v0.2 won't build upon v0.1, and will switch to a BSD-3 license.

The initial v0.2 prototype will require Python 3.12 or higher.
Especially the availability of PEP 965 will accelerate the prototyping process.
Once I'm satisfied with the prototype, I plan to add support for earlier
Python versions.

## Optimistic Design Goals

With the current ideas that I've come up with,
I believe that the following design goals should be achievable.
But as I (slowly) work on the prototype,
there's a good chance that the design goals require adjustment.
Some might call that cheating; I call it agile.

And now for some esoteric jargon:
RxIO is inspired by push-pull FRP,
symbolic programming,
the composition API of Vue.js,
PostgreSQL's transaction isolation mechanisms,
and AnyIO's interface.

Mix all of that up,
and you'll get functionality resembling that of spreadsheet software,
but more way more powerful, and working natively in modern Python.

### API

- provides both sync and async interfaces
- documentation for humans
- not a framework: can be integrated without rewriting your codebase
- lightweight and portable: no required runtime dependencies
- pluggable and extensible backends, e.g. threading, asyncio, joblib, or redis

### Error handling and debugging

- all exceptions should raise, unless explicitly silenced
- exceptions raise as soon as possible
- and their tracebacks are concise and helpful
- plays nicely with debuggers
- configurable logging, with helpful messages
- no deadlock by design, a variable can even depend on itself

### Performance

- maximally lazy; *if a tree falls in a forest and no one is around to hear it,
  it doesn't make a sound*
- vertically scalable; dereferenced nodes get absorbed, symbolic optimization
  might be employed
- horizontally scalable; doesn't require central synchronization
- robust to failures:

### Code quality

- fully type-annotated, and strictly type-checked
- thoroughly [hypothesis](https://hypothesis.readthedocs.io/en/latest/)-tested
- strict code style, enforced by [ruff](https://docs.astral.sh/ruff/)
- all (public) methods have docstrings, preferably with (doctest) examples

## Use cases

- state management
- bridging sync and async code
- front-end (WASM) web apps, e.g. using pyodide or pyscript
- mobile apps, with e.g. [kivy](https://kivy.org/)
- GUI's e.g. with TkInter, PyQT, or wxPython
- interactive data visualization, e.g. with bokeh, plotly, panels, or dash
- real-time web servers, e.g. with HTTP/3 or WebRTC
- trading bots
- robotics
- home automation
- automation within Excel spreadsheets

... so that's anything that deals with I/O or state management.
