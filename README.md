# SkyTour
Plan observations using a database of DSOs using Django.

This makes HEAVY use of the [SkyField](https://github.com/skyfielders/python-skyfield) package (saving a lot of time)!

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
4.  `pipenv shell` to enter a shell in your environment.
5. Download the JPL ephemeris files into the directory with manage.py.
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

### Site Parameters

There's a library of models under "Site Parameters".  Here you can set site-wide defaults:

Each parameter is of a different type: float, positive integers, "regular" integers, images, strings, and links.  These are used elsewhere in the code, if the corresponding value is in the DB, then it will be used; otherwise there'll be a default (hardcoded) in the code.

The default values given below are hard-coded into the system;  if you create the corresponding record
under SiteParameters, then it will override those defaults.

NOTE: You *have* to use the slugs shown below, otherwise the code won't know where to find the values!

#### Float

|          Name            |            Slug              | Default | Notes | 
| ------------------------ | :--------------------------- | ------: | ----: |
| Adj. Planets Separation  | adjacent-planets-separation  |    10.0 |     1 |
| Asteroid Cutoff          | asteroid-cutoff              |    10.0 |     2 |
| Asteroid Mag. Limit      | asteroid-magnitude-limit     |    10.0 |     3 |
| Declination Limit        | declination-limit            |   -25.0 |     4 | 
| DSO Mag. Limit           | dso-magnitude-limit          |    12.0 |     5 |
| Eyepiece FOV             | eyepiece-fov                 |    60.0 |     6 |
| Hour Angle Range         | hour-angle-range             |     3.5 |     7 | 
| Obs. Session Length      | observing-session-length     |     3.0 |     8 | 
| Skymap Mag. Limit: DSOs  | skymap-magnitude-limit-dsos  |     9.2 |     9 | 
| Skymap Mag. Limit: Stars | skymap-magnitude-limit-stars |     5.5 |    10 |


##### Notes

1. How close together do planets get in the sky to be "interesting" (in degrees).  
    * Note that they will both show up on finder charts for either planet.
2. Only query asteroids that COULD get as bright as this (speeds up lookups).
3. The faintest asteroid when polling for "visible" asteroids: 
    * i.e., if too far away, it's too faint, and don't include.  
    * This updates any dropdown for asteroids (i.e., only those that are currently brighter will show up), 
    * also it controls what is shown on the Skymap.
4. The most-southern declination includes in observing plans
    * TODO: somehow make this work for observers south of the equator (so that it's a northern limit).
5. Faintest DSOs shown on list of DSOs - can reset in the session cookie
6. The size of the FOV centered on finder charts (in arcmin): 
    * Default is 1°
    * You probably want to set this to the largest FOV eyepiece you have.
7. How far E/W an observing plan will list objects
    * Western extent at the beginning of the session; 
    * Eastern extent at the end of the session.
8. Used to create DSO lists for an observing plan
9. On the Skymap, how faint to show DSOs
    * Note: Only DSOs with a priority = 'highest' will be shown here.  
    * You can change priorities to highlight your favorite DSOs.
10. Faintest stars to show on a SkyMap

#### Positive Integers

|        Name         |        Slug         | Default | Notes | 
| :------------------ | :------------------ |   :-:   | ----: |
| Default Location ID | default-location-id |    *    |     1 | 
| SkyMap DSO Priority | skymap-dso-priority |    1    |  2, 3 | 

##### Notes

1. This is the ID/PK of the record in the ObservingLocation table of your "base" location.
    * The default is the first ObservingLocation record in the table.
2. This sets how "deep" we plot DSOs on a skymap
3. The value 1 here means "highest priority" only;  using 2 would be "highest + high" and so on.

#### Signed Integers

None yet.

#### Strings

|        Name         |        Slug         |  Default  | Notes | 
| :------------------ | :------------------ |    :-:    | ----: |
| Poll Planets        | poll-planets        | 'visible' |     1 | 

##### Notes

1. When polling planets for an Observing Plan, include all of them or just the ones that will be above the horizon within the observing session window.

#### Images

None yet.

#### Links

None yet.   This might be where some of the resources in the Website model go instead.


