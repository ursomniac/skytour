# DSOs

There is a DSO model where you can store your own list of DSOs.

I've seeded this with several thousand DSOs down to 13th magnitude (and lower)

## DSOInField

Objects close to a DSO (generally within 30') are in a separate parallel table
called DSOInField.   They have the same metadata as DSOs.  The idea is that 
in practice, you'll "observe" a field with either a primary DSO or multiple DSOs
in the field (e.g, M51).

The DSO search box in the navbar will point to the DSO page if an in-field DSO is entered.

## Sources/Catalogs

### Complete Catalogs
* Messier
* Caldwell
* Herschel 400
* Sharpless
* Hickson Compact Groups

### Mostly Complete Catalogs
* Abell (PNs)
* Arp Peculiar Galaxies
* Barnard (dark nebulae)
* Collinder, Melotte, Trumpler (open clusters)

### Sporadically-Complete Catalogs
* NGC and IC
* PK (PNs)
* UGC and PGC

### Other
This is for objects whose primary ID isn't in the Catalog list.

There also a Bayer/Flamsteed "catalog" for objects whose primary ID is in them
(e.g., Omega Centauri, h Persei).

## DSO Metadata Fields

It has all of the expected fields:
* RA / Dec (J2000)
* Mag (usually V, sometimes B)
* Object Type and Subclass/Morphology
* Angular Size
* Surface Brightness / Contrast Index (from Stellarium)

Canonical values are taken from SIMBAD, or HyperLeda (for galaxies).
These are stored in metadata dicts and override the fields in the Admin
on the DSODetailPage.

The "other_parameters" field allows you to add additional metadata to an object (e.g., cluster ages).
The format is a series of key/value pairs separated by semi-colons, e.g.:

Age: 12.7 Gyr;
Origin: Halo

for a globular cluster.   The "notes" field is for more free-form content about a DSO.

## Adding a new DSO

V2.x will have a script to automate this as well as seeding from a "master" DSO list

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

### Generated Images/Finding Charts

There are also other fields for images:

1. Custom finder charts:  
    * A wide-field view showing other nearby DSOs
    * A narrow-field view showing both the largest eyepiece and the image FOV for:
        * Wide-field eyepiece
        * eQuinox 2 FOV
        * Seestar S50 and S30 FOV (non-rotated) both default and mosaic modes
2. DSO Finder chart - these are generated within this software, so they exist for all DSOs AND are uniform (this is the same as the wide-field chart but suitable for printing).
3. Image from Stellarium with the overlay of the eQuinox 2 telescope.
4. External Finder chart - these are uploaded images of someone else's finder charts (largely DEPRECATED)5. DEPRECEATED - Field View - these comes from http://astronomy.tools --- you can customize it for your eyepieces and telescope, and it'll overlay them on scaled images from the PSS (so the view isn't likely to be close to the real world, but it DOES give you a good idea of scale).

These images are shown in the "map" panel on the DSODetail page in a carousel:
* Narrow-field View
* Wide-field View
* Atlas Plates (in order of proximity to the center of the plate)
* External Finder Chart

### Uploaded Images of Objects from the Web

You can add images found on the WWW (up to 3) - they'll appear at the bottom of the page.
These are intended as references against what you're observing/imaging (i.e., "What do the 
spiral arms look like?  Can I see particular structures that are supposed to be there?").

### Library Images

These models (which also exist for the SSO models) are for images coming from your imaging telescope.
They can appear in carousels in two places on a DSODetail page:
1. in the top-right corner - the "display" panel - usually these are cropped to be somewhat square to best fit in the panel;
2. below on the right-hand side (against the finder charts) with the field images obtained from Stellarium

Objects with at least 1 library image have a "camera" icon in listings of DSOs.

## Observing Modes

Each DSO has a set of up to five modes:
* N = Naked-Eye
* B = Binoculars
* S = Small Telescope (aperture <= 6")
* M = Medium Telescope (aperture > 6")
* I = Imaging Telescope (eQuinox 2, Seestar S50, etc.)

corresponding to which are most-appropriate for an object (many have more than one).

Each has a priority (0 = very low to 4 = highest), and a viability (0 = unviable to 9 = extremely easy).
They're completely subjective but should give a decent indication of what's possible.

## The Atlas

The sky has been split into 258 "plates" going from +90° to -90° declination in several bands:
* ±90° (1 plate) = 2 total
* ±75° (12 plates, every  2.0h  in RA) = 24 total
* ±60° (16 plates, every  1.5h  in RA) = 32 total
* ±45° (20 plates, every  1.2h  in RA) = 40 total
* ±30° (24 plates, every  1.0h  in RA) = 48 total
* ±15° (32 plates, every  0.75h in RA) = 64 total
*   0° (48 plates, every  0.50h in RA) = 48 total

The plates cover about 20° in diameter with stars down to mag 9.5 (true?).

## DSO Lists

You can create observing list for any part of the sky.  

Lists flagged as "active" will show a "telescope" icon on DSOs in lists indicating
they're flagged for observation.  Objects can be on more than one list: the "telescope"
icon will appear if a DSO is on any active list.

