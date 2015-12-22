# decorstate

[![Build Status](https://travis-ci.org/ahawker/decorstate.svg)](https://travis-ci.org/ahawker/decorstate)

Build dumb little "state machines" with Python decorators.

## Usage

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
