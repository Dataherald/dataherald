# Visualization Screenshot Generator

This Python tool helps our engineering team streamline processes for the operations team. It requires a CSV file with a Visualization ID. Using this ID, the tool fetches screenshots from a specific API, then uploads them to an Amazon S3 bucket. As a final step, it generates a new CSV file, just like the original, but with an extra column - the URL of the uploaded screenshot. Essentially, give it a Visualization ID, and it does the heavy lifting.

## Prerequisites

- AWS credentials configured on your machine with a user that has permissions to perform the necessary actions (S3:PutObject, S3:GetObject, etc.). You can set up the credentials by installing AWS CLI and using `aws configure`.

## How to use:

1. Set up a Python virtual environment.

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install the required packages.

```sh
pip3 install -r requirements.txt
```

3. Setup the `.env` file with your specific settings. You can use the `.env.example`

4. Make sure you have the input CSV in the correct format. The CSV file can contain various fields, but it _must include_ a `Visualization ID` field:

```csv
City Name,State Name,Visualization ID
Los Angeles,CA,64305b5b577f0c04dcdcca4a
...
```

5. Run the script:

```sh
python main.py
```

The output CSV file will follow the same structure as the input CSV, with an additional column at the end containing the S3 URL of the corresponding screenshot.

## Logging:

The script logs progress to both a log file (`app.log`) and the console. It records the number of rows that have been successfully processed, as well as any rows that have encountered errors.

## Troubleshooting:

If you encounter issues while running the script, please refer to the `app.log` file for more detailed information about the error.
