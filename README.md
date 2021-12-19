Site for people to rate your images
----------

[![Build Status](https://drone.niduroki.net/api/badges/niduroki/rate-shoot/status.svg)](https://drone.niduroki.net/niduroki/rate-shoot)

Intention is for you to upload thumbnails of a photoshoot, so a model can look over the thumbnails, tells you which ones to keep, and you can work accordingly.

-----------

## Docker

Expose port 8000.
Volume `/app/data` for database and thumbnails.

### Update notes

There is a database migration to be executed, as of 2021-06-24, to do so call alembic upgrade head, in the base directory (maybe through your docker container).  
E.g. `docker exec -itu uwsgi rate-shoot alembic upgrade head`

Dropped root-privileges on this image on 2021-03-21, you need to to a `chown -R 1000 volume-dir` on your volume directory for the data, sometime before or after the next update.

Renamed volume `/rate-shoot/data` into `/app/data` on 2021-12-19 for more similar docker images.
