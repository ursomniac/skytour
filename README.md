# SkyTour
Plan observations using a database of DSOs.

#### Disclaimer
To be honest I've only written this for my use;  I'm not planning on advertising it or making it "battle ready" for widespread use.   That being said, I will try to help out with things, and interested in suggestions for improvement, bearing in mind this is "side" project.

There are definitely places where things should be less hard-coded.  I'll try to improve upon them as much as feasible.

## Tech
* Database: SQLite
* CMS: Django

### Packages
* Skyfield does most of the heavy lifting
* Matplotlib for the maps and plots

## Install
1. install `pipenv`.
2. Create a new project directory:
    1. In there, `pipenv --three`.  This creates your virtual environment.
3. Clone this repo.
    1. `pipenv sync` - this will install everything you need.
4. Download the JPL ephemeris files into the directory with manage.py.
    1. Follow the instructions at https://rhodesmill.org/skyfield/planets.html
    2. You'll want the  `de421.bsp` file for certain.
    3. You'll want excerpts for the planetary system for the moons:
        * I did a date range of 2011-01-01 to 2029-12-31 and the files range from 17MB for Jupiter to 98MB for Neptune.
    
## Configure
1. `python manage.py migrate` to build the database.
2. `python manage.py createsuperuser` to create an account for the CMS/Admin
3. `python manage.py runserver` to spin things up on port 8000.

At this point you should be able to get to the site at: `http://localhost:8000/`.
The CMS is at `http://localhost:8000/admin` and you can log in with the account you've just created.

## Customize

### Locations

The ObservingLocation database probably has all of my locations, which aren't likely to interest you.  You can delete them easily from the Admin by:

* Check the box in the upper-left-hand corner of the list (next to the PK column)
* Select "Delete selected observing locations" from the dropdown, then "Go".

You can now add your favorite location(s) to the database.   It's set up so that you can add in locations you MIGHT want, but haven't checked out.  See the README under `apps/location` for more details.

For the image fields, I take screen grabs from the Light Pollution Map (`http://lightpollutionmap.info`), Google Earth, and Google Maps.  That's also where all of the sky brightness metadata comes from in the ObservingLocation model.

### Planets and Moons

I've selected the subset of moons for each planet that I might hope to see with my Celestron SE 8.  You can edit those lists from the Planets section of the CMS (removing or adding by name in the comma-separated list).   The JPL files you downloaded have all of them.



