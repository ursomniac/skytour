# SkyTour
Plan observations using a database of DSOs.

# Checklist of changes to be made:

## Make PlanetView
* Get planet coordinates, etc.
* Create finding chart
    * Add DSOs
* Create telescopic view of the planet (with moons bright enough to be observed).

## Refactor the PlanView
* DONE: Clean up datetime stuff
    * DONE: Fix UTDT and timezone offset
    * DONE: Update ObservingLocation model to have local time zone
    * Deal with DST (somehow)
* DONE: Get Sun and Moon coordinates up front
* DONE: Create better structure for stored data

New Flow:
1. DONE: Get Sun and Moon
2. DONE: Get planets
    1. DONE: Check if planets are "up" in the window of observations
3. Send core info to template 
    1. Add links for MoonView ???
    2. And links for PlanetView
    3. DONE: Separate out DSO lists?
        1. Move DSO finder chart creation to the DSOView
        2. Remove all the plots from /media ?

### Refactor plotting
* DONE: Move Hipparcos to its own method
* DONE: Move BSC to its own method
* DONE: Move Constellation lines to its own method
* DONE: Move planet moon locations to its own method
* DONE: Move phase plot to its own method
* move annotation from plt to ax
    * move annotation code into the above methods.
* Update BSC plot to have points as an option to the BSC method
* All-sky view at start/end.

### Other new methods
Overall things:
    * figure out which units everything should be in
    * create methods for conversion

* Magnitude 
    * DONE: Should handle Moon and planets, and ???
* DONE: Angular Size (fix and refactor)

## Debug phase stuff
* DONE: Test and confirm the data are right 
    * DONE: I moved everything to routines within SkyField

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

## Environment
* Create ability to set "dark mode" on server startup.
    * Change global style/CSS to support this.