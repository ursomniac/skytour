# TODO list for Version 2

## Overall Logic for cookie

### Default SiteParameters

1. Default Observing MODE value (NBSMI) 
    a. Mode implies default equipment values
        * Can we get away with MODE defining limits ALONE?
            - OR make SiteParameter overrides for this!   <--- I like this

2. Default Observing Location 
    a. Sets up Declination Limits
    b. Set Time Zone in this model!   (eliminates having it on the cookie!)

* Will auto-populate on the Cookie setting form

## Gear Model

1. Let's auto-populate for imagers

2. Populating for telescope is a little hazier

# Steps to Install, etc.

## Things we need to do

0. Get overall choice-based metadata (i.e., what mode will you be using?)
    a. Modes N and B have extremely limited uses - no imaging
    b. Modes S and M have no need for imaging-based things 
    c. Mode I has some need for imaging-based things
    d. _REMEMBER_ that a user CAN switch modes on-demand (or use two at the same time)

1. Set up virtual env
2. Install packages (use the pipenv for that)
3. Create `app_data` files:
    a. CometEls.txt
    b. bright_asteroids.txt (get MPC file, then set up initial filters).
    c. Hipparcos and Stellarium files get generated on first access (skyfield load.Loader()) - so force this now
    d. NASA files for planets/moons: - need date range for this
        i. DE442s (or following)
        ii. *_excerpt.bsp files
4. Seed DSOs
    a. Run LEDA/SIMBAD API access
        i. Get override default from somewhere
    b. Generate finder views
        i. CAN we fix the FN problem so that they have predictable names?   That way we can create a ZIP archive.
        ii. IS THERE A WAY to genereate maps from Stellarium with an API?  (Create Finder views)
        iii. Can we generate default Object Images from a DSS API?
    c. Create Atlas Plates
        i. OR if you can DL/access a GZIP file of them...
5. Generate default/starting values:
    a. Default Location 
    b. Default SiteParameter values



