# Observe app

This has the ObservingLocation model, and also views for Observing Plan.

I set this up because there are several locations we go to, and I'm always on the lookout
for potential locations.

This model contains all of those place.   You assign them a grade:
* TBD - I haven't checked it out yet
* Reject - doesn't meet necessary criteria
* Possible - first pass seems OK, need to scrutinize it more
* Active - we actually have used this site.

The criteria tend to be this:
1. Does the site have clear views, esp. in the E-S-W arc?
2. Does the site have easy and safe access?
3. What is the potential annoyance from nearby cars?
4. Is there enough room for a small group of people?

## Sky brightness

We get information from http://www.lightpollution.info (and their app).
Instead of using an API we enter values for:

* latitude and longitude
* SQM
* Brightness, Artif. Brightness and Ratio
* Bortle scale estimate
* Elevation
* Distance (per Google Maps)
* Travel time (ditto)

## Listing Page plots

On the ObservingLocation listing page (/observing_location) two plots are generated
with SQM vs. Distance, and Bright vs. Travel Time.

They're color coded by status and with different symbols for the state (since I live near 4 states, it's helpful; it would not be hard to change it to some other parameter.)

The table on the OLL page is sortable on each column.

