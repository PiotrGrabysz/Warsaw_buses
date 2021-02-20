![sample_map](/uploads/d53ee890a762aa5905f2ae84f6733bf4/sample_map.png)

# Final Assignment 

Final assignment made for the Tools Supporting Data Analysis in Python classes, fall semester of 2020.

This project consists of a few parts:

* collect_data. It is for downloading data and contains functions
    + collect_busestrams() for downloading geolocalization data of buses (or trams) for given period of time.
    + collect_timetables for downloading the whole timetable (for the particular day when this function is run)


* process_data. In this module one can make analysis of
    + speed which the buses go with. Describe the notion of a location used in the solution.
    + buses punctuality. To calculate the delays for each stop I find the bus position closest to the stop. But by close I mean close in pace AND time. Why? Suppose that a bus gets to the final station, waits and then goes in the other direction. In such scenario it might pass a bus stop twice, but clearly I am interested only in one such passing. Put it differently, while analysing punctuality I want to know when the bus is near the stop but only if this bus is going in the right direction. So I take the distance between the stop and the bus and add some 'penalty' which is the difference between bus timestamp and the schedule's time of arrival.

### Instalation

Run in the terminal

> `pip install git+https://gitlab.uw.edu.pl/p.grabysz/final-assignment`

To see the list of required site packages, please see the requirements.txt file.

### Sample usage

To get familiar with the module commands and to read some of my thoughts and comments about decisions taken in this project, please read the collect_data_sample_usage.ipynb and run_data_analysis_sample_usage.ipynb from notebooks folder. You can also run in the terminal:

> `collect_data --help`

and 

> `run_data_analysis --help`
