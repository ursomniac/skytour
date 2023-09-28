# DSOs

There is a DSO model where you can store your own list of DSOs.

I've seeded this with ~900 DSOs down to roughly -30° declination.
* Messier
* Caldwell
* Herschel 400
* anything else that popped up in Stellarium with V < 12.

It has all of the expected fields:
* RA / Dec
* Mag
* Object Type (TODO: make a better list?)
* Angular Size
* Surface Brightness / Contrast Index (from Stellarium)

## Adding a new DSO

1. Add the metadata in the Admin
2. Add the eQuinox image from Stellarium
3. Get the wide/narrow field from running `python manage.py create_wide_narrow_charts --dso_list <list>`
4. Add/set the imaging priority with `python manage.py add_to_imaging_checklist -p 2 <id>`
5. Create an updated Atlas Plate from running `python manage.py create_atlas_plate -f <list>` - recommend getting the atlas plate list by using a nearby DSO.
6. Get the DSS view and upload it (optional)
7. Optional: create the older DSO finder chart with `python manage.py create_dso_finder_charts --dso_list <list>`
8. Optional: create the DSO PDF file with `python manage.py create_dso_pdf --dso_list <list>`

You can create several records and then run the management commands with a list where indicated.

## Images

There's a model for uploading images (from HST, etc.).

There are also other fields for images:

1. Finder chart - this was one where I put maps that I uploaded from the Internet, but they came from different sources, and largely weren't available.
2. DSO Finder chart - these are generated within this software, so they exist for all DSOs AND are uniform. - DECPRECATED
3. Field View - these comes from http://astronomy.tools --- you can customize it for your eyepieces and telescope, and it'll overlay them on scaled images from the PSS (so the view isn't likely to be close to the real world, but it DOES give you a good idea of scale).
4. Custom finder charts:  
    * A wide-field view showing other nearby DSOs
    * A narrow-field view showing both the largest eyepiece and the image FOV for the eQuinox 2 telescope.
5. Image from Stellarium with the overlay of the eQuinox 2 telescope.

## Priorities

Completely subjective.

## DSO Lists

You can create observing list for any part of the sky.  