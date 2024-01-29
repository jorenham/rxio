# Reactive I/O

-----

[![license](https://img.shields.io/github/license/jorenham/rxio?style=flat-square)](https://github.com/jorenham/rxio/blob/master/LICENSE?)

-----

**RxIO is an expertimental project, and has no stable interface.**

The earlier 0.1.* versions won't be continued.

At the moment only Python 3.12 is supported. This makes prototyping easier.
Once the prototype is ready, support will be added for earlier Python versions.

## Use cases:

RxIO aims to

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

## Design Goals

- clean and intuïtive interface: concise, simple, yet powerful
- fast, even in complex applications
- documentation for humans
- solid error handling: no hidden exceptions, concise traces, helpful messages
- provides both sync and async interfaces
- maximally deterministic: failures can be reproduced
- debuggable: plays nicely with debuggers, configurable logging
- not a framework: can be integrated without rewriting your codebase
- pluggable backends, e.g. threading, asyncio, joblib, or redis
- wasm-compatible
- fully type-annotated, and understood by editors
- [hypothesis](https://hypothesis.readthedocs.io/en/latest/)-tested
- strict code style, enforced by [ruff](https://docs.astral.sh/ruff/)
- no required runtime dependencies, only optional ones
