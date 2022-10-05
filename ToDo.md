# To Do

- send file as `text/html` from static struct, return 404, if not in struct (as ../../../etc/passwd, e.g. sanitize input)
- single place for '/opds/authors/', '/opds/sequence/', '/opds/genres/' links place (code refinement)
- multiple pass over `.list` for lower peak memory consumption (no OOM on Orange PI)

# FIX

- use genres replacement when generating indexes
- pagination in genre book lists
- random and search in prod, header in search-books
