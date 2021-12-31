# SkyTour
Plan observations using a database of DSOs.

# Checklist of changes to be made:

## Make PlanetView
* Get planet coordinates, etc.
* Create finding chart
    * Add DSOs
* Create telescopic view of the planet (with moons bright enough to be observed).

## Refactor the PlanView
* Clean up datetime stuff
    * Fix UTDT and timezone offset
    * Update ObservingLocation model to have local time zone
    * Deal with DST (somehow)
* Get Sun and Moon coordinates up front
* Create better structure for stored data

New Flow:
1. Get Sun and Moon
2. Get planets
    1. Check if planets are "up" in the window of observations
3. Send core info to template 
    1. Add links for MoonView ???
    2. And links for PlanetView
    3. Separate out DSO lists?
        1. Move DSO finder chart creation to the DSOView
        2 Remove all the plots from /media ?

### Refactor plotting
* Move Hipparcos to its own method
* Move BSC to its own method
* Move Constellation lines to its own method
* Move planet moon locations to its own method
* Move phase plot to its own method

### Other new methods

One overall things:
    * figure out which units everything should be in
    * create methods for conversion

* Magnitude 
    * Should handle Moon and planets, and ???
* Angular Size (fix and refactor)

## Debug phase stuff
* Test and confirm the data are right 

## Create PDF view/creation for:
* DSOs
* ObservingLocation
* Observation?  
    * This would just be a printable form.
    * Fill in things like ObservingLocation metadata, date, etc.
    * At some point add in metadata for photography...
* Planets
* Overview
    * Somehow figure out a subset of DSOs
        * maybe have PlotView create a second form to select DSOs to add to the Overview?
        * short-hand observing form?  (which things in the list did get observed?)

* Think about other solar system stuff
    * Asteroids
    * Comets
