"""
This file contains the functions necessary for
creating the fixation cross and the bar stimuli.
To run the 'microsaccade bias temporal separation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy import visual
import numpy as np

DOT_SIZE = 0.1  # radius of fixation dot
ITEM_SIZE = 2  # radius of item
ITEM_ECCENTRICITY = 5  # distance from fixation to item

RADIUS_COLOUR_WHEEL = 5
INNER_RADIUS_COLOUR_WHEEL = 3.5

colour_wheel = None


def draw_fixation_dot(settings, colour="#eaeaea"):
    # Make fixation dot
    fixation_dot = visual.Circle(
        win=settings["window"],
        units="pix",
        radius=settings["deg2pix"](DOT_SIZE),
        pos=(0, 0),
        fillColor=colour,
    )

    fixation_dot.draw()


def draw_item(colour, position, settings):
    # Parse input
    if position == "left":
        pos = (-settings["deg2pix"](ITEM_ECCENTRICITY), 0)
    elif position == "right":
        pos = (settings["deg2pix"](ITEM_ECCENTRICITY), 0)
    else:
        raise Exception(f"Expected 'left' or 'right', but received {position!r}.")

    # Create stimulus
    item = visual.Circle(
        win=settings["window"],
        units="pix",
        radius=settings["deg2pix"](ITEM_SIZE),
        fillColor=colour,
        pos=pos,
    )

    item.draw()


def create_colour_wheel(settings):
    global colour_wheel

    if colour_wheel is not None:
        return colour_wheel

    # Parameters for the colour wheel
    radius = settings["deg2pix"](RADIUS_COLOUR_WHEEL)  # Radius of the colour wheel
    inner_radius = settings["deg2pix"](
        INNER_RADIUS_COLOUR_WHEEL
    )  # Inner radius of the colour wheel
    num_segments = settings["num_segments"]
    colours = settings["colours"]

    # Draw the colour wheel using segments
    colour_wheel = []
    for i in range(num_segments):
        # Create a wedge for each segment
        wedge = visual.ShapeStim(
            settings["window"],
            vertices=[
                [
                    inner_radius * np.cos(np.radians(i)),
                    inner_radius * np.sin(np.radians(i)),
                ],
                [radius * np.cos(np.radians(i)), radius * np.sin(np.radians(i))],
                [
                    radius * np.cos(np.radians(i + 1)),
                    radius * np.sin(np.radians(i + 1)),
                ],
                [
                    inner_radius * np.cos(np.radians(i + 1)),
                    inner_radius * np.sin(np.radians(i + 1)),
                ],
            ],
            fillColor=colours[i],
            lineColor=None,
        )
        colour_wheel.append(wedge)

    return colour_wheel


def show_text(input, window, pos=(0, 0), colour="#ffffff"):
    textstim = visual.TextStim(
        win=window, font="Courier New", text=input, color=colour, pos=pos, height=22
    )

    textstim.draw()


def create_stimuli_frame(colour, position, settings, fix_colour="#eaeaea"):
    draw_fixation_dot(settings, fix_colour)
    draw_item(colour, position, settings)


def create_cue_frame(target_item, settings):
    draw_fixation_dot(settings)
    show_text(target_item, settings["window"], pos=(0, settings["deg2pix"](0.3)))
