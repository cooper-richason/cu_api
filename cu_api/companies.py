# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/companies.ipynb.

# %% auto 0
__all__ = ['search', 'update']

# %% ../nbs/companies.ipynb 3
from . import core, config
from .query import Query as _Query
from .core import set_headers as _set_headers
from .search import _search_loop, get_owners
import pandas as pd
import pytz
from tqdm.autonotebook import tqdm

# %% ../nbs/companies.ipynb 5
class Query(_Query):pass
def create_query(*args, **kwargs): return _Query(*args, **kwargs)

# %% ../nbs/companies.ipynb 7
def _clean_row(company_data:list, #Returned company data as list of dictionaries,
                          cf_fields:list = [], # list of custom fields on companies you would like to include
):
    """Process to clean returned company data"""

    core.prc_get_cf_fields()
    custom_fields = getattr(config,'CUSTOM_FIELDS')
    custom_fields_dict = getattr(config,'CUSTOM_FIELDS_DICT')

    def clean_date(date):
        try:
            if date is None: return None  # Handle None values (empty rows)
            if isinstance(date, int) and len(str(date)) >= 6 and len(str(date)) <= 10:
                # If it's an integer with <= 10 digits, assume it's a Unix timestamp
                ct_timezone = pytz.timezone('US/Central')
                new_date = pd.to_datetime(date, unit='s',utc=True).tz_convert(ct_timezone)
                return new_date
            else: return date
        except Exception as e:
            return date

    native_items = ['id', 'name','assignee_id', 'contact_type_id']
    output_dict = {}

    for item in native_items: output_dict[item] = company_data.get(item, None)
    if company_data['address']: 
        for item in dict(company_data['address']).keys(): output_dict[item] = dict(company_data['address'])[item]

    custom_field_data = company_data['custom_fields']

    for dict_item in custom_field_data:
        item_id = dict_item['custom_field_definition_id']
        item_name = custom_fields_dict.get(item_id, None)
        data_type = custom_fields[item_id].get('data_type')

        if item_name not in cf_fields and item_id not in cf_fields or item_name is None:
            continue
        elif item_name is not None and ('options' in list(custom_fields[item_id].keys())):
            item_value = dict_item['value']
            value_name = core.cf_option_name(item_id,item_value)
            output_dict[item_name] = value_name
        elif data_type == 'Date':
            cleaned_date = clean_date(dict_item['value'])
            output_dict[item_name] = cleaned_date
        else:
            item_value = dict_item['value']
            output_dict[item_name] = item_value

    return output_dict

# %% ../nbs/companies.ipynb 8
def _clean_dataframe(df):
    list_assign_ids = list(df['assignee_id'].dropna().unique().astype(int))
    assignee_dict = get_owners(list_assign_ids)
    print(assignee_dict)

    df['Owned By'] = df['assignee_id'].apply(lambda value: assignee_dict.get(value))
    df.drop(columns=['assignee_id'])
    return df


# %% ../nbs/companies.ipynb 9
def set_headers(AccessToken:str, #Access Token (API Key) provided by Copper
                 UserEmail:str): #Email associated with your API key
    _set_headers(AccessToken,UserEmail)
    

# %% ../nbs/companies.ipynb 10
def search(search_query, # Instance of Query object
            clean_data:bool = True, # Whether to clean results or not
            drop:list = None, # Columns to drop from final dataframe
            **kwargs
            )->pd.DataFrame:
    """Search for Company records in Copper!
    
    This function allows you to systematically search Copper for companies 
    that match the parameters specified in your `Query` and returns the 
    returns the data as a pandas dataframe
    """
    
    combined_results, Outputs = _search_loop(search_query= search_query, url= 'https://api.copper.com/developer_api/v1/companies/search')
    
    # Custom Fields
    if 'cf_fields' in kwargs:     cf_fields = kwargs.get('cf_fields')
    else:                         cf_fields = Outputs

    # Processing Rows:
    cleaned_rows = []
    for result in tqdm(combined_results,'Cleaning Data',total=len(combined_results)):
        cleaned_rows.append(_clean_row(result, cf_fields))
    
    # To Clean, or not to Clean
    if not clean_data:
        print('Returning raw results')
        return cleaned_rows

    cleaned_rows_df = pd.DataFrame(cleaned_rows)
    cleaned_data_df = _clean_dataframe(cleaned_rows_df)

    if isinstance(drop,list):      return cleaned_data_df.drop(columns=drop,inplace=True)
    else:                               return cleaned_data_df 

# %% ../nbs/companies.ipynb 11
def search_old(search_params:dict={}, # search params for standard company fields
            cf_search:list=[],# search params for custom fields
            clean_data:bool = True, # Whether to clean results or not
            cf_fields:list = [], # list of custom fields on companies you would like to include
            drop_cols:list = None, # Columns to drop
            )->pd.DataFrame:
    """Searches copper companies and returns Pandas DataFrame"""
    
    total_pages = page = 1
    combined_results = []
    
    Sess = core.get_session()

    while page <= total_pages:
        page_params = {
            "page_size": 100,
            "page_number": page,
            }
        
        if search_params != {}: page_params.update(search_params)

        if cf_search != {}:
            cf_addition = {"custom_fields":cf_search}
            page_params.update(cf_addition) 

        result = Sess.post('https://api.copper.com/developer_api/v1/companies/search',json=page_params)
    
        if result.status_code == 200:
            total_pages = (int(result.headers['X-PW-TOTAL'])//100)+1
            
            # Creatig Progress Bar:
            if page == 1: progress_bar = tqdm(total=total_pages,desc='Searching Copper')
            progress_bar.update(1)  # Update the progress bar
            
            result_json = result.json()
            combined_results.extend(result_json)
            page +=1

        else:
            print(f"Issue with page {page}. Stopping.")
            break

    progress_bar.close()  # Close the progress bar when done

    if not clean_data:
        print('Returning raw results')
        return combined_results
 
   
    print('\nData Recieved. Cleaning results:')

    cleaned_data = [_clean_row(result, cf_fields) for result in combined_results]
    cleaned_data_df = pd.DataFrame(cleaned_data)

    print('Returning cleaned results')
    if isinstance(drop_cols,list):      return cleaned_data_df.drop(columns=drop_cols,inplace=True)
    else:                               return cleaned_data_df 

# %% ../nbs/companies.ipynb 13
def update(df: pd.DataFrame, columns: list, cf_ids: list = None):
    """
    Function to update companies in copper using a pandas DataFrame with a column of 'id' to identify
    companies and a list of the columns you would like to update.
    
    Either pass in a list of custom field ids, or a list will be created using matching column names.
    """

    if 'id' not in df.columns: raise 

    if cf_ids is None:
        cf_ids = [reverse_cf_lookup.get(col) for col in columns if col in reverse_cf_lookup]
        columns = [col for col in columns if col in reverse_cf_lookup]

    df = df[columns + ['id']]
    prepared_data = df.set_index('id').to_dict(orient='index')

    total_companies = len(df['id'])
    companies_updated = 0
    max_size = 10
    Sess = get_session(headers)

    # Initialize the tqdm progress bar
    progress_bar = tqdm(total=total_companies)

    while companies_updated < total_companies:
        current_batch_size = min(max_size, total_companies - companies_updated)
        payload = []

        # Loop to make `payload`
        for idx in range(companies_updated, companies_updated + current_batch_size):
            comp_id = int(df['id'].iloc[idx])

            cf_data_list = [{'custom_field_definition_id': cf_id, 'value': prepared_data[comp_id][col]}
                            for cf_id, col in zip(cf_ids, columns)]

            company_json = {"id": comp_id, 'custom_fields': cf_data_list}
            payload.append(company_json)

        json_data = {"companies": payload}
        request_sent = Sess.post('https://api.copper.com/developer_api/v1/companies/bulk_update', json=json_data)

        if request_sent.status_code != 200:
            print(request_sent.text)
            break
        else:
            companies_updated += current_batch_size
            progress_bar.update(current_batch_size)  # Update the progress bar

    progress_bar.close()  # Close the progress bar when done
    print('All companies updated.')
