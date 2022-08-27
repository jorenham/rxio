import asyncio

import pytest

from rxio.core import RxVar


async def test_initial():
    v = RxVar('v')
    assert v.name == 'v'
    assert v.tick == 0
    assert v.tickname == 'v@0'

    assert not v.is_set
    default = object()
    assert v.get_nowait(default) is default

    with pytest.raises(LookupError):
        v.get_nowait()


async def test_set_nowait_once():
    v = RxVar('v')
    v.set_nowait(42)

    assert v.is_set
    assert v.tick == 1
    assert v.tickname == 'v@1'

    assert v.get_nowait() == 42
    assert await v.get() == 42


async def test_set_once():
    v = RxVar('v')
    await v.set(42)

    assert v.is_set
    assert v.tick == 1
    assert v.tickname == 'v@1'

    assert v.get_nowait() == 42
    assert await v.get() == 42


async def test_set_nowait_twice():
    v = RxVar('v')

    t0 = asyncio.create_task(v.get())
    v.set_nowait(42)
    t1 = asyncio.create_task(v.get())
    v.set_nowait(69)

    assert v.is_set
    assert v.tick == 2
    assert v.tickname == 'v@2'

    assert v.get_nowait() == 69
    assert await v.get() == 69

    # expected behauviour; overwriting within the same tick is ok
    assert await t0 == 69
    assert await t1 == 69


async def test_set_twice():
    v = RxVar('v')

    tg0 = asyncio.create_task(v.get())
    tw0 = asyncio.create_task(v.wait())
    await v.set(42)
    tg1 = asyncio.create_task(v.get())
    tw1 = asyncio.create_task(v.wait())
    await v.set(69)

    assert v.is_set
    assert v.tick == 2
    assert v.tickname == 'v@2'

    assert v.get_nowait() == 69
    assert await v.get() == 69

    assert await tg0 == 42
    assert await tw0 == 42
    assert await tg1 == 42  # .get() before the second set()
    assert await tw1 == 69  # .wait() before the second set()
