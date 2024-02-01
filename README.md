# Reactive I/O

-----

[![license](https://img.shields.io/github/license/jorenham/rxio?style=flat-square)](https://github.com/jorenham/rxio/blob/master/LICENSE?)

-----

**RxIO is an expertimental project, and has no stable interface.**

The earlier 0.1.* versions won't be continued;
RxIO 0.2 will be complete restart, and switched to a BSD-3 license.

At the moment only Python 3.12 is supported. This makes prototyping easier.
Once the prototype is ready, support will be added for earlier Python versions.

## Optimistic Design Goals

With the current ideas that I've come up with, I believe that the following design goals 
should be achieveable. But as I'll (slowly) work on the prototype, there's a good chance
that I'll adjust these design goals. 
Some might call that cheating, I call it agile.

And now for some esoteric jargon:
RxIO is inspired by push-pull FRP, symbolic programming, the composition API of Vue.js,
PostgreSQL's transaction isolation mechanisms.

Mix all of that up, and you'll get functionality resembling that of spreadsheet software, 
but more way more powerful, and working natively in modern Python.

### API

- provides both sync and async interfaces
- documentation for humans
- not a framework: can be integrated without rewriting your codebase
- lightweight and portable: no required runtime dependencies
- pluggable and extensible backends, e.g. threading, asyncio, joblib, or redis

### Error handling and debugging

- all exceptions raise, unless explicitly silenced
- exceptions raise as soon as possible
- and their tracebacks are concise and helpful
- plays nicely with debuggers
- logs helpful messages, if you want it to
- no deadlock by design, a variable can even depend on itself

### Performance

- maximally lazy; *if a tree falls in a forest and no one is around to hear it, it doesn't make a sound*
- vertically scalable; dereferenced nodes get absorbed, symbolic optimization might be employed
- horizontally scalable; doesn't require central synchronization
- robust to failures: 

### Code quality

- fully typed, and strictly type-checked
- thoroughly [hypothesis](https://hypothesis.readthedocs.io/en/latest/)-tested
- strict code style, enforced by [ruff](https://docs.astral.sh/ruff/)
- all (public) methods have docstrings, preferrably with doctest-able examples

## Use cases

- state management
- bridging sync and async code
- front-end web apps, using e.g. pyodide or pyscript
- mobile apps, with e.g. [kivy](https://kivy.org/)
- GUI's based e.g. with TkInter, PyQT, or wxPython
- interactive data visualization, e.g. with bokeh, plotly, panels, or dash
- realtime webservers, e.g. with HTTP/3 or WebRTC
- trading bots
- robotics
- home automation
- automation within Excel spreadsheets

... so that's basically anything that deals with I/O or state-management.
