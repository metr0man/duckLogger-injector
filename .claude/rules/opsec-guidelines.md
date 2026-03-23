# OpSec Guidelines for Injection

## 1. No Blocking Operations

All delays and waits **must** use `asyncio.sleep()`. Never use `time.sleep()` during injection — it blocks the entire event loop and stalls both the HTTP server and UART frame processing.

```python
# Correct
await asyncio.sleep(ms / 1000)

# Forbidden during injection
time.sleep(ms / 1000)
```

Any function in the injection path that contains a delay must be an `async def` and must be awaited.

## 2. Caps Lock State Awareness

Before injecting any `STRING` content, check the current `KeyboardLED.caps_lock` state. Injecting characters without accounting for caps lock will invert the case of all letters.

**Rule:** At the start of every injection sequence, read `KeyboardLED.caps_lock`:

- If `caps_lock` is `True`, letters that should be lowercase must set `mod_byte |= 0x02` (Shift) to cancel the lock. Letters that should be uppercase need no modifier.
- If `caps_lock` is `False`, use the standard mapping: uppercase → set Shift, lowercase → no modifier.

Do not toggle caps lock on or off as part of an injection sequence. Work with the existing state to avoid a visible, unintended caps lock toggle on the target keyboard.

## 3. Physical Keyboard Collision Handling

When an injection sequence is active, incoming UART frames from the physical keyboard (via `UARTBuffer`) must not be processed normally — delivering both injected and live keystrokes simultaneously will corrupt the output on the target.

Use one of two strategies (choose per implementation context):

### Option A — Queue (preferred for transparent pass-through)

Pause normal processing of `UARTBuffer` frames for the duration of the injection. Buffer incoming physical frames in a `collections.deque` with a fixed max length (e.g., 32 frames). After injection completes, drain and process the queued frames in order.

```python
# Pseudocode
injecting = True
# ... inject frames ...
injecting = False
while queued_frames:
    frame = queued_frames.popleft()
    process(frame)
```

### Option B — Drop (acceptable when injection takes priority)

While `injecting` is `True`, discard incoming UART frames without logging or re-emitting them. Use this only when keystroke loss during injection is explicitly acceptable.

In both cases, the `injecting` flag must be an `asyncio`-safe boolean (a plain `bool` is safe since MicroPython's asyncio is cooperative — no mutex needed).

## 4. UART Write Contention

Both `KeyboardLED.update_led()` and the injection path write to the same `UART` object. Do not interleave these writes — an LED control frame mid-injection produces a malformed sequence on the CH9350.

Suspend `KeyboardLED` UART writes for the duration of each injected key frame pair (press + release). Resume after the release frame is sent.
