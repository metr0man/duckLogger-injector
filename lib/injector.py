import asyncio
from ducky_parser import parse, Delay

# Checked by the main loop: while True, incoming physical keyboard frames
# are dropped so they don't interleave with injected USB HID output.
is_injecting = False


async def run_injection(script_text, kbd, led):
    """Execute a Ducky Script string as USB HID output.

    Args:
        script_text: Raw Ducky Script (newline-separated commands).
        kbd:         Keyboard instance — frames are sent via kbd.emulate().
        led:         KeyboardLED instance — caps_lock state is read before
                     STRING expansion so injected characters match intent.

    The global ``is_injecting`` flag is set for the full duration of the
    call and is guaranteed to be cleared in the finally block even if the
    script raises an exception.
    """
    global is_injecting
    is_injecting = True
    try:
        for item in parse(script_text, caps_lock=led.caps_lock):
            if isinstance(item, Delay):
                await asyncio.sleep(item.ms / 1000)
            else:
                kbd.emulate(item)
                await asyncio.sleep(0)  # yield to event loop between frames
    finally:
        is_injecting = False
