import asyncio

from rxio.core import RxVar


async def test_initial():
    v = RxVar('v')
    assert v.name == 'v'
    assert v.tick == 0
    assert v.is_empty
    assert v.value is RxVar.empty
    assert not v._future.done()

    assert await v.get_tick() == 0


async def test_set_sync():
    v = RxVar('v')

    task_get = asyncio.create_task(v.get_value())
    task_next = asyncio.create_task(v.next_value())
    task_it_next = asyncio.create_task(v.__aiter__().__anext__())

    await asyncio.sleep(0)

    v.value = 42

    assert not v.is_empty
    assert v.value == 42
    assert v.tick == 1

    assert await task_get == 42
    assert await task_next == 42
    assert await task_it_next == 42

    assert await v == 42
    assert await v.get_value() == 42


async def test_set_sync_overwrite():
    v = RxVar('v')

    it = v.__aiter__()
    tasks_early = list(map(
        asyncio.create_task,
        [v.get_value(), v.next_value(), it.__anext__()]
    ))
    await asyncio.sleep(0)  # start the early tasks

    tasks_late = list(map(
        asyncio.create_task,
        [v.get_value(), v.next_value(), it.__anext__()]
    ))
    # late tasks aren't started now

    v.value = 666
    v.value = 42

    assert not v.is_empty
    assert v.value == 42
    assert v.tick == 2

    vals_early = await asyncio.gather(*tasks_early)
    assert vals_early == [666] * 3

    assert await v == 42
    assert await v.get_value() == 42
    assert await v.__aiter__().__anext__() == 42

    assert await tasks_late[0] == 42
    # ensure the tasks could be done
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    # but they shouldn't; as the event loopt does not get control in between
    # the setter calls; only one of the two set values is registered
    assert not tasks_late[1].done()
    assert not tasks_late[2].done()

    # die pls
    tasks_late[1].cancel()
    tasks_late[2].cancel()


async def test_set_async():
    v = RxVar('v')

    task_get = asyncio.create_task(v.get_value())
    task_next = asyncio.create_task(v.next_value())
    task_it_next = asyncio.create_task(v.__aiter__().__anext__())

    await asyncio.sleep(0)

    await v.set_value(42)

    assert not v.is_empty
    assert v.value == 42
    assert v.tick == 1

    assert await task_get == 42
    assert await task_next == 42
    assert await task_it_next == 42

    assert await v == 42
    assert await v.get_value() == 42


# noinspection PyUnresolvedReferences
async def test_set_async_overwrite():
    v = RxVar('v')

    it0 = v.__aiter__()
    it0_next = v.iter_values(False)
    tasks0 = list(map(
        asyncio.create_task,
        [v.get_value(), it0.__anext__(), v.next_value(),  it0_next.__anext__()]
    ))
    await asyncio.sleep(0)  # start the early tasks

    it1 = v.__aiter__()
    it1_next = v.iter_values(False)
    tasks1 = list(map(
        asyncio.create_task,
        [v.get_value(), it1.__anext__(), v.next_value(),  it1_next.__anext__()]
    ))
    # late tasks aren't started now

    await v.set_value(666)
    await v.set_value(42)

    assert not v.is_empty
    assert v.value == 42
    assert v.tick == 2

    vals_early = await asyncio.gather(*tasks0)
    assert vals_early == [666] * 4

    vals_late = await asyncio.gather(*tasks1)
    assert vals_late == [666, 666, 42, 42]  # [current, current, next, next]

    assert await v == 42
    assert await v.get_value() == 42

    assert await v.__aiter__().__anext__() == 42
    assert await it0.__anext__() == 42
    assert await it1.__anext__() == 42
