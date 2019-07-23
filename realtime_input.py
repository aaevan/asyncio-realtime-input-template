import asyncio
import os
import sys
import select
import tty
import termios
from subprocess import call

state_dict = {}
state_dict['x_coord'] = 0
state_dict['y_coord'] = 0

def isData(): 
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def clear():
    """
    clears the screen.
    """
    # check and make call for specific operating system
    _ = call('clear' if os.name =='posix' else 'cls')

async def get_key(help_wait_count=100, refresh_rate=30): 
    """
    handles raw keyboard data, passes to handle_input if its interesting.
    Also, displays help tooltip if no input for a time.

    refresh_rate sets the number of times per second that input is polled.
    """
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        key = None
        state_dict['same_count'] = 0
        old_key = None
        while True:
            await asyncio.sleep(1 / refresh_rate)
            if isData():
                key = sys.stdin.read(1)
                if key is not None:
                    await handle_input(key)
    finally: 
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings) 

async def example_async_function(interval=1):
    count = 0
    while True:
        await asyncio.sleep(interval)
        print("{} count: {}".format(interval, count))
        count += 1

async def example_changing_state():
    while True:
        await asyncio.sleep(1)
        current_coord = state_dict['x_coord'], state_dict['y_coord']
        print("Current coords: {}".format(current_coord))

async def handle_input(key):
    """
    interpret keycodes and do various actions.
    """
    print('received "{}"'.format(key))
    if key == 'w':
        state_dict['y_coord'] -= 1
        print("up!")
    if key == 'a':
        state_dict['x_coord'] -= 1
        print("left!")
    if key == 's':
        state_dict['y_coord'] += 1
        print("down!")
    if key == 'd':
        state_dict['x_coord'] += 1
        print("right!")
    elif key == 'q':
        print("Quitting!")
        loop = asyncio.get_event_loop()
        for task in asyncio.Task.all_tasks():
            task.cancel()

async def main():
    try:
        old_settings = termios.tcgetattr(sys.stdin) 
        await asyncio.gather(
            get_key(),
            example_changing_state(),
            example_async_function(5),
            example_async_function(3),
            example_async_function(2),
        )
    except asyncio.CancelledError:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings) 

asyncio.run(main())
