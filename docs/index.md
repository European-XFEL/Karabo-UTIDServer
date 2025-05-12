# UTID Server

The `UTIDServer` device  provides Universal Unique Timing Identifiers (UTID)s
to a distributed Karabo installation, by emitting `signalTimeTick`s.

In the EuXFEL context a UTID corresponds to a train id.

In this basic implementation the POSIX timestamp is used to deduce the
UTID on the precision of `period`.

The device can be subclassed to implement more sophisticated timing
provision, e.g. on-top of a protocol like White Rabbit. In this case
the `get_utid` needs to be overwritten.

## Concept

The graph below shows the general timing concept used in Karabo to 
distribute UTIDs. This device is what is called a `Time Server` in the
graph. It calls `signalTimeTick` every `updatePeriod` $\Delta t_U$, passing
the `period` $\delta t_p$ with which device servers internally interpolate the
UTIDs.

``` mermaid

erDiagram
direction LR

    "Time Server" ||--o{ "Device Server C++" : "signalTimeTick ($$\Delta t_U$$)"
    "Device Server C++" ||--o{ "REMOTE/DEVICE/A" : "slotTimeTick ($$\delta t_p$$)"
    "Device Server C++" ||--o{ "REMOTE/DEVICE/B" : "slotTimeTick ($$\delta t_p$$)"
    "Device Server C++" ||--o{ "..." : "slotTimeTick ($$\delta t_p$$)"

    "Time Server" ||--o{ "Device Server Bound" : "signalTimeTick ($$\Delta t_U$$)"
    "Device Server Bound" ||--o{ "REMOTE/DEVICE/C" : "slotTimeTick ($$\delta t_p$$)"
    "Device Server Bound" ||--o{ "REMOTE/DEVICE/D" : "slotTimeTick ($$\delta t_p$$)"
    "Device Server Bound" ||--o{ "...." : "slotTimeTick ($$\delta t_p$$)"

    "Time Server" ||--o{ "Device Server Karathon" : "signalTimeTick ($$\Delta t_U$$)"
    "Device Server Karathon" ||--o{ "REMOTE/DEVICE/E" : "TimeMixin.get_timestamp() ($$\delta t_p$$)"
    "Device Server Karathon" ||--o{ "REMOTE/DEVICE/F" : "TimeMixin.get_timestamp() ($$\delta t_p$$)"
    "Device Server Karathon" ||--o{ "....." : "TimeMixin.get_timestamp() ($$\delta t_p$$)"
```

## Configuration Options

The device has two configuration options. The **period** specifies the
base period between two UTIDs in milliseconds. The **updatePeriod**
property determines how frequently a `signalTimeTick` is actually sent to
the distributed system. It should be equal to, or larger `period`. Karabo
servers internally interpolate between `signalTimeTicks`, so a larger value
here can be used to reduce broker traffic.
