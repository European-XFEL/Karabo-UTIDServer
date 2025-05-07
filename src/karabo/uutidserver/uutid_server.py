from datetime import datetime

from karabo.middlelayer import (
    AccessLevel, AccessMode, Device, MetricPrefix, Signal, State, UInt64, Unit,
    background, isSet, sleep)


class UUTIDServer(Device):
    """ A minimal device that provides unique timing identifiers (UUTID)s.

    This device provides Universal Unique Timing Identifiers (UUTID)s to
    a distributed Karabo installation, by emitting `signalTimeTick`s.

    In the EuXFEL context a UUTID corresponds to a train id.

    In this basic implementation the POSIX timestamp is used to deduce the
    UUTID on the precision of `period`.

    The device can be subclassed to implement more sophisticated timing
    provision, e.g. on-top of a protocal like White Rabbit. In this case
    the `get_uutid` needs to be overwritten.
    """
    period = UInt64(
        displayedName="Period",
        description="The time between ticks.",
        unitSymbol=Unit.SECOND,
        metricPrefixSymbol=MetricPrefix.MILLI,
        defaultValue=100,
        minInc=1,
        accessMode=AccessMode.INITONLY,
        requiredAccessLevel=AccessLevel.EXPERT,
    )

    @UInt64(
        displayedName="Publish Period",
        description="The time between ticks being published.",
        unitSymbol=Unit.SECOND,
        metricPrefixSymbol=MetricPrefix.MILLI,
        defaultValue=10000,
        minInc=10,
        accessMode=AccessMode.INITONLY,
        requiredAccessLevel=AccessLevel.EXPERT,
    )
    def publishPeriod(self, value):
        # ensure that this is larger than or equal period
        if isSet(value) and isSet(self.period):
            assert value >= self.period
        self.publishPeriod = value

    currentUUTID = UInt64(
        displayedName="Current UUTID",
        accessMode=AccessMode.READONLY,
    )

    signalTimeTick = Signal(UInt64(), UInt64(), UInt64(), UInt64())

    async def onInitialization(self):
        self._timer_task = background(self._timer())
        self.state = State.ACTIVE

    def onDestruction(self):
        if self._timer_task is not None:
            self._timer_task.cancel()

    async def _timer(self):
        # both are in ms, we convert here to .value so we can pass
        # a plain Python type to `get_uutid`.
        # we ensure we publish once, right on start-up
        time_to_publish = self.period.value
        period = self.period.value
        while True:
            uutid, sec, frac, period = await self.get_uutid(period)
            time_to_publish -= period

            if time_to_publish <= 0:
                # the period published here is in microseconds
                self.signalTimeTick(uutid, sec, frac, period * 1000)
                time_to_publish = self.publishPeriod.value
                self.currentUUTID = uutid

            await sleep(period / 1000)  # in seconds

    async def get_uutid(self, period: int) -> tuple[int, int, int, int]:
        """ Return a current UUTID

        Overwrite this method if you do not wish to use the default
        implementation which returns the current UNIX timestamp at the
        precision of `period`.
        """
        # the current timestamp in seconds, as a float, with precision up
        # to microseconds
        now = datetime.now()
        uutid = now.timestamp()

        # extract the seconds and fractional part
        sec = int(uutid)
        frac = abs(sec - uutid) * 1e9

        # push up to the period precision before the decimal
        uutid = uutid * (1000 / period)

        # finally reduce to an int, truncating towards 0 in the process.
        uutid = int(uutid)

        return uutid, sec, frac, period
