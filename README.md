# TheTVDB v4 Kodi Scraper – TVDB ID Fix

This repository is a fork of the Kodi **TheTVDB v4 TV Show Scraper** with a targeted fix for resolving TV shows by their TheTVDB ID when the ID is included in the folder name.

## The problem

Kodi normally searches for a TV show by its title. This can produce incorrect matches when different series have similar or ambiguous names.

For example:

```text
Galaxy Angel (79289)
```

A normal title search for `Galaxy Angel` can return a different series, such as **Galaxy Angel A**, instead of the series identified by TVDB ID `79289`.

## The fix

The scraper now detects a numeric value at the end of the title in parentheses:

```text
Series Name (TVDB_ID)
```

If the number is outside the normal release-year range (`1900–2100`), it is treated as a TheTVDB series ID.

The scraper then:

1. Resolves the ID through TheTVDB.
2. Retrieves the exact series name and year.
3. Performs a normal TheTVDB search using that exact information.
4. Keeps only the search result with the requested TVDB ID.
5. Returns that result to Kodi.

This preserves the normal scraper workflow while ensuring that an explicitly supplied TVDB ID identifies the intended series.

If the ID cannot be resolved or no matching search result is found, the scraper falls back to the normal title-based search.

## Examples

### TVDB ID

```text
Galaxy Angel (79289)
```

The scraper uses `79289` as the TVDB ID and resolves the correct **Galaxy Angel** series instead of relying on an ambiguous title search.

### Release year

```text
Urusei Yatsura (1981)
```

`1981` is treated as a release year, not as a TVDB ID, and the normal title/year search is used.

## Scope

This is a small, targeted modification to the series search logic. The rest of the scraper behaviour is unchanged.

The fix has been tested against the Kodi TheTVDB v4 scraper based on version `1.1.13-a`, including series with ambiguous titles and folders containing explicit TVDB IDs.

## Branch

```text
fix-tvdb-id-in-title
```

## Disclaimer

This is an unofficial fork and is not affiliated with or endorsed by TheTVDB or Kodi.
