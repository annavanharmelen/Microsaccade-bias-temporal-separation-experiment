"""
This file contains the functions necessary for
creating the interactive response dial at the end of a trial.
To run the 'microsaccade bias temporal separation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual, event
from psychopy.hardware.keyboard import Keyboard
from stimuli import (
    create_colour_wheel,
    RADIUS_COLOUR_WHEEL as RADIUS,
    INNER_RADIUS_COLOUR_WHEEL as INNER_RADIUS,
)
from time import time
import numpy as np
from eyetracker import get_trigger
import random


def make_marker(radius, inner_radius, settings):
    # Create a marker for the selected colour preview
    marker = visual.Rect(
        settings["window"],
        width=15,
        height=settings["deg2pix"](radius - inner_radius),
        fillColor=None,
        lineColor=(1, 1, 1),
    )

    return marker

def get_colour(mouse_pos, offset, colours):
    # Extract mouse position
    mouse_x, mouse_y = mouse_pos

    # Determine current colour based on mouse position
    angle = (np.degrees(np.arctan2(mouse_y, mouse_x)) + 360) % 360
    colour_angle = angle - offset
    if colour_angle > 360:
        colour_angle -= 360
    current_colour = colours[int(colour_angle)]

    return current_colour, angle

def move_marker(marker, mouse_pos, offset, colours, radius, inner_radius, settings):
    # Get current selected colour and use for marker
    current_colour, angle = get_colour(mouse_pos, offset, colours)
    marker.fillColor = current_colour

    # Fix the marker's position to the colour wheel's radius
    marker.pos = (
        settings["deg2pix"]((radius + inner_radius) / 2 * np.cos(np.radians(angle))),
        settings["deg2pix"]((radius + inner_radius) / 2 * np.sin(np.radians(angle))),
    )

    # Rotate the marker to follow the curve of the donut
    marker.ori = -angle + 90  # Adjust to span across the width of the donut

    marker.draw()

    return current_colour


def evaluate_response(selected_colour, target_colour, colours):
    # Determine position of both colours on colour wheel
    selected_colour_id = colours.index(selected_colour) + 1
    target_colour_id = colours.index(target_colour) + 1

    # Calculate the distance between the two colours
    abs_rgb_distance = abs(selected_colour_id - target_colour_id)
    
    if abs_rgb_distance > 180:
        rgb_distance = 360 - abs_rgb_distance
    else:
        rgb_distance = abs_rgb_distance

    performance = round(100 - rgb_distance / 180 * 100)

    return {
        "abs_rgb_distance": abs_rgb_distance,
        "rgb_distance": rgb_distance,
        "performance": performance,
    }


def get_response(
    target_colour,
    positions,
    target_item,
    settings,
    testing,
    eyetracker,
):
    keyboard: Keyboard = settings["keyboard"]

    # Check for pressed 'q'
    check_quit(keyboard)

    # These timing systems should start at the same time, this is almost true
    idle_reaction_time_start = time()
    keyboard.clock.reset()

    # Prepare the colour wheel and initialise variables
    colours = settings["colours"]
    offset = random.randint(0, 360)
    colour_wheel = create_colour_wheel(offset, settings)
    mouse = event.Mouse(visible=False, win=settings["window"])
    mouse.getPos()
    marker = make_marker(RADIUS, INNER_RADIUS, settings)
    selected_colour = None

    # Wait until participant starts moving the mouse
    while not mouse.mouseMoved():
        for wedge in colour_wheel:
            wedge.draw()
        settings["window"].flip()
    response_started = time()
    idle_reaction_time = response_started - idle_reaction_time_start

    if not testing and eyetracker:
        trigger = get_trigger("response_onset", positions, target_item)
        eyetracker.tracker.send_message(f"trig{trigger}")

    # Show colour wheel and get participant response
    while not selected_colour:
        # Draw each wedge
        for wedge in colour_wheel:
            wedge.draw()

        # Move the marker
        current_colour = move_marker(
            marker, mouse.getPos(), offset, colours, RADIUS, INNER_RADIUS, settings
        )

        # Flip the display
        settings["window"].flip()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse click
            selected_colour = current_colour

    response_time = time() - response_started

    if not testing and eyetracker:
        trigger = get_trigger("response_offset", positions, target_item)
        eyetracker.tracker.send_message(f"trig{trigger}")

    return {
        "idle_reaction_time_in_ms": round(idle_reaction_time * 1000, 2),
        "response_time_in_ms": round(response_time * 1000, 2),
        "selected_colour": selected_colour,
        "colour_wheel_offset": offset,
        **evaluate_response(selected_colour, target_colour, colours),
    }


def wait_for_key(key_list, keyboard):
    keyboard: Keyboard = keyboard
    keyboard.clearEvents()
    keys = event.waitKeys(keyList=key_list)

    return keys


def check_quit(keyboard):
    if keyboard.getKeys("q"):
        raise KeyboardInterrupt()
