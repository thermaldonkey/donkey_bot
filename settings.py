HOST = 'irc.twitch.tv'
PORT = 6667
PASS = '' # OAuth key
IDENTITY = '' # Bot's nickname on Twitch
CHANNEL = '' # Channel bot should connect to
# See http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls on this:
DB_URL = 'dialect+driver://username:password@host:port/database'
POINTS_ALIAS = 'points' # Alias for channel points
# Response string for retrieving points count. Interpolations are required but everything else is
# fair game to change!
POINTS_COUNT = "{viewer} has {points} {point_alias}"
# Response string for adding points to a viewer. Interpolations are required but everything else
# is fair game to change!
ADDED_POINTS = "Gave {viewer} {points} more {point_alias}"
# Response string for removing points from a viewer. Interpolations are required but everything else
# is fair game to change!
REMOVED_POINTS = "Took {points} {point_alias} away from {viewer}"
