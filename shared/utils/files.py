import io
import csv
import pyarrow as pa
import pyarrow.parquet as pq


def convert_dicts_to_csv(data: list[dict], separator: str = ';', encoding: str = 'utf-8') -> str:
    """
    Convert a list of dictionaries to a CSV formatted string.
    
    Parameters:
        data (list[dict]): A list of dictionaries to convert to CSV.
        separator (str): The separator character used in the CSV file (default is ';').
        encoding (str): The encoding format for the CSV content (default is 'utf-8').
    
    Returns:
        str: The CSV formatted string.
    """
    # Get the column names from the first dictionary in the list
    column_names = list(data[0].keys())

    # Use StringIO to mimic file writing.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=column_names, delimiter=separator)

    # Write the CSV data to the StringIO buffer
    writer.writeheader()
    for item in data:
        writer.writerow(item)

    # Get the CSV data as a string
    csv_data = output.getvalue()
    output.close()

    return csv_data


def convert_dicts_to_parquet(data: list[dict]) -> io.BytesIO:
    """
    Converts a list of dictionaries to a Parquet format in memory and returns a buffer containing the Parquet data.

    Args:
        data (list[dict]): A list of dictionaries where each dictionary represents a row of data to be converted into Parquet format.

    Returns:
        io.BytesIO: A buffer object that contains the Parquet file data as bytes, ready to be read or written to a file.
    """
    table = pa.Table.from_pylist(data)
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)
    return buf



def write_buffer_to_file(buffer: io.BytesIO, file_path: str) -> None:
    """
    Writes the contents of a buffer to a specified file.

    Args:
        buffer (io.BytesIO): The buffer containing data to write.
        file_path (str): The path to the file where the data should be saved.

    Returns:
        None
    """
    # Ensure the buffer's position is at the beginning
    buffer.seek(0)

    # Open the file in binary write mode and write the buffer
    with open(file_path, 'wb') as f:
        f.write(buffer.read())