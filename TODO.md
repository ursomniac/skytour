
# TODO

In no particular order.

## Find a better way to customize; remove hard-coded things.

1. Select the "Preferred" Observing Location; use it for defaults
     1. This would be best done using Django sessions.
2. DONE: ~~State tuple should be customizable~~ 
3. DONW: ~~Ditto time zones (although here I could just add all of them...)~~

## Run-time environment

1. Create a way to have "dark mode" at startup.
    * Figure out the CSS to do this.

## Front-End / Static

1. Better CSS, less stuff crammed in templates

## Coordinates
I've been very sloppy about which coordinate set is being used.

I THINK that's why e.g., RA/Dec values between this app and Stellarium differ a bit.   I SUSPECT that for
solar system objects I should be using APPARENT coords.

1. Research this more and refactor if necessary.

## Finalize Skyfield integration

There are still a few places where I'm using my own code instead of the routines in SkyField:

* alt/az transformation
* nutation and obliquity
* ∆T (although I like my method :-) ).
* others?

## DSO charts

Right now the only way to add a finder chart is to run a management command after adding the records.
Worse, it iterates through the whole list!

1. See if we can put this BACK into the save() for the DSO model.
2. Do this. :-)

## New Features

### SkyTrack 
This would make the plots showing an object's movement across the sky.

See the example at https://rhodesmill.org/skyfield/example-plots.html for starters.

### Jupiter Moons

I'm sure there's a way to  calculate/predict events:

* disk shadows
* occultations

### Jupiter features

DONE: ~~I'm sure there's a way to tell when the GRS is in view.~~

### Saturn

I cheat on displaying the rings.   I need to do better.

### Orrery view?

1. Inner Solar System
2. Whole Solar System
3. Planet System (so you can see when a moon is behind the planet)
 
This will also be useful if/when comets, etc. get introduced?

### Comets and other MPC items.
1. MPC-derived things (comets, etc.)

### SkyView

1. DONE: ~~Meteor shower radiants (and a model with dates, etc.)~~


### Milky Way contours... 
I'll bet that data exists somewhere!

### Almanac
To be honest it might be better just to hand-add these to the Admin, and then have the home page display a calendar.

### Home Page Improvements

1. Calendar
    1. with Moon phase
2. Add bright asteroids.

### PDF

Originally this software was just going to make lots of PDFs.

* Location PDF - to be used on site when evaluating a TBD site.
* DSO PDF - might be handier in a binder than needing a laptop in the field.
* Planet PDF - ditto
* SkyMap PDF - ditto

### Observation Log

Right now there's a FK table to DSO, but that's not the right way to do this.

(Plus we might observe other things than DSOs!)

1. Separate the ObservingLog out of DSO
2. Create/check the model
    1. Location
    2. UTDT
    3. ??? How to do drawings?   I suppose that can be ex-post-facto.
    4. Sort out descriptions so as to create useful metadata
    5. Also observing conditions/transparency/etc.
        1. For this we might want some kind of "weather" interface to get temperature/humidity/etc. info
        2. This could be another model for ObservingSession
3. Make some kind of GFK to the observing instance
4. Visual (eyepiece) vs. Image (camera)
    1. For the latter need to figure out metadata
        1. Exposure
        2. Filters
        3. Etc.


## Performance

It's realll slow.

1. Get time() stats?
2. Run all of the earth.at(t).observve(target) calls up front?
3. At the very least, survey how MANY calls like this get made for a request.
4. If there's a way to pass global information from one method/view to another (with **kwargs?) then have a form for setting UTDT/location and use that.
