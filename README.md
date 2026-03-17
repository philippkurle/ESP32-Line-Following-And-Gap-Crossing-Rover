# Line-Following and Gap-Crossing Rover

This repository contains the rover control logic I developed for a university group project. My contribution focused on implementing the decision-making logic for line following and gap crossing on an ESP32-based rover.

## Overview

The rover follows a black line and is able to cross gaps in the track. To achieve this, it reads two brightness sensors via analogue-to-digital conversion and uses threshold-based logic to distinguish between black and white surfaces.

## System Interface and Technologies Used

- ESP32
- MicroPython
- Analogue brightness sensors
- Bluetooth connection
- Bluefruit Connect smartphone app for status messages and notifications
- Pymakr for uploading and interacting with the rover code

## My Contribution

The code required to establish a Bluetooth connection, initialise the ESP32 pins, and control the motors was already provided. My work focused on the rover's navigation and decision-making behaviour.

## Control Concept

The rover continuously reads two brightness sensors, compares the readings against a calibrated threshold, and selects motor commands based on a rule-based decision system. Additional logic handles gap detection, directional bias estimation, and track exit behaviour.

## Line-Following Logic

After testing the sensor readings multiple times, a stable threshold for detecting black was determined. Based on this threshold, the following control logic was implemented:

- If both sensors detect black, the rover drives straight. 
- If one sensor detects white, the rover corrects its path by following a curved trajectory.

## Gap-Crossing Logic

I developed and tested two different gap-crossing strategies:

### Curved crossing
Some gaps were located on shorter track sections with slight curvature. In these cases, the rover could not reliably cross in a straight line and failed to re-enter the track correctly. To solve this, I implemented a curved crossing strategy: the rover begins the crossing on a curved trajectory and, if the track is not detected again, switches to the opposite trajectory.

[![Curved crossing demo](docs/images/curved_crossing_thumbnail.png)](https://github.com/user-attachments/assets/b32d4a72-7c75-41c8-95c8-d1e1f8f249d9)

### Straight crossing
For tracks without curved sections, I developed a second version using straight gap crossing. This version was used in the final test.

[![Straight crossing demo](docs/images/straight_crossing_thumbnail.png)](https://github.com/user-attachments/assets/fbd1173c-5b01-44a4-aa4f-7305391d7ac3)

## Additional Logic

If crossing a gap takes too long, the rover assumes it has reached the largest gap on the track and increments a counter. Once this counter reaches 2, the rover uses that gap as the designated exit point.

During the first 3.5 seconds of operation, the rover counts left and right corrections to determine a directional bias, allowing the rover to infer the track's overall direction. This bias is then used to decide the direction in which the rover begins crossing a gap in the curved-crossing version, as well as the direction in which it exits the track in both versions. 

After leaving the track through the largest gap, the rover stops and must be restarted manually.

## Repository Structure

- `curved-crossing-logic/` – rover navigation and control logic for curved gaps
- `straight-crossing-logic/` – rover navigation and control logic for tracks with straight gaps only
- `docs/images/` – thumbnails used in the README and additional images



