"""Module for interacting with YouTube search."""
# Native python imports
import logging

# Local imports
from pytube.innertube import InnerTube


logger = logging.getLogger(__name__)


class Search_channel:
    def __init__(self, query):
        """Initialize Search object.

        :param str query:
            Search query provided by the user.
        """
        self.query = query
        self._innertube_client = InnerTube(client='WEB')

        # The first search, without a continuation, is structured differently
        #  and contains completion suggestions, so we must store this separately
        self._initial_results = None

        self._results = None
        self._completion_suggestions = None

        # Used for keeping track of query continuations so that new results
        #  are always returned when get_next_results() is called
        self._current_continuation = None

    @property
    def completion_suggestions(self):
        """Return query autocompletion suggestions for the query.

        :rtype: list
        :returns:
            A list of autocomplete suggestions provided by YouTube for the query.
        """
        if self._completion_suggestions:
            return self._completion_suggestions
        if self.results:
            self._completion_suggestions = self._initial_results['refinements']
        return self._completion_suggestions

    @property
    def results(self):
        """Return search results.

        On first call, will generate and return the first set of results.
        Additional results can be generated using ``.get_next_results()``.

        :rtype: list
        :returns:
            A list of YouTube objects.
        """
        if self._results:
            return self._results

        videos, continuation = self.fetch_and_parse()
        self._results = videos
        self._current_continuation = continuation
        return self._results

    def get_next_results(self):
        """Use the stored continuation string to fetch the next set of results.

        This method does not return the results, but instead updates the results property.
        """
        if self._current_continuation:
            videos, continuation = self.fetch_and_parse(self._current_continuation)
            self._results.extend(videos)
            self._current_continuation = continuation
        else:
            raise IndexError

    def fetch_and_parse(self, continuation=None):
        """Fetch from the innertube API and parse the results.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: tuple
        :returns:
            A tuple of a list of YouTube objects and a continuation string.
        """
        # Begin by executing the query and identifying the relevant sections
        #  of the results
        raw_results = self.fetch_query(continuation)

        # Initial result is handled by try block, continuations by except block
        try:
            sections = raw_results['contents']['twoColumnSearchResultsRenderer'][
                'primaryContents']['sectionListRenderer']['contents']
        except KeyError:
            sections = raw_results['onResponseReceivedCommands'][0][
                'appendContinuationItemsAction']['continuationItems']
        item_renderer = None
        continuation_renderer = None
        for s in sections:
            if 'itemSectionRenderer' in s:
                item_renderer = s['itemSectionRenderer']
            if 'continuationItemRenderer' in s:
                continuation_renderer = s['continuationItemRenderer']

        # If the continuationItemRenderer doesn't exist, assume no further results
        if continuation_renderer:
            next_continuation = continuation_renderer['continuationEndpoint'][
                'continuationCommand']['token']
        else:
            next_continuation = None

        # If the itemSectionRenderer doesn't exist, assume no results.
        if item_renderer:
            channels = []
            raw_video_list = item_renderer['contents']
            for video_details in raw_video_list:
                # Skip over ads
                if video_details.get('searchPyvRenderer', {}).get('ads', None):
                    continue

                # Skip "recommended" type videos e.g. "people also watched" and "popular X"
                #  that break up the search results
                if 'shelfRenderer' in video_details:
                    continue

                # Skip auto-generated "mix" playlist results
                if 'radioRenderer' in video_details:
                    continue

                # Skip playlist results
                if 'playlistRenderer' in video_details:
                    continue
                """
                # Skip channel results
                if 'channelRenderer' in video_details:
                    continue
                """

                # Skip 'people also searched for' results
                if 'horizontalCardListRenderer' in video_details:
                    continue

                # Can't seem to reproduce, probably related to typo fix suggestions
                if 'didYouMeanRenderer' in video_details:
                    continue

                # Seems to be the renderer used for the image shown on a no results page
                if 'backgroundPromoRenderer' in video_details:
                    continue

                if 'videoRenderer' not in video_details:
                    pass
                    #logger.warn('Unexpected renderer encountered.')
                    #logger.warn(f'Renderer name: {video_details.keys()}')
                    #logger.warn(f'Search term: {self.query}')
                    #logger.warn(
                        #'Please open an issue at '
                        #'https://github.com/pytube/pytube/issues '
                        #'and provide this log output.'
                    #)
                    #continue
                
                #skip videos
                if 'videoRenderer' in video_details:
                    continue

                if 'channelRenderer' not in video_details:
                    print("error! at pytube.chsearch(custom)")
                    continue

                # Extract relevant video information from the details.
                # Some of this can be used to pre-populate attributes of the
                #  YouTube object.
                chid = video_details['channelRenderer']["channelId"]
                channels.append(chid)
        else:
            channels = None

        return channels, next_continuation

    def fetch_query(self, continuation=None):
        """Fetch raw results from the innertube API.

        :param str continuation:
            Continuation string for fetching results.
        :rtype: dict
        :returns:
            The raw json object returned by the innertube API.
        """
        query_results = self._innertube_client.search(self.query, continuation)
        if not self._initial_results:
            self._initial_results = query_results
        return query_results  # noqa:R504