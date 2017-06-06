"""
    tests
    ~~~~~

    Tests for the :mod:`~decorstate` module.
"""
from __future__ import unicode_literals


import collections
import decorstate
import pytest
import threading
import time


@pytest.fixture(scope='function')
def switch_factory():
    """
    Fixture that returns a factory for creating a basic Switch.
    """
    class Switch(object):

        @decorstate.transition('off', 'on')
        def on(self, *args, **kwargs):
            pass

        @decorstate.transition('on', 'off')
        def off(self, *args, **kwargs):
            pass

    return Switch


@pytest.fixture(scope='function')
def stateless_switch(switch_factory):
    """
    Fixture that represents a simple on/off switch as a "state machine" with no initial state.
    """
    return switch_factory()


@pytest.fixture(scope='function')
def switch(switch_factory):
    """
    Fixture that represents a simple on/off switch as a "state machine".
    """
    switch_factory.state = 'off'
    return switch_factory()


@pytest.fixture(scope='function')
def guarded_switch():
    """
    Fixture that represents a simple on/off switch as a "state machine" that has guard conditions
    on its transitions.
    """
    class Switch(object):
        state = 'off'

        always_on = True

        @decorstate.transition('off', 'on')
        def on(self, *args, **kwargs):
            pass

        @decorstate.transition('on', 'off')
        def off(self, *args, **kwargs):
            pass

        @off.guard
        def off(self, *args, **kwargs):
            return not self.always_on

    return Switch()


@pytest.fixture(scope='function')
def evented_switch():
    """
    Fixture that represents a simple on/off switch as a "state machine" that has event handles registered.
    """
    class Switch(object):
        state = 'off'

        exit_event = threading.Event()
        before_event = threading.Event()
        after_event = threading.Event()

        @decorstate.transition('off', 'on')
        def on(self, *args, **kwargs):
            pass

        @decorstate.transition('on', 'off')
        def off(self, *args, **kwargs):
            pass

        @on.exit
        def on(self, *args, **kwargs):
            self.exit_event.set()

        @on.before
        def on(self, *args, **kwargs):
            self.before_event.set()

        @on.after
        def on(self, *args, **kwargs):
            self.after_event.set()

    return Switch()


@pytest.mark.parametrize('item', [
    None,
    1,
    1.0,
    u'foo',
    b'bar',
    r'baz',
    '~`!@#$%^&*()_+',
    list(),
    dict(),
    set(),
    frozenset(),
    map,
    list,
    object
])
def test_iterable_always_returns_iterable(item):
    """
    Assert that :func:`~decorstate.iterable` will always return an iterable instance regardless of the input.
    """
    it = decorstate.iterable(item)
    assert isinstance(it, collections.Iterable)


@pytest.mark.parametrize('item', [
    [],
    [1, 2, 3],
    ['foo'],
    tuple(),
    dict(x=1, y=2),
    set(),
    frozenset()
])
def test_iterable_returns_original_item_when_iterable(item):
    """
    Assert that :func:`~decorstate.iterable` will always return the original item if it is an iterable.
    """
    it = decorstate.iterable(item)
    assert it is item


def test_transition_event_notifies_on_context_manager_exit():
    """
    Assert that :class:`~decorstate.TransitionChangedEvent` notifies all waiters when it exits the context manager.
    """
    transition_event = decorstate.TransitionChangedEvent()
    notified_event = threading.Event()

    def waiter(timeout=None):
        with transition_event:
            transition_event.wait(timeout)
            notified_event.set()

    t = threading.Thread(target=waiter)
    t.start()

    with transition_event:
        time.sleep(0.01)

    assert notified_event.wait(1)


@pytest.mark.parametrize(('name', 'value'), [
    ('foo', 'bar'),
    ('foo', True),
    ('baz', 10),
    ('baz', [1, 2, 3])
])
def test_set_attr_default_sets_when_not_defined(name, value):
    """
    Assert that :func:`~decorstate.set_attr_default` sets the attribute to the default value when it is
    not already set on the object.
    """
    class Foo(object):
        pass

    decorstate.set_attr_default(Foo, name, value)
    assert getattr(Foo, name) == value


def test_set_attr_default_ignores_when_defined():
    """
    Assert that :func:`~decorstate.set_attr_default` does not set the attribute to the default value when it
    is already set on the object.
    """
    class Foo(object):
        exists = True

    decorstate.set_attr_default(Foo, 'exists', 'default_value')
    assert Foo.exists is True


@pytest.mark.xfail(reason='Attibutes are lazy-created with removal of @machine decorator.')
def test_wait_for_state_returns_true_on_transition(switch):
    """
    Assert that :func:`~decorstate.wait_for_state` returns `True` on a transition.
    """
    notified_event = threading.Event()

    def waiter(timeout=None):
        switched = decorstate.wait_for_state(switch, 'on', timeout)
        if switched:
            notified_event.set()

    t = threading.Thread(target=waiter)
    t.start()

    switch.on()
    time.sleep(1)

    assert notified_event.is_set()


def test_transitions_create_default_attrs(stateless_switch):
    """
    Assert that :attr:`~state`, :attr:`~transition`, and :attr:`~transition_event` are automatically created
    on the machine instance once the first transition is invoked.
    """
    assert not hasattr(stateless_switch, 'state')
    assert not hasattr(stateless_switch, 'transition')
    assert not hasattr(stateless_switch, 'transition_event')

    stateless_switch.on()

    assert hasattr(stateless_switch, 'state')
    assert hasattr(stateless_switch, 'transition')
    assert hasattr(stateless_switch, 'transition_event')


def test_transitions_sets_attrs(switch):
    """
    Assert that :attr:`~state`, :attr:`~transition`, and :attr:`~transition_event` are set based on the
    most recent transition performed.
    """
    switch.on()

    assert switch.state == switch.on.transition.next_state
    assert switch.transition == switch.on.transition
    assert switch.transition_event == switch.on.transition.default_transition_event

    switch.off()

    assert switch.state == switch.off.transition.next_state
    assert switch.transition == switch.off.transition
    assert switch.transition_event == switch.off.transition.default_transition_event


def test_invalid_transition_maintain_current_state(switch):
    """
    Assert that executing a transition method that is invalid for the current state is a noop
    and does not perform a state transition.
    """
    assert switch.state == switch.off.transition.next_state
    switch.off()
    assert switch.state == switch.off.transition.next_state


def test_guard_false_guard_condition_blocks_transition(guarded_switch):
    """
    Assert that :meth:`~decorstate.Transition.guard` callable that returns `False` will block
    transition from executing and switching state.
    """
    guarded_switch.on()
    assert guarded_switch.state == guarded_switch.on.transition.next_state

    guarded_switch.off()
    assert guarded_switch.state == guarded_switch.on.transition.next_state

    guarded_switch.always_on = False

    guarded_switch.off()
    assert guarded_switch.state == guarded_switch.off.transition.next_state


def test_transition_events_fire(evented_switch):
    """
    Assert that :meth:`~decorstate.Transition.before`, :meth:`~decorstate.Transition.after`, and
    :meth:`~decorstate.Transition.exit` transition events all fire when performing state transitions.
    """
    assert not evented_switch.before_event.is_set()
    assert not evented_switch.after_event.is_set()
    assert not evented_switch.exit_event.is_set()

    evented_switch.on()

    assert evented_switch.before_event.is_set()
    assert evented_switch.after_event.is_set()

    evented_switch.off()

    assert evented_switch.exit_event.is_set()
