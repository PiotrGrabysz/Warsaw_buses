<img width="638" alt="sample_map" src="https://user-images.githubusercontent.com/58878073/109390984-03cd6a80-7915-11eb-9c5f-550dac456cd2.png">

# Warsaw buses

This project is the final assignment made for the Tools Supporting Data Analysis in Python classes, fall semester of 2020. It uses data from https://api.um.warszawa.pl to analyze the speed which the buses go with and their punctuality.

This is the very first version of the project.

### Content

This project consists of a two parts:

* collecting the data. You can download:
    + geolocalization data of buses (or trams) for given a period of time.
    + timetables for all the buses (or trams)


* processesing the data. You can make analysis of:
    + speed which the buses go with including locations where the speed is exceeded significantly often. For now it is assume that the buses go in a straight line.
    + buses punctuality. 

### Instalation

Run in the terminal

> `pip install git+https://gitlab.uw.edu.pl/p.grabysz/final-assignment`

All the necessary packages are automatically installed.

### Sample usage

To get familiar with the package commands and to read some of my thoughts and comments about decisions taken in this project, please read the collect_data_sample_usage.ipynb and run_data_analysis_sample_usage.ipynb from notebooks folder. You can also run in the terminal:

> `collect_data --help`

and 

> `run_data_analysis --help`
