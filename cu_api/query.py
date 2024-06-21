# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/query.ipynb.

# %% auto 0
__all__ = ['Query']

# %% ../nbs/query.ipynb 3
from . import config
from .core import get_cf_options

def _check_key(key):
    """
    Function to ensure that 'keys' are custom field id as an interager
    """
    CF_ID_LOOKUP = getattr(config,'CF_ID_LOOKUP')
    CUSTOM_FIELDS_DICT = getattr(config,'CUSTOM_FIELDS_DICT')
    
    if isinstance(key,str) and key in CF_ID_LOOKUP.keys():
        return CF_ID_LOOKUP.get(key)
    elif isinstance(key,int) and key in CUSTOM_FIELDS_DICT.keys():
        return key
    elif isinstance(key,str):
        try:
            int_key = int(key)
            if int_key in CUSTOM_FIELDS_DICT.keys():
                return int_key
        except ValueError:
            pass
    
    raise ValueError(f"Provided key '{key}' is not a valid custom field name(str) or custom field id(int)")

# %% ../nbs/query.ipynb 4
def _check_value(key:int, value):
    """
    Function to convert provided custom field values to their corresponding IDs.

    This function ensures that the provided 'values' are the IDs for the given custom field key 'key'.

    Parameters:
    key (int): The custom field id as an integer.
    value (str, int, or list): The value(s) to be checked and converted to their corresponding id(s). This can be a single string, integer, or a list of strings and/or integers.

    Returns:
    list: A list of unique custom field option IDs.
    """
    if isinstance(value, str): value = [value]
    if isinstance(value, int): value = [value]

    def find_key_by_value(dictionary, search_value):

        for key, value in dictionary.items():
            if value == search_value:
                return key

    cf_options = get_cf_options(key)
    Updated_List = []

    for item in value:
        if isinstance(item,str) and item in cf_options.values():
            id_value = find_key_by_value(cf_options, item)
            Updated_List.append(id_value)
        elif isinstance(item,int) and item in cf_options.keys():
            Updated_List.append(item)
        elif isinstance(item,str):
            try:
                int_key = int(item)
                if int_key in cf_options.keys():
                    Updated_List.append(int_key)
            except ValueError:
                continue
    
    return list(set(Updated_List))

# %% ../nbs/query.ipynb 5
class Query:
    """
    A class to represent and process search parameters for Copper API.

    This class allows input of both native Copper field names or custom field IDs for search parameters.
    It processes these inputs to prepare them for querying the Copper API.
    
    Examples
    --------
    Setting search parameters:
    >>> query = Query()
    >>> query['field_name'] = 'value_name'
    >>> query['custom_field_id'] = 'value_name'
    >>> query['field_name'] = ['value1', 'value2']

    Retrieving processed search parameters:
    >>> query.keys()
    >>> query.items()
    >>> query.values()
    >>> query.get_output('field_name')
    
    Attributes
    ----------
    _data : dict
        Stores the raw input data provided by the user.
    _processed_data : dict
        Stores the processed data ready for querying the Copper API.
    _native_fields : list
        Keeps track of the Copper's native fields.

    Methods
    -------
    get_input(key, default=None)
        Returns the original input value for the given key.
    get_output(key, default=None)
        Returns the processed value for the given key.
    
    inputs()
        Returns all items in the _data dictionary.
    input_keys()
        Returns all keys in the _data dictionary.
    input_values()
        Returns all values in the _data dictionary.
    
    items()
        Returns all items in the _processed_data dictionary.
    keys()
        Returns all keys in the _processed_data dictionary.
    values()
        Returns all values in the _processed_data dictionary.
    
    __repr__()
        Returns a formatted string representation of the Query object.
    __delitem__(key)
        Deletes the item from both _data and _processed_data dictionaries.
    __contains__(key)
        Checks if a key exists in the _data or _processed_data dictionaries.
    __setitem__(key, value)
        Sets the item in the _data dictionary and processes it.
    __getitem__(key)
        Retrieves the item from the _data or _processed_data dictionaries.
    """
    def __init__(self):
        self._data = {}
        self._processed_data = {}
        self._native_fields = []
        self._custom_fields = []

    def _process_input(self, key, value):
        """Default processing function that stores the length of the value."""

        if isinstance(key,list) or key not in ['id','name','address','assignee_id','contact_type_id',
                  'phone_number','city','state','postal_code','email_domains']:
            key = check_key(key) 
            value = check_value(key,value)
        else:
            self._native_fields.append(key)

        self._processed_data[key] = value
    
    def __setitem__(self, key, value):
        if key == 'Custom Fields' or key == 'Custom_Fields':
            self._custom_fields = value
        else:
            self._data[key] = value
            self._process_input(key, value)

    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]
        elif key in self._processed_data:
            return self._processed_data[key]
        else:
            raise KeyError(f"Key '{key}' not found  in provided Query.")

    def get_input(self, key, default=None):
        """Get the original value."""
        return self._data.get(key, default)

    def get_output(self, key, default=None):
        """Get the processed value."""
        return self._processed_data.get(key, default)

    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
        if key in self._processed_data:
            del self._processed_data[key]

    def __contains__(self, key):
        return key in self._data or key in self._processed_data

    def inputs(self):
        return self._data.items()

    def input_keys(self):
        return self._data.keys()

    def input_values(self):
        return self._data.values()

    def items(self):
        return self._processed_data.items()

    def keys(self):
        return list(self._processed_data.keys())

    def values(self):
        return self._processed_data.values()

    def __repr__(self):
        return f"Search Object: \nInputs:  {self._data}, \nProcessed Data:  {self._processed_data} \nNative Fields used:{self._native_fields})"


# %% ../nbs/query.ipynb 6
def _process_query(Query):
    """
    Function to take in a Query object and outputs items needed to search Copper.

    Input
    -----
    
    Query (object) containing the desired search parameters and information on desired outputs

    Outputs
    ------
    
    Native_Params - list[dict] for search parameters related to fields native to copper records types.

        Example: [{'state':'CA'}]

    CF_Params - list[dict] or search parameters related to custom fields on copper records. These have a special format dictated by Copper.

        Example: {"custom_field_definition_id": 588393, "value":[1806073]}

    Output_CFs - list of desired custom fields for the output dataframe
    """
    Native_Params = []
    CF_Params = []
    list_non_native = Query.keys()

    if Query._native_fields: 
        for item in Query._native_fields:
            Native_Params.append(Query.get_output(item))
            list_non_native.remove(item)
    
    if list_non_native:
        for item in list_non_native:
            CF_Params.append({"custom_field_definition_id": item,"value":Query.get_output(item)})
        
    return Native_Params, CF_Params
