# Line-Following and Gap-Crossing Rover

This repository contains the rover control logic I developed for a university group project. My contribution focused on implementing the decision-making logic for line following and gap crossing on an ESP32-based rover.

## Overview

The rover follows a black line and crosses potential gaps in the track. In order to achieve this, it reads two brightness sensors via analog-to-digital conversion and uses threshold-based logic to distinguish between black and white surfaces.

## System Interface and Technologies

- ESP32
- MicroPython
- Analog brightness sensors
- Bluetooth communication
- Bluefruit Connect smartphone app for status messages and notifications
- Pymakr for uploading and interacting with the rover code

## My Contribution

The code required to establish a Bluetooth connection, initialize the ESP32 pins, and control the motors was already provided. My work focused on the rover's navigation and decision-making behavior.

## Control Concept

The rover continuously reads two brightness sensors, compares the readings against a calibrated threshold, and selects motor commands based on a rule-based decision system. Additional logic handles gap detection, directional bias estimation, and track exit behavior.

## Line-Following Logic

After testing the sensor readings multiple times, a stable threshold for detecting black was determined. Based on this threshold, the following control logic was implemented:

- If both sensors detect black, the rover drives straight.
- If one sensor detects white, the rover corrects its path by following a curved trajectory.

## Gap-Crossing Logic

I developed and tested two different gap-crossing strategies:

### Curved crossing
Some gaps were located on shorter track sections with slight curvature. In these cases, the rover could not reliably cross in a straight line and failed to re-enter the track correctly. I therefore implemented a curved crossing strategy, where the rover begins the crossing on a curved trajectory and switches to the opposite trajectory, if the track is not detected again.

[![Curved crossing demo](docs/images/curved_crossing_thumbnail.png)](https://github.com/user-attachments/assets/b32d4a72-7c75-41c8-95c8-d1e1f8f249d9)

### Straight crossing
For tracks without curved sections, I developed a second version using straight gap crossing. This version was then used in the final test.

[![Straight crossing demo](docs/images/straight_crossing_thumbnail.png)](https://github.com/user-attachments/assets/fbd1173c-5b01-44a4-aa4f-7305391d7ac3)

## Additional Logic

If crossing a gap takes too long, the rover assumes it has reached the largest gap on the track and increments a counter. Once this counter reaches 2, the rover uses that gap as the designated exit point.

During the first 3.5 seconds of operation, the rover counts left and right corrections to determine a directional bias, allowing it to infer the track's overall direction. In the curved-crossing version, this bias is used to decide the direction in which the rover begins crossing a gap. It is also used to determine the direction in which the rover exits the track in both versions

The rover stops and must be restarted manually, after leaving the track through the largest gap.

## Repository Structure

- `curved-crossing-logic/` – rover navigation and control logic for curved gaps
- `straight-crossing-logic/` – rover navigation and control logic for tracks with straight gaps only
- `docs/images/` – the thumbnails used in the README and additional images

## Challenges and Main Lessons

One of the main challenges was that the rover behaved reliably during basic line following, but gap crossing introduced a new source of instability. When entering a gap with poor alignment, the rover could drift away from the track, especially if the gap was longer. This showed that successful gap crossing depended not only on detecting the track correctly, but also on the rover's orientation at the moment it left the line.

I also found that reaction timing had a strong influence on performance. By removing unnecessary `sleep` calls from the main control loop, the rover was able to react more quickly to sensor readings and maintain better alignment. This improved overall stability, but it did not fully solve the problem of crossing curved gaps.

To improve performance in curved sections, I developed "soft" curve functions, where one motor continued running at a reduced output instead of being stopped completely. This produced smoother turning behaviour and significantly improved the rover's ability to recover the track after curved gaps.

However, this also revealed an important trade-off: logic that worked well for curved gaps could reduce performance on long straight gaps. In the curved-crossing approach, the rover began gap crossings with a curved trajectory, which made straight-gap recovery less reliable. Several attempts were made to distinguish straight and curved gaps earlier, but these approaches did not produce consistent results.

The final solution was to make the crossing behavior more adaptive. In the curved-crossing version, the rover begins with a curved trajectory based on the inferred track direction. If the line is not detected again within a certain time, the rover switches to a counter-curve to recover the track. In addition, timing-based logic using `ticks_ms()` and `ticks_diff()` was used to identify the largest gap based on crossing duration and treat it as the designated exit point on the second crossing.

A key lesson from the project was that robust behavior could not be achieved with a single idealized control rule. The rover's performance depended heavily on track geometry, timing, and alignment, so the control logic had to be developed iteratively and adapted to the expected course layout. This also led to the decision to keep a separate straight-crossing version, which proved to be the safer choice for the final test because the track only contained straight gaps.
