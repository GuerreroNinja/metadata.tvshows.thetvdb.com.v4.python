from pprint import pformat
import re

import xbmcgui
import xbmcplugin
import json

from . import tvdb
from .artwork import add_artworks
from .tvdb import get_language
from .utils import logger

SUPPORTED_REMOTE_IDS = {
    'IMDB': 'imdb',
    'TheMovieDB.com': 'tmdb',
}

ARTWORK_URL_PREFIX = 'https://artworks.thetvdb.com'


def search_series(title, settings, handle, year=None) -> None:
    logger.debug(f'Searching for TV show "{title}", year="{year}"')

    tvdb_client = tvdb.Client(settings)
    search_results = None

    # If the title ends with a numeric value in parentheses, treat it as a
    # TVDB ID unless it looks like a release year.
    id_match = re.search(r'\((\d+)\)\s*$', title)
    if id_match:
        candidate_id = int(id_match.group(1))

        # Normal release years are not TVDB IDs.
        if not 1900 <= candidate_id <= 2100:
            try:
                # First resolve the ID to get the exact series name and year.
                show = tvdb_client.get_series(candidate_id)

                if show:
                    show_name = show.get("name")
                    show_year = show.get("year")

                    logger.debug(
                        f'Found TVDB ID {candidate_id}: '
                        f'"{show_name}" ({show_year})'
                    )

                    # Search using the exact series name and year so that
                    # Kodi receives a normal TheTVDB search result.
                    if show_name:
                        search_results = tvdb_client.search(
                            show_name,
                            year=show_year,
                            type="series",
                            limit=10,
                        )

                        # Keep only the exact TVDB ID we requested.
                        search_results = [
                            result
                            for result in search_results
                            if str(result.get("tvdb_id")) == str(candidate_id)
                        ]

                        if search_results:
                            logger.debug(
                                f'Using TVDB search result for ID '
                                f'{candidate_id}'
                            )
                        else:
                            logger.debug(
                                f'No matching search result found for '
                                f'TVDB ID {candidate_id}. '
                                'Falling back to title search.'
                            )
                            search_results = None

            except Exception as exc:
                logger.debug(
                    f'TVDB ID {candidate_id} lookup failed: {exc}. '
                    'Falling back to title search.'
                )

    # Fall back to the normal title search if no TVDB ID was resolved.
    if search_results is None:
        if year is None:
            search_results = tvdb_client.search(
                title, type="series", limit=10
            )
        else:
            search_results = tvdb_client.search(
                title, year=year, type="series", limit=10
            )

            if not search_results:
                logger.debug(
                    f"No results found for '{title}' where year='{year}'. "
                    "Falling back to search without year criteria."
                )
                search_results = tvdb_client.search(
                    title, type="series", limit=10
                )

    logger.debug(f'Search results {search_results}')

    if not search_results:
        return

    language = get_language(settings)
    items = []

    for show in search_results:
        show_name = show["translations"].get(language, show["name"])
        show_year = show.get("year")

        if show_year:
            show_name += f" ({show_year})"

        liz = xbmcgui.ListItem(show_name, offscreen=True)
        logger.debug(f'FIND RESULT: title="{show_name}" tvdb_id="{show["tvdb_id"]}" year="{show.get("year")}"')
        url = f'{show["tvdb_id"]}|{title}'
        items.append((url, liz, True))

    xbmcplugin.addDirectoryItems(handle, items, len(items))


def get_series_details(id, settings, handle, title):
    # get the details of the found series
    logger.debug(f'Find info of tvshow with id {id}')
    tvdb_client = tvdb.Client(settings)
    show = tvdb_client.get_series_details_api(id, settings)
    if not show:
        xbmcplugin.setResolvedUrl(
            handle, False, xbmcgui.ListItem(offscreen=True))
        return

    showId = {'tvdb': str(show["id"])}
    for remoteId in show.get('remoteIds'):
        if remoteId.get('sourceName') == "IMDB":
            showId['imdb'] = remoteId.get('id')
        if remoteId.get('sourceName') == "TheMovieDB.com":
            showId['tmdb'] = remoteId.get('id')
    
    details = {'title': title,
                'tvshowtitle': title,
                'plot': show["overview"],
                'plotoutline': show["overview"],
                'episodeguide': json.dumps(showId),
                'mediatype': 'tvshow',
                }
    name = show["name"]
    year_str = show.get("firstAired") or ''
    if year_str:
        year = int(year_str.split("-")[0])
        logger.debug(f"series year_str: {year_str}")
        details["premiered"] = year_str
        details['year'] = year
        name = f'{name} ({year})'
    studio = get_studio(show)
    if studio:
        details["studio"] = studio
    genres = get_genres(show)
    details["genre"] = genres
    country = show.get("originalCountry", None)
    if country:
        details["country"] = country
    status = show.get('status')
    if status:
        details['status'] = status['name']
    liz = xbmcgui.ListItem(name, offscreen=True)
    logger.debug(f"series details: {pformat(details)}")
    liz.setInfo('video', details)
    liz = set_cast(liz, show)
    unique_ids = get_unique_ids(show)
    liz.setUniqueIDs(unique_ids, 'tvdb')
    language = tvdb.get_language(settings)
    max_season_images = int(settings.get("max_season_images"))
    add_artworks(show, liz, language, max_season_images)
    xbmcplugin.setResolvedUrl(
        handle=handle, 
        succeeded=True, 
        listitem=liz)


def set_cast(liz, show):
    cast = []
    characters = show.get('characters') or ()
    for char in characters:
        if char["peopleType"] == "Actor":
            data = {
                'name': char['personName'],
                'role': char['name'],
            }
            thumbnail = char.get('image') or char.get('personImgURL')
            if thumbnail:
                if not thumbnail.startswith(ARTWORK_URL_PREFIX):
                    thumbnail = ARTWORK_URL_PREFIX + thumbnail
                data['thumbnail'] = thumbnail
            cast.append(data)
    liz.setCast(cast)
    return liz


def get_genres(show):
    return [genre["name"] for genre in show.get("genres", ())]


def get_studio(show):
    companies = show.get("companies", ())
    if not companies:
        return None
    studio = None
    if len(companies) == 1:
        return companies[0]['name']
    for company in companies:
        if company["primaryCompanyType"] == 1:
            studio = company["name"]
    return studio


def get_tags(show):
    tags = []
    tag_options = show.get("tagOptions", ())
    if tag_options:
        for tag in tag_options:
            tags.append(tag["name"])
    return tags


def get_unique_ids(show):
    unique_ids = {'tvdb': show['id']}
    remote_ids = show.get('remoteIds')
    if remote_ids:
        for remote_id_info in remote_ids:
            source_name = remote_id_info.get('sourceName')
            if source_name in SUPPORTED_REMOTE_IDS:
                unique_ids[SUPPORTED_REMOTE_IDS[source_name]] = remote_id_info['id']
    return unique_ids
