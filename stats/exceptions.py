class StravaExternalException(Exception):
    def __init__(self, msg='There was an error with the Strava API',
                 *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
