# The Plan

# 1. Observing Session app

## 1.1. Create ObservingSession model

Metadata:
* Location
* Date/Time
* Log weather/conditions

It MIGHT be cool (the way to go):
* Select/create new ObservingSession
* update the Django session metadata
    * Run planet/moon/bright asteroid ephemeris for that date/time and cache
* Update with new date/time as needed.
    * This might get weird wrt the observing log (i.e., you don't want to have 5 sessions in one night)

So maybe the flow is:

1. Create new ObservingSession instance for a date and start time
2. Allow for the Django session to be changed UNDER the OS instance
    1. That way you can update for each target if you wanted to.
3. For an ObservingLog instance:
     1. Update the Django session information (aha - this is starting to make sense, I think)
     2. Log the time-relevant metadata
         1. RA/Dec/Alt/Az
         2. Sky conditions

## 1.2. ObservingLog changes

* Move out of DSO
* We'll need SOME kind of GFK to DSO/Planet/Moon/Asteroid/Comet, or maybe it's OK to have N FK fields.
    * OR just have "model" field and "slug" field...?

## 1.3. Django Session

1. TODO: Can you update a session during a session? - probably

### 1.3.1. Caching 

1. Can I run all the planets/asteroids/etc. and cache the results for a given UTDT/location?
2. If so, then the likely flow would be:
    1. Update ObservingSession record (or instantiate it)
    2. Run all the things
        1. Cache the object dicts
            1. TODO: Create a dict like this for DSO (if there isn't one already)
    3. Select thing to observe
        1. Optionally create ObservingLog record
            1. This is so that you can preview things for a date/time/location
            2. Or instantiate an ObservingLog record

