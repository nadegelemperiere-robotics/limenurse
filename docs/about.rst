About the project
=================

Purpose and scope
-----------------


The system allows a **Raspberry Pi** to act as a bridge between a **Limelight 3A** vision camera and both an **FTC Control Hub** and a **development laptop**. It enables simultaneous access to the Limelight from both devices, facilitating vision debugging and tuning outside of competition.

Target audience
---------------

This project is intended for FTC team using a limelight 3A camera, namely :

- FTC Team Developers
- FTC Team Data Scientists
- Mentors and Coaches
- Robot Integrators

Context
-------

One of the key challenges when setting up a vision pipeline in a Limelight 3A for an FTC competition is the lack of access to real-time camera data when the Limelight is connected to the Control Hub. Although teams can initially tune their pipelines based on a database of representative images, real-world robot motion and environmental changes can create unforeseen conditions which require investigation.

When vision fails in these scenarios, diagnosing issues becomes extremely difficult without access to live images, pipeline outputs, or logs. **LimeNurse** provides detailed access to limelight vitals during the tuning phase on real scenario.

**The purpose of this project is to build a Raspberry Pi-based bridge that allows:**

- The **FTC Control Hub** to access the **Limelight** through the raspberry pi **as it would do with a real limelight** (for use in OpModes) 
- An **external laptop** to access the **Limelight's web client** simultaneously through an **ethernet interface** (for debugging and tuning)

Of course, **this solution is not legal for use in competitions** and is intended solely for **tuning and development purposes**. However, it dramatically accelerates vision pipeline refinement at a moderate cost.

Definitions, Acronyms, and Abbreviations
----------------------------------------

- `FTC`_: FIRST Tech Challenge
- `Raspberry Pi`_: A small single-board computer 
- `Control Hub`_: The FTC standard processor
- `Limelight 3A`_: A high frequency camera providing embedded and customable vision pipelines

.. _`FTC`: https://firstinspires.org 
.. _`Raspberry Pi`: https://www.raspberrypi.com
.. _`Control Hub`: https://www.revrobotics.com/rev-31-1595/
.. _`Limelight 3A`: https://docs.limelightvision.io

