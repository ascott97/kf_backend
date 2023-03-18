# KF Backend Test

A small program that does the following:

1. Retrieves all outages from the `GET /outages` endpoint
2. Retrieves information from the `GET /site-info/{siteId}` endpoint for the site with the ID `norwich-pear-tree`
3. Filters out any outages that began before `2022-01-01T00:00:00.000Z` or don't have an ID that is in the list of
   devices in the site information
4. For the remaining outages, it should attach the display name of the device in the site information to each appropriate outage
5. Sends this list of outages to `POST /site-outages/{siteId}` for the site with the ID `norwich-pear-tree`

## Prerequisites
* To run the program you will need python3.8 installed & in your path.

## Running
* Install the dependencies(python-dateutil & requests): `pip install -r requirements.txt`
* Export an API Key as the environment variable `KF_API_KEY` e.g `export KF_API_KEY="<API KEY>"`
* Run the program from a terminal `python kf_backend.py`

## Unit tests
Unit tests for this program can be ran like so:
* Running `python -m unittest discover` from the root of the repo.

## This Solution

This solution involves having a class that can be instantiated with the base url of the service and the api key to use for all requests.
Then we have a reusable `handler` function that takes two arguments, a site and a date, so we can filter the outages before we send them to the /site-outages endpoint.  
Finally we have 3 functions for getting/sending data to/from the api:  
1. `_get_outages`
2. `_get_site_info`
3. `_post_site_outages`

And one last function:  `_filter_outages` that contains the logic for filtering the outages and attaching the device names.

All the https requests are handled by [requests.Session](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects) which sets the `x-api-key` header
for all http requests, and handles retries for all http requests if we receive a 429 or 500 status code so exponential backoff doesn't have to be implemented from scratch.
