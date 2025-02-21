"""
This file contains the functions necessary for
creating and running a single trial start-to-finish,
including eyetracker triggers.
To run the 'microsaccade bias temporal separation' experiment, see main.py.

made by Anna van Harmelen, 2025
"""

from psychopy.core import wait
from time import time, sleep
from response import get_response, check_quit
from stimuli import (
    draw_fixation_dot,
    create_stimuli_frame,
    create_cue_frame,
    show_text,
)
from eyetracker import get_trigger
import random


def generate_trial_characteristics(conditions, settings):
    # Extract condition information
    target_item, informative, *positions = conditions

    # Decide on random colours of stimulus
    stimuli_colours = random.sample(settings["colours"], 2)

    # Determine target colour and position
    if target_item == 1:
        target_colour = stimuli_colours[0]
        target_position = positions[0]
    elif target_item == 2:
        target_colour = stimuli_colours[1]
        target_position = positions[1]
    else:
        raise Exception(f"Expected 1 or 2, but received {target_item!r}.")

    return {
        "ITI": random.randint(500, 800),
        "stimuli_colours": stimuli_colours,
        "positions": positions,
        "probe_colour": target_colour,
        "target_item": target_item,
        "target_colour": target_colour,
        "target_position": target_position,
        "retrocue": target_item if informative else 0,
    }


def do_while_showing(waiting_time, something_to_do, window):
    """
    Show whatever is drawn to the screen for exactly `waiting_time` period,
    while doing `something_to_do` in the mean time.
    """
    window.flip()
    start = time()
    something_to_do()
    wait(waiting_time - (time() - start))


def single_trial(
    ITI,
    stimuli_colours,
    positions,
    probe_colour,
    target_item,
    target_colour,
    target_position,
    retrocue,
    settings,
    testing,
    eyetracker=None,
):
    # Initial fixation cross to eliminate jitter caused by for loop
    draw_fixation_dot(settings)

    screens = [
        (0, lambda: 0 / 0, None),  # initial one to make life easier
        (ITI / 1000, lambda: draw_fixation_dot(settings), None),
        (
            0.25,
            lambda: create_stimuli_frame(stimuli_colours[0], positions[0], settings),
            "stimulus_onset_1",
        ),
        (0.75, lambda: draw_fixation_dot(settings), None),
        (
            0.25,
            lambda: create_stimuli_frame(stimuli_colours[1], positions[1], settings),
            "stimulus_onset_2",
        ),
        (0.75, lambda: draw_fixation_dot(settings), None),
        (
            0.25,
            lambda: create_cue_frame(retrocue, settings),
            "cue_onset",
        ),
        (1.00, lambda: draw_fixation_dot(settings), None),
    ]

    # !!! The timing you pass to do_while_showing is the timing for the previously drawn screen. !!!
    for index, (duration, _, frame) in enumerate(screens[:-1]):
        # Send trigger if not testing
        if not testing and frame:
            trigger = get_trigger(frame, positions, target_item, retrocue)
            eyetracker.tracker.send_message(f"trig{trigger}")

        # Check for pressed 'q'
        check_quit(settings["keyboard"])

        # Draw the next screen while showing the current one
        do_while_showing(duration, screens[index + 1][1], settings["window"])

    # The for loop only draws the last frame, never shows it
    # So show it here + wait
    settings["window"].flip()
    wait(screens[-1][0])

    response = get_response(
        target_colour,
        positions,
        target_item,
        retrocue,
        settings,
        testing,
        eyetracker,
    )

    # Show performance
    draw_fixation_dot(settings)
    show_text(
        f"{response['performance']}", settings["window"], (0, settings["deg2pix"](0.3))
    )

    if not testing:
        trigger = get_trigger("feedback_onset", positions, target_item, retrocue)
        eyetracker.tracker.send_message(f"trig{trigger}")

    settings["window"].flip()
    sleep(0.25)

    return {
        "condition_code": get_trigger("stimulus_onset_1", positions, target_item, retrocue),
        **response,
    }
