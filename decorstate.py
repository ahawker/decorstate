"""
    decorstate
    ~~~~~~~~~~

    Simple "state machines" with Python decorators.

    :copyright: (c) 2015-2017 Andrew Hawker.
    :license: Apache 2.0, See LICENSE file.
"""
from __future__ import unicode_literals, print_function

import collections
import contextlib
import functools
import logging
import sys
import threading
import time


__all__ = ['transition']


LOGGER = logging.getLogger(__name__)


if sys.version_info[0] == 2:
    Condition = threading._Condition
    str_types = basestring
else:
    Condition = threading.Condition
    str_types = str


def noop(*args, **kwargs):
    """
    Dummy method that just returns :bool:`True`.
    """
    return True


def iterable(item):
    """
    Return an iterable that contains the given item or itself if it already is one.
    """
    if isinstance(item, collections.Iterable) and not isinstance(item, str_types):
        return item
    return [item] if item is not None else []


class TransitionChangedEvent(Condition):
    """
    Threading condition that is notified whenever a machine performs a state transition.
    """

    def __enter__(self):
        return super(TransitionChangedEvent, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.notify_all()
        return super(TransitionChangedEvent, self).__exit__(exc_type, exc_val, exc_tb)


class Transition(object):
    """
    Object that implements the descriptor protocol to define a transition between two states of a machine.

    Transitions are defined as a decorated methods on an instance method.

    Transitions may also define three additional decorated methods to be called during specific phases of a transition.
    The following are supported:
        @transition.guard -- Callable to return a `bool` that determines if the transition should execute.
        @transition.before -- Callable to be invoked before starting the transition.
        @transition.after -- Callable to be invoked after completing the transition.
        @transition.exit -- Callable to be invoked before the next transition is invoked to change machine state.

    Example:

    Let's take the example of a simple light switch.

    import decorstate

    class LightSwitch(object):
        state = 'off'

        @decorstate.transition('off', 'on')
        def on(self, *args, **kwargs):
            print 'Let there be light!'

        @decorstate.transition('on', 'off')
        def off(self, *args, **kwargs):
            print 'The darkness engulfs you'

    >>> switch = LightSwitch()
    >>> switch.state
    'off'
    >>> switch.on()
    >>> switch.state
    'on'
    >>> switch.off()
    >>> switch.state
    'off
    """

    #: Default state of the machine if the :attr:`state` is not defined.
    default_state = None

    #: Default transition of the machine if the :attr:`transition` is not defined.
    default_transition = None

    #: Default transition event of the machine to create :attr:`transition_event` instances.
    default_transition_event = TransitionChangedEvent()

    def __init__(self, current_state=None, next_state=None, action=None, condition=None,
                 enter=None, exit=None, before=None, after=None):
        self.current_state = current_state
        self.next_state = next_state
        self.action = action
        self.condition = condition or noop
        self.on_enter = enter or noop
        self.on_exit = exit or noop
        self.on_before = before or noop
        self.on_after = after or noop

    def __call__(self, func, *args, **kwargs):
        if func is not None:
            functools.update_wrapper(self, func)
            LOGGER.debug('Creating transition for callable "{}"'.format(func.__name__))
        return self.update(action=func)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.wrapper(instance)

    @property
    def name(self):
        return self.action.__name__ if self.action else ''

    def update(self, action=None, condition=None, enter=None, exit=None, before=None, after=None):
        """
        Create a new :class:`~decorstate.Transition` instance composed of the updated transition functions.
        """
        return type(self)(current_state=self.current_state,
                          next_state=self.next_state,
                          action=action or self.action,
                          condition=condition or self.condition,
                          enter=enter or self.on_enter,
                          exit=exit or self.on_exit,
                          before=before or self.on_before,
                          after=after or self.on_after)

    def guard(self, func):
        """
        Wrapped function which is called to determine if the state machine should perform this transition.
        """
        LOGGER.debug('Registering guard callable for "{}" transition'.format(self.name))
        return self.update(condition=func)

    def enter(self, func):
        """
        Wrapped function called when transition into a new state.
        """
        LOGGER.debug('Registering enter callable for "{}" transition'.format(self.name))
        return self.update(enter=func)

    def exit(self, func):
        """
        Wrapped function called when transitioning out of the current state and to a new one.
        """
        LOGGER.debug('Registering exit callable for "{}" transition'.format(self.name))
        return self.update(exit=func)

    def before(self, func):
        """
        Wrapped function called before executing the transition action.
        """
        LOGGER.debug('Registering before callable for "{}" transition'.format(self.name))
        return self.update(before=func)

    def after(self, func):
        """
        Wrapped function called after executing the transaction action.
        """
        LOGGER.debug('Registering after callable for "{}" transition'.format(self.name))
        return self.update(after=func)

    @contextlib.contextmanager
    def transition_from(self, machine, *args, **kwargs):
        """
        Perform process of transitioning out of the current state.
        """
        with machine.transition_event:
            if machine.transition:
                machine.transition.on_exit(machine, *args, **kwargs)
            yield machine
            machine.transition = self
            machine.state = self.next_state

    @contextlib.contextmanager
    def transition_into(self, machine, *args, **kwargs):
        """
        Perform process of transitioning from the current state to a new one.

        This means performing all exit handling of the previous transition as well as the enter handling
        and action of the new transition.
        """
        # Perform exit process of the current transition before starting the enter process of the next.
        with self.transition_from(machine, *args, **kwargs) as machine:
            try:
                self.on_before(machine, *args, **kwargs)
                yield self
            except:
                raise
            finally:
                self.on_after(machine, *args, **kwargs)

    def wrapper(self, machine):
        """
        Returns a function which executes the entire flow of a transition.

        :param machine: Instance of the object whose functions are decorated with :func:`~decorstate.transition`.
        """
        def decorator(*args, **kwargs):
            """
            Decorator which encapsulates execution of a single transition.
            """
            state = machine.state

            # Do not perform transition if the current state of the machine
            # and the required current state of the transition do not match.
            if state not in iterable(self.current_state):
                LOGGER.debug('Transition not supported from state "{}"'.format(state))
                return state

            # Ignore transitions whose guard conditions fail to return True.
            if self.condition and not bool(self.condition(machine, *args, **kwargs)):
                LOGGER.debug('Guard condition failed for transition from state "{}"'.format(state))
                return state

            LOGGER.debug('Transitioning from "{}" to "{}"'.format(state, self.next_state))

            # Perform the transition from the previous state to new.
            # This includes calling performing the exit phase of the previous state/transition
            # and the enter/action of the new one.
            with self.transition_into(machine, *args, **kwargs) as new:
                new.action(machine, *args, **kwargs)
                return new.next_state

        # Attach descriptor and helper functions to the decorator for easy use.
        decorator = functools.update_wrapper(decorator, self.action)
        decorator.wait = functools.partial(wait_for_state, machine, self.next_state)
        decorator.transition = self

        # Set default values on the instance that is using this descriptors if they don't already have them set.
        set_attr_default(machine, 'state', self.default_state)
        set_attr_default(machine, 'transition', self.default_transition)
        set_attr_default(machine, 'transition_event', self.default_transition_event)

        return decorator


transition = Transition


def wait_for_state(machine, state, timeout=None):
    """
    Wait until the given machine transitions into a specific state.

    :param machine: Machine to wait for a transition into a specific state
    :param state: State to wait for the machine to transition into
    :param timeout: Timeout in seconds to wait for transition; default: None
    """
    end = None
    remaining = timeout

    if not initialized(machine):
        return False

    with machine.transition_event:
        while machine.state != state:
            if timeout is not None:
                if end is None:
                    end = time.time() + timeout
                else:
                    remaining = end - time.time()
                    if remaining <= 0:
                        return False
            machine.transition_event.wait(remaining)

    return True


def set_attr_default(obj, name, default=None):
    """
    Set the value of an attribute on the given object if it isn't yet defined.
    """
    if not hasattr(obj, name):
        setattr(obj, name, default)


def initialized(machine):
    """
    Check to see if the given machine is initialized.

    :param machine: Machine to check to see if default attributes are set
    :return: `True` if the machine has its attributes set, `False` otherwise
    """
    return all(hasattr(machine, attr) for attr in ('state', 'transition', 'transition_event'))
