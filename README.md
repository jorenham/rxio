# Reactive I/O

-----

[![PyPI version shields.io](https://img.shields.io/pypi/v/rxio.svg)](https://pypi.python.org/pypi/rxio/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rxio.svg)](https://pypi.python.org/pypi/rxio/)
[![PyPI license](https://img.shields.io/pypi/l/rxio.svg)](https://pypi.python.org/pypi/rxio/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

-----

Currently in the early development phase; do not use in production.


## Roadmap:

- [x] `RxVar[T]`: variable
- [ ] `RxResult[*Ps, T]`: function result, bound to reactive args
- [ ] `Rx{Function,Method}`: returns `RxResult`, can watch when called
- [ ] (mk)docs 
- [ ] github actions
- [ ] `RxAttr[T]`: descriptor attribute / field
- [ ] `RxType`: custom rx type base: reactive attrs, methods, properties and lifecycle
- [ ] `Rx{Bool,Int,Float,Str,...}`: reactie builtin types
- [ ] `Rx{Tuple,List,Set,Dict,...}`: reactive builtin collections
- [ ] `reactive(...)`: central `Rx*` construction for (builtin) types, functions, etc.
- [ ] `Rx{File,Signal,Process,Socket,...}`: reactive IO (state) 
- [ ] [dataclasses](https://docs.python.org/3/library/dataclasses.html) integration
- [ ] (optional) [python-attrs](https://github.com/python-attrs/attrs) integration
- [ ] (optional) [pydantic](https://github.com/pydantic/pydantic) integration
