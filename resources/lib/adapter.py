import abc


class PointsAdapter:
    @abc.abstractmethod
    def get_points(self, imdb, season, episode, type=None):
        """Get points for a specific playing file."""
