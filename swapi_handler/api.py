import asyncio
import logging

import aiohttp
import petl as etl

class SWAPIHandler:
    """
    SWAPIHandler is a class that handles the retrieval and processing of data from the Star Wars API (SWAPI).
    """
    def __init__(self):
        self.planet_dict = {}


    async def get_data_from_api(self, session, url: str) -> dict:
        """
        Retrieves data from the specified URL using the provided session.

        Args:
            url (str): The URL to fetch data from.
            session (aiohttp.ClientSession): The session to use for the HTTP request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            aiohttp.ClientResponseError: If there is an error fetching data from the API.
        """
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return None


    async def resolve_homeworld(self, session, url: str) -> str:
        """
        Resolves the homeworld URL to its corresponding planet name.

        Args:
            session (aiohttp.ClientSession): The session to use for API requests.
            url (str): The URL of the homeworld.

        Returns:
            str: The name of the homeworld planet.

        Raises:
            aiohttp.ClientResponseError: If there is an error fetching data from the API.
        """
        if url in self.planet_dict:
            return self.planet_dict[url]
        else:
            if url.startswith('https'):
                response = await self.get_data_from_api(session, url)
                if response:
                    planet_name = response['name']
                    self.planet_dict[url] = planet_name
                    return planet_name  
            return None


    async def preprocess_homeworlds(self, session, data: list[dict]) -> list[dict]:
        """
        Preprocesses the homeworld URLs in the data by resolving them to their corresponding planet names.

        Args:
            session (aiohttp.ClientSession): The session to use for API requests.
            data (list[dict]): The list of data to preprocess.

        Returns:
            list[dict]: The preprocessed data with homeworld URLs replaced by planet names.

        Raises:
            aiohttp.ClientResponseError: If there is an error fetching data from the API.
        """
        for row in data:
            if 'homeworld' in row and row['homeworld']:
                row['homeworld'] = await self.resolve_homeworld(session, row['homeworld'])
        return data
    

    def clean_data(self, data: list[dict]) -> etl.Table:
        """
        Cleans the data by removing unnecessary fields and adding a 'date' field.

        Args:
            data (list[dict]): The data to clean.

        Returns:
            etl.Table: The cleaned data as an ETL table.
        """
        data = etl.fromdicts(data)
        data = etl.addfield(data, 'date', lambda row: row['edited'].split('T')[0])
        data = etl.cutout(
            data, 
            'films', 
            'species', 
            'vehicles', 
            'starships', 
            'created', 
            'edited',
            'url'
            )
        return data
    

    async def get_data_and_url(self, session, url: str) -> tuple[list[dict], str]:
        """
        Retrieves data and the next URL from the specified URL using the provided session.

        Args:
            session (aiohttp.ClientSession): The session to use for the HTTP request.
            url (str): The URL to fetch data from.

        Returns:
            tuple[list[dict], str]: A tuple containing the data and the next URL.

        Raises:
            aiohttp.ClientResponseError: If there is an error fetching data from the API.
        """
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                swapi = await response.json()
                data = swapi['results']
                url = swapi['next']
                return data, url    
        except aiohttp.ClientResponseError as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return [], None
        

    async def fetch_all_pages(self, start_url: str) -> etl.MemorySource:
        """
        Fetches all pages of data from the SWAPI starting from the specified URL.

        Args:
            start_url (str): The URL to start fetching data from.

        Returns:
            etl.MemorySource: A memory source containing the fetched data as CSV.

        Raises:
            aiohttp.ClientResponseError: If there is an error fetching data from the API.
        """
        headers_included: bool = False
        url = start_url
        csv_buffer = etl.MemorySource()

        async with aiohttp.ClientSession() as session:
            while url:
                try:
                    data, url = await self.get_data_and_url(session, url)
                    data = await self.preprocess_homeworlds(session, data)
                    results = self.clean_data(data)

                    if not headers_included:
                        etl.tocsv(results, csv_buffer, encoding='utf-8')
                        headers_included = True
                    else:
                        etl.appendcsv(results, csv_buffer, encoding='utf-8')
                        
                except Exception as e:
                    logging.error(f"Error processing data from {url}: {e}")
                    break
        return csv_buffer