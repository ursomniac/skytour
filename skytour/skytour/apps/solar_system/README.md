# Solar System App

This has the views for:

* Planet Listing - just links to the Planet Detail pages
* Planet Detail
    * show metadata for a given UTDT;
    * finder chart
    * telescope view
    * form to change to a different UTDT and location

## Example Telescope View

![download-2](https://user-images.githubusercontent.com/485748/147896952-2d741fdb-f1c8-4f5d-8de0-de127618802e.png)

## Example Finder Chart

![download](https://user-images.githubusercontent.com/485748/147896978-e9225e7c-6b58-4e2c-adb8-fa89e4f82743.png)

(Note proximity of Venus to Mercury, and that Mercury is crossing in front of Messier 75.)   Of course it was cloudy.


# How this is constructed:

## Models

Each type of solar-system object has a model:

### Planets

Excludes Earth, and the dwarf planets (mostly because they're too faint to be reachable with my scope).  Ceres is
under Asteroid because getting its position, etc. uses the same setup as for the other minor planets.

### Sun and Moon
Treated separately.   Right now the Sun has minimal coding, mostly "where is the Sun from the POV of the Earth".

### Asteroids

This is a subset of asteroids whose orbits take it close enough to Earth that their visual magnitiude is < 12.
HOWEVER, there are several holes in this:

1. I've missed a few main-belt asteroids that fall into this situation.
2. I've added a few that do not get that brights.
3. I've ignored the very rare, very close approaches of NEOs.

Basically this is a first pass and I don't know what I want to do.

### Comets

Still TBD;  I need to find a way to just get "the ones that matter now" instead of getting a large sample.
PROBABLY what I'll do is NOT to use a source from the MPC, but just have the orbital elements be part of the 
model, and let the user deal with it.

### Meteor Showers

Not much to say here - this is mostly involved with the Calendar.

## Backend Code

Each object type has a file (e.g., `planets.py`) that has the code for getting positions/metadata for all 
objects (to construct observing lists) and one object.

What is returned for an object is a dict with several layers, but each object follows MOSTLY the same structure, 
i.e., getting  `object['coords']['ra']` ought to return the R.A. as a float regardless of whether it's a planet,
Moon, or asteroid.

