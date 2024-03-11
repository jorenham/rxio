<h1 align="center">RxIO</h1>

<p align="center">
    <em>Declarative Reactive programming in modern Python</em>
</p>

<p align="center">
    <a href="https://github.com/jorenham/rxio/actions?query=workflow%3ACI">
        <img
            alt="Continuous Integration"
            src="https://github.com/jorenham/rxio/workflows/CI/badge.svg"
        />
    </a>
    <!-- <a href="https://pypi.org/project/rxio/">
        <img
            alt="PyPI"
            src="https://img.shields.io/pypi/v/rxio?style=flat"
        />
    </a> -->
    <!-- <a href="https://github.com/jorenham/rxio">
        <img
            alt="Python Versions"
            src="https://img.shields.io/pypi/pyversions/rxio?style=flat"
        />
    </a> -->
    <a href="https://github.com/jorenham/rxio">
        <img
            alt="License"
            src="https://img.shields.io/github/license/jorenham/rxio?style=flat"
        />
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img
            alt="Ruff"
            src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"
        />
    </a>
    <a href="https://github.com/microsoft/pyright">
        <img
            alt="Checked with pyright"
            src="https://microsoft.github.io/pyright/img/pyright_badge.svg"
        />
    </a>
</p>


- :zap: Reactive
- :speech_balloon: Declarative
- :moneybag: Symbolic
- :crystal_ball: Predictable
- :globe_with_meridians: Scalable
- :electric_plug: Pluggable
- :beetle: Debuggable
- :floppy_disk: Lightweight
- :cat: Fast & Lazy
- :couple: Sync & Async
- :shipit: Not a framework

-----

> [!IMPORTANT]
> RxIO is an experimental project and has no stable interface.

The initial v0.2 prototype will require Python 3.12 or higher.
Especially the availability of PEP 965 will accelerate the prototyping process.
Once I'm satisfied with the prototype, I plan to add support for earlier
Python versions.

## Sneak Peak

```pycon
>>> from rxio import rx
>>> a, b = rx(2), rx(7)
>>> c = a * b
>>> int(c)
14
>>> a *= 3
>>> int(c)
42
```

## FAQ

> "If a tree falls in a forest and no one is around to hear it, does it make a sound?"

No. The tree was dereferenced, so RxIO inlined it into the forest.

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
