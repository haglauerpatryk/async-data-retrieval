from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.views.decorators.http import require_GET

from asgiref.sync import sync_to_async

from .api import SWAPIHandler
from .models import DatasetMetadata, DatasetFiles

from io import StringIO
import petl as etl
import csv


class IndexView(generic.TemplateView):
    """
    A basic view that renders the index page by retrieving all dataset metadata.
    """
    datasets = DatasetMetadata.objects.all()
    extra_context = {
        'datasets': datasets
    }
    template_name = 'swapi_handler/index.html'


def retrieve_dataset(dataset_id: int) -> list[list[str]]:
    """
    Retrieves and decodes the CSV file associated with a dataset.

    Args:
        dataset_id (int): The primary key of the dataset to retrieve.

    Returns:
        list[list[str]]: A list of lists where each sub-list is a row from the CSV file.
    """
    dataset_file = DatasetFiles.objects.get(dataset=dataset_id)
    csv_data = dataset_file.csv_file.read().decode('utf-8')

    csv_reader = csv.reader(StringIO(csv_data))
    list_of_lists = list(csv_reader)
    print(type(list_of_lists))
    return list_of_lists


@require_GET
def dataset_details(request, dataset_id: int) -> HttpResponse:
    """
    Renders a detail view for a specific dataset.

    Args:
        request: The HttpRequest object.
        dataset_id (int): The primary key of the dataset whose details are to be displayed.

    Returns:
        HttpResponse: Renders the dataset detail page with the given context.
    """
    context = {
        'dataset_id': dataset_id,
    }
    return render(request, 'swapi_handler/dataset_details.html', context)


@require_GET
def fetch_data(request, dataset_id: int) -> JsonResponse:
    """
    Fetches a subset of rows from a dataset CSV file and returns it in JSON format.

    Args:
        request: The HttpRequest object, expects a 'rows' parameter to specify pagination.
        dataset_id (int): The primary key of the dataset from which data is fetched.

    Returns:
        JsonResponse: A JSON response containing the specified slice of data rows.
    """
    try:
        rows = int(request.GET.get('rows', 0))
    except ValueError:
        rows = 0

    list_of_lists = retrieve_dataset(dataset_id)

    data = etl.rowslice(list_of_lists, rows, rows + 10)
    data = etl.dicts(data)
    
    return JsonResponse(list(data), safe=False)


@require_GET
def column_selection(request, dataset_id: int) -> HttpResponse:
    """
    Retrieves and displays CSV column headers for dataset selection.

    Args:
        request: The HttpRequest object.
        dataset_id (int): The primary key of the dataset.

    Returns:
        HttpResponse: Renders a page to allow users to select columns from the dataset.
    """
    dataset_file = DatasetFiles.objects.get(dataset=dataset_id)
    csv_data = dataset_file.csv_file.read().decode('utf-8')

    csv_reader = csv.reader(StringIO(csv_data))
    list_of_lists = list(csv_reader)

    headers = list_of_lists[0]

    context = {
        'dataset_id': dataset_id,
        'headers': headers
    }
    return render(request, 'swapi_handler/column_selection.html', context)


@require_GET
def count_occurrences(request, dataset_id: int) -> JsonResponse:
    """
    Counts occurrences of specified column values in a dataset.

    Args:
        request: The HttpRequest object, should include 'columns' as a comma-separated string.
        dataset_id (int): The primary key of the dataset.

    Returns:
        JsonResponse: A JSON response containing the counts of values in specified columns.
    """
    columns = request.GET.get('columns')

    if not columns:
        return JsonResponse({'error': 'No columns specified'}, status=400)

    # Split the columns string into a list of column names
    columns_list = columns.split(',')

    dataset_file = DatasetFiles.objects.get(dataset=dataset_id)
    csv_data = dataset_file.csv_file.read().decode('utf-8')

    csv_reader = csv.reader(StringIO(csv_data))
    list_of_lists = list(csv_reader)

    table = etl.wrap(list_of_lists)
    counts = etl.valuecounts(table, *columns_list)

    result = list(counts.dicts())
    
    return JsonResponse(result, safe=False)


async def convert_and_download_csv(request) -> HttpResponse:
    """
    Asynchronously fetches data from the Star Wars API, converts it to CSV format, and initiates a download.

    Args:
        request: The HttpRequest object.

    Returns:
        HttpResponse: A response that triggers the download of the CSV file with the appropriate headers.
    """
    swapi = SWAPIHandler()
    base_url = 'https://swapi.dev/api/people/'
    filename = 'star_wars_characters.csv'
    csv_buffer = await swapi.fetch_all_pages(base_url)
    save_csv = sync_to_async(save_csv_file)
    await save_csv(csv_buffer, filename)

    response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response


def save_csv_file(csv_buffer: object, filename: str) -> None:
    """
    Helper function for the purpose of sync_to_async conversion.
    Saves a CSV file buffer to the database linked with dataset metadata and file records.

    Args:
        csv_buffer (object): The buffer containing the CSV data to be saved.
        filename (str): The name of the file to be saved.

    Side effects:
        Creates a new entry in DatasetMetadata and DatasetFiles models and saves the file.
    """
    dataset_metadata = DatasetMetadata.objects.create(
        filename=filename
    )
    dataset_file = DatasetFiles.objects.create(
        dataset=dataset_metadata
    )
    dataset_file.csv_file.save(filename, ContentFile(csv_buffer.getvalue()))
