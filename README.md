# The TVDB v4 TV Shows Scraper for Kodi — Folder Name as Title

This branch is a modified version of the official [The TVDB v4 TV Shows Scraper for Kodi](https://github.com/thetvdb/metadata.tvshows.thetvdb.com.v4.python).

It includes two fixes:

1. **TVDB ID-based series search** — fixes series containing a `{tvdb-######}` identifier in their folder name, allowing Kodi to correctly resolve the series through its TheTVDB ID.
2. **Folder name as title** — uses the series folder name as the title displayed and stored by Kodi, while continuing to retrieve all other metadata from TheTVDB.

## Fixes included

### 1. TVDB ID-based series search

Kodi can identify a series folder using a TheTVDB ID in the form:

```text
{tvdb-72843}
```

The original scraper may fail to resolve such folders correctly during the series search.

This branch includes a fix that detects the `{tvdb-######}` identifier and uses it to resolve the corresponding TheTVDB series directly, avoiding an unreliable title-based search.

This is especially useful when the folder name contains a custom title or a title that does not match TheTVDB's localized metadata.

### 2. Folder name as title

This version uses the **series folder name as the title displayed and stored by Kodi**, while continuing to retrieve all other metadata from TheTVDB.

This is particularly useful for anime libraries where the folder name contains a preferred **romaji title**, while TheTVDB may provide a localized title that is unsuitable for the Kodi library.

For example:

```text
Folder:
Gokudou-Kun Manyuuki

TheTVDB Spanish title:
Jester el aventurero

Kodi title:
Gokudou-Kun Manyuuki
```

The scraper still uses TheTVDB for the rest of the series information, including:

* Plot and plot outline
* Genres
* Year and premiere date
* Studio
* Country
* Status
* TheTVDB, IMDb and TMDB IDs
* Artwork
* Season artwork
* Episode information

The selected TheTVDB language is therefore still used for the metadata; **only the series title is replaced by the folder name**.

## How the folder-name fix works

During the `find` operation, the scraper receives the series title from Kodi. This title corresponds to the name of the series folder.

The branch passes that title together with the TheTVDB series ID to the `getdetails` operation. When the series details are returned, the folder name is used for:

```python
'title'
'tvshowtitle'
```

All other information continues to come from TheTVDB.

The TheTVDB ID remains available internally, so subsequent season and episode requests continue to work normally.

## Example

A series stored as:

```text
Gokudou-Kun Manyuuki/
```

can be scraped with:

* **Kodi title:** `Gokudou-Kun Manyuuki`
* **Description:** Spanish TheTVDB description
* **Artwork:** TheTVDB artwork
* **Episodes:** TheTVDB episode metadata

This avoids unwanted localized titles such as:

```text
Jester el aventurero
```

while retaining the metadata supplied by TheTVDB.

## Branch

```text
folder-name-as-title
```

Current implementation commit:

```text
ba07bf7 — Use folder name as TV show title
```

## Based on

Official The TVDB Kodi scraper:

https://github.com/thetvdb/metadata.tvshows.thetvdb.com.v4.python

## Disclaimer

This is an unofficial fork and is not affiliated with or endorsed by TheTVDB or Kodi.
