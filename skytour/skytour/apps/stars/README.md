# SkyMap App

![skymap_example](https://user-images.githubusercontent.com/485748/147896893-eb9bf2b3-43d7-485a-81be-a50dd603e5d9.png)

This will show the sky at a given date/time/location.

## What's Shown

South is down, North is up.

1. Stars - Uses the Bright Star Catalog with constellation lines (same as Stellarium) and designations for the brightest stars.
2. Planets - shown by their symbol
3. Moon and Sun - shown by their symbol
4. Asteroids - shown with a red circle and the ID number superposed
5. Comets - shown as a yellow hexagon with a letter - the identification of a comet is shown on the list on the right-hand side
6. Prominent DSOs this is from a custom list (right now it's not possible to customize this).  DSO types are (roughly):
    * Circles = galaxies, globular clusters, and planetary nebulae
    * Squares = nebulae
    * Stars = open star clusters
    * Crosses = barred spiral galaxies
7. Milky Way contours
8. Equators: equatorial (large-dash), ecliptic (dot-dash), galactic (thin-dash) lines
9. Celestial Points: North/South Poles (equatorial, ecliptic, galactic), and 0°/180° longitude points
10. Meteor Showers (large/small orange crosses depending on the average intensity of the shower)
11. Altitude Rings:
    * 20° altitude
    * 40° altitude
    * (default) 70° altitude or whatever the "slew-limit" SiteParameterFloat is set to.

## Optional Parameters

* Now - use the current time instead of the cookie's time
* Offset - you can use this to adjust the time up to ±5 hours from the time of the cookie (or current time if Now is used)
* Location Mask - display the mask for the given Observing Location - helpful if your observing location has obstructed views
    * To set this you need to add ObservingLocationMask entries to your location
* Simple - removes much of the "cruft", added constellation abbreviations - useful for printing
* Min DSO Alt. - this alters which DSOs are listed to the right.
