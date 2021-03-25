Site for people to rate your images
----------

[![Build Status](https://drone.niduroki.net/api/badges/niduroki/rate-shoot/status.svg)](https://drone.niduroki.net/niduroki/rate-shoot)

Intention is for you to upload thumbnails of a photoshoot, so a model can look over the thumbnails, tells you which ones to keep, and you can work accordingly.

-----------

## Docker

Expose port 8000.
Volume `/rate-shoot/data` for database and thumbnails.

### Update notes

Dropped root-privileges on this image on 2021-03-21, you need to to a `chown -R 1000 volume-dir` on your volume directory for the data, sometime before or after the next update.
