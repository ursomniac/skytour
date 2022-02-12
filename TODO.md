
# TODO

In no particular order.

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

## DSO charts

Right now the only way to add a finder chart is to run a management command after adding the records.
Worse, it iterates through the whole list!

1. See if we can put this BACK into the save() for the DSO model.
2. Do this. :-)

## New Features

### Jupiter Moons

I'm sure there's a way to  calculate/predict events:

* disk shadows
* occultations

### Saturn

I cheat on displaying the rings.   I need to do better.

### Orrery view?

1. Inner Solar System
2. Whole Solar System
3. Planet System (so you can see when a moon is behind the planet)
 
This will also be useful if/when comets, etc. get introduced?

### Milky Way contours... 
I'll bet that data exists somewhere!

### Home Page Improvements

1. Calendar
    1. with Moon phase

### PDF

Originally this software was just going to make lots of PDFs.

* Location PDF - to be used on site when evaluating a TBD site.
* DSO PDF - might be handier in a binder than needing a laptop in the field.
* Planet PDF - ditto
* SkyMap PDF - ditto

## Performance

It's really slow.

1. Get time() stats?
2. Run all of the earth.at(t).observve(target) calls up front?
3. At the very least, survey how MANY calls like this get made for a request.
4. If there's a way to pass global information from one method/view to another (with **kwargs?) then have a form for setting UTDT/location and use that.
