# CU API

I use [Copper's](https://copper.com/) API a lot for work, so a module of functions to work with in in Python. This is my attempt to turn these functions into a package that can be used by others.


## Installation

If you are already in a Notebook, you can still the package to your environment with python:

``` python
!pip install cu_api
```
This package is designed to be a user friendly wrapper for the Copper
CRM API to make interacting witth and pulling data easier.

Or install the package to your environment in the command line:
## Install

You can install the `cu_api` package through PyPI:

``` {.bash .shell}
pip install cu_api
```

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
## How to use

Start by importing all the modules you’ll need for your project. The
`cuapi_wrapper` package is broken down into seperate modules for working
with companies, tasks, opportunities, users, etc.

For example, if we wanted to look at **companies** in copper, we should
start by importing the **copper_crm.companies** module. We can then
search these companies for those who are in California:

``` python

from cu_api import search

df = search.companies(Advertisers)
```


import cu_api.companies as companies

companies.set_headers(os.environ['MY_COPPER_KEY'],'myemail@email.com')

SunnyStates = companies.Query
SunnyStates['state'] = ['CA','FL','AZ','TX']
SunnyStates['Amenities'] = ['Pool','Beach','Hot tub']
SunnyStates.outputs = ['Account Manager','Lifetime Spend']

companies.search(SunnyStates)
```
