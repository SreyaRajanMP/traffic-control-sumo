# Traffic Control Using SUMO

An adaptive traffic signal control system developed using Python and SUMO. The system monitors traffic density, dynamically changes traffic-light phases, prioritizes emergency vehicles, and provides manual signal override controls.

## Features

- SUMO traffic simulation
- Adaptive traffic signal timing based on vehicle density
- Emergency vehicle priority
- Manual traffic-light override using a Tkinter GUI
- Random simulation seed for varied traffic conditions
- Real-time traffic monitoring

## Requirements

- Python 3
- SUMO
- TraCI Python library
- Tkinter

Install TraCI:

```bash
python -m pip install traci

How to Run :
1. Install SUMO and add its bin folder to your system PATH.
2. Clone this repository:
    git clone https://github.com/SreyaRajanMP/traffic-control-sumo.git
    cd traffic-control-sumo
3. Run the traffic controller:
    python Traffic_control.py
The SUMO GUI and traffic monitoring windows will open automatically.

Project Files
- Traffic_control.py — Main traffic control program
- config.sumocfg — SUMO simulation configuration
- intersection.net.xml — Road network
- routes.rou.xml — Vehicle routes and traffic definitions
- detectors.add.xml — Traffic detector configuration
- tls.add.xml — Traffic-light configuration
- gui-settings.xml — SUMO GUI settings
- camera-output.xml — Traffic camera/detector data

Technologies Used
- Python
- SUMO
- TraCI
- Tkinter
- XML