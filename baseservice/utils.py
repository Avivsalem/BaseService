import threading
from typing import Collection, TypeVar, List, Iterator, Generic, Callable, Optional
from itertools import cycle, islice


class KwargsException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs


TItemType = TypeVar('TItemType')


class StatefulListIterator(Collection[TItemType]):
    def __init__(self, items: List[TItemType]) -> None:
        self._items = items
        self._item_count = len(items)
        self._item_cycle = cycle(self._items)

    def __contains__(self, __x: object) -> bool:
        return self._items.__contains__(__x)

    def __len__(self) -> int:
        return self._item_count

    def __iter__(self) -> Iterator[TItemType]:
        return islice(self._item_cycle, self._item_count)


TEventType = TypeVar('TEventType')


class Event(Generic[TEventType]):
    def __init__(self) -> None:
        self._handlers: List[Callable[[TEventType], None]] = []

    def register_handler(self, handler: Callable[[TEventType], None]) -> None:
        self._handlers.append(handler)

    def unregister_handler(self, handler: Callable[[TEventType], None]) -> bool:
        if handler in self._handlers:
            self._handlers.remove(handler)
            return True
        return False

    def fire(self, event: TEventType, continue_after_failure: bool = True) -> bool:
        ret_val = True
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                ret_val = False
                if not continue_after_failure:
                    raise
        return ret_val


TValueType = TypeVar('TValueType')


class ThreadLocalValue(threading.local, Generic[TValueType]):
    """
    this class holds a single, thread-local value

    x = ThreadLocalValue(5)
    x.value # 5
    x.value = 7 # changes only for this thread
    """

    def __init__(self, init_value: Optional[TValueType] = None):
        self.value = init_value


class ThreadLocalMember(Generic[TValueType]):
    """
    this is a descriptor, for making thread local memebers for class:

    class MyClass:
        x = ThreadLocalMember()
        y = ThreadLocalMember(1)
        z = ThreadLocalMember()
        w = ThreadLocalMember(1)
        def __init__():
            self.x = 5
            self.w = 2

    a = MyClass():
    a.x # 5
    a.x = 7 # changes only for this thread
    a.y # 1 - the default init value for this
    a.z # raises AttributeError (z was not set on class). once it's set, then value is the init value for each thread
    a.w # 2 for this thread, 1 for any other thread (because of the default init value)
    """

    def __init__(self, init_value: Optional[TValueType] = ...):
        self._init_value = init_value

    def __set_name__(self, owner, name):
        self._public_name = name
        self._private_name = f'_thread_local_{name}'

    def _get_or_set_lv(self, instance, init_value):
        try:
            lv = getattr(instance, self._private_name)
        except AttributeError:
            lv = ThreadLocalValue(init_value)
            setattr(instance, self._private_name, lv)
        return lv

    def __get__(self, instance, owner) -> Optional[TValueType]:
        if self._init_value is not ...:
            lv = self._get_or_set_lv(instance, self._init_value)
        else:
            if not hasattr(instance, self._private_name):
                raise AttributeError(f"'{owner.__name__}' object has no attribute '{self._public_name}'")
            lv = getattr(instance, self._private_name)

        return lv.value

    def __set__(self, instance, value):
        if self._init_value is ...:
            init_value = value
        else:
            init_value = self._init_value
        lv = self._get_or_set_lv(instance, init_value)
        lv.value = value
