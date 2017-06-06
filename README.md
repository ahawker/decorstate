# decorstate

[![Build Status](https://travis-ci.org/ahawker/decorstate.svg?branch=master)](https://travis-ci.org/ahawker/decorstate)
[![Test Coverage](https://codeclimate.com/github/ahawker/decorstate/badges/coverage.svg)](https://codeclimate.com/github/ahawker/decorstate/coverage)
[![Code Climate](https://codeclimate.com/github/ahawker/decorstate/badges/gpa.svg)](https://codeclimate.com/github/ahawker/decorstate)
[![Issue Count](https://codeclimate.com/github/ahawker/decorstate/badges/issue_count.svg)](https://codeclimate.com/github/ahawker/decorstate)

[![PyPI Version](https://badge.fury.io/py/decorstate.svg)](https://badge.fury.io/py/decorstate)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/decorstate.svg)](https://pypi.python.org/pypi/decorstate)
[![PyPI Downloads](https://img.shields.io/pypi/dm/decorstate.svg)](https://pypi.python.org/pypi/decorstate)

Build dumb little "state machines" with Python decorators.

### Installation

To install decorstate from [pip](https://pypi.python.org/pypi/pip):
```bash
    $ pip install decorstate
```

To install decorstate from source:
```bash
    $ git clone git@github.com:ahawker/decorstate.git
    $ cd decorstate
    $ python setup.py install
```

### Usage

How do I use this pile?

```python
import decorstate

class Switch(object):
    state = 'off'

    @decorstate.transition('off', 'on')
    def on(self, *args, **kwargs):
        print 'You turned me on!'

    @decorstate.transition('on', 'off')
    def off(self, *args, **kwargs):
        print 'You turned me off!'

>>> switch = Switch()
>>> switch.state
'off'
>>> switch.on()
You turned me on!
'on'
>>> switch.off()
You turned me off!
'off'
```

A switch? Really? How lame.


```python
import decorstate

class BrokenSwitch(object):
    state = 'off'

    @decorstate.transition('off', 'on')
    def on(self, *args, **kwargs):
        print 'You turned me on!'

    @decorstate.transition('on', 'off')
    def off(self, *args, **kwargs):
        print 'You turned me off? Nah!'

    @off.guard
    def off(self, *args, **kwargs):
        print 'Ha! I laugh at your feeble attempt!'

>>> broken_switch = BrokenSwitch()
>>> broken_switch.state
'off'
>>> broken_switch.on()
You turned me on!
'on'
>>> broken_switch.off()
Ha! I laugh at your feeble attempt!
'on'
>>> broken_switch.state
'on'
>>> broken_switch.off()
Ha! I laugh at your feeble attempt!
'on'
>>> broken_switch.state
'on'
```

A broken switch? Yawn.


```python
import decorstate

class InstantOffSwitch(object):
    state = 'off'

    @decorstate.transition('off', 'off')
    def on(self, *args, **kwargs):
        print 'You turned me on!'

    @decorstate.transition('on', 'off')
    def off(self, *args, **kwargs):
        print 'You turned me off!'

    @on.after
    def on(self, *args, **kwargs):
        print 'Ha! No light for you!'

>>> instant_off_switch = InstantOffSwitch()
>>> instant_off_switch.state
'off'
>>> instant_off_switch.on()
You turned me on!
Ha! No light for you!
'off'
>>> instant_off_switch.state
'off'
```

Well, that's kinda mean.


```python
import decorstate
import random

class IoTSwitch(object):
    state = 'off'

    @decorstate.transition('off', 'off')
    def on(self, *args, **kwargs):
        print 'You turned me on? Maybe...'

    @decorstate.transition('on', 'off')
    def off(self, *args, **kwargs):
        print 'You turned me off? Maybe...'

    @on.guard
    def on(self, *args, **kwargs):
        return self.coin_flip()

    @off.guard
    def off(self, *args, **kwargs):
        return not self.coin_flip()

    @staticmethod
    def coin_flip():
        return random.randint(1, 2) == 1

>>> iot_switch = IoTSwitch()
>>> iot_switch.state
'off'
>>> iot_switch.on()
'off'
>>> iot_switch.on()
'off'
>>> iot_switch.on()
'off'
>>> iot_switch.on()
You turned me on? Maybe...
'on'
>>> iot_switch.off()
'on'
>>> iot_switch.off()
'on'
>>> iot_switch.off()
'on'
>>> iot_switch.off()
'on'
>>> iot_switch.off()
You turned me off? Maybe...
'off'
```

Hey now, why you hating? Internet powered light switches are next level shit. My living room has its own twitter feed.


### Why?

I was interesting in doing something a bit more complex using the Python [descriptor protocol](https://docs.python.org/2/howto/descriptor.html).

### TODO?

Random thoughts and musing about potential changes/features.

*  Consider adding the @machine decorator back as currently, you cannot use the "state", "transition" and "transition_event" attributes until the first transition has been performed since they are lazy created.
*  Add event handler that fires only when "entering" a state and not when you perform multiple transitions but stay in the same state.

### License

[Apache 2.0](LICENSE)
