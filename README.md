# CU API

There is a [Copper's](https://copper.com/) API a lot for work, so a module of functions to work with in in Python. This is my attempt to turn these functions into a package that can be used by others.

------------------------------------------------------------------------

## Installation

If you are already in a Notebook, you can still the package to your environment with python:

``` python
!pip install cu_api
```

Or install the package to your environment in the command line:

``` {.bash .shell}
pip install cu_api
```

------------------------------------------------------------------------

## Queries and Searching

To get most information from the Copper API, you need to search for it. You can define what companies, people, opportunities, etc. you are interested in by specifying various filters. These can be values in Custom Fields that you defined, or standard fields on each record type.

This package makes this easier uses a `Query` object to hold the various filters you would like to use.

Since, I work in Advertising. Let's assume that I would like to pull the information for all Advertisers in the CRM. We can first create a new query:

``` python
from cu_api import Query

Advertisers = Query()
```

Then we can add a filter to search for companies that have the "Live" value in the "Campaign Status" field:

``` python
Advertisers['Campaign Satus'] = 'Live'

## Or, if you know the id of the custom field:

Advertisers[2938821] = 'Live'
```

We can also add other filters to check only get Advertisers in California and from a specific sales person:

``` python
Advertisers['state'] = 'CA'
Advertisers['owner'] = 'Jim Halpert'
```

Your `Advertisers` query can then used with the `search` function to get data from Copper.

``` python

from cu_api import search

df = search.companies(Advertisers)
```

