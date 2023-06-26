import pandas as pd
import requests
from urllib.parse import quote
import boto3
import logging
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Create a separate logger for console output
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Initialize the S3 client
s3 = boto3.client("s3")

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("input.csv")

# Define the screenshot endpoint structure
API_URL = os.getenv("API_URL")
SCREENSHOT_ENDPOINT = (
    API_URL
    + "/api/v2/screenshot?size=900x700&url=https://embed.dataherald.com/v4/viz/{visualizationId}"
)

# S3 bucket config
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_S3_BUCKET_IMAGES_URL = os.getenv("AWS_S3_BUCKET_IMAGES_URL")

# Get the total number of rows
total_rows = df.shape[0]

# Create a new column for Image Link in the DataFrame
df["Image Link"] = ""

# Initialize a list to hold the image file names
image_files = []

# Iterate through each row of the DataFrame
for index, row in df.iterrows():
    logging.info(f"Processing row {index + 1} of {total_rows}...")

    # Get the current visualization ID
    viz_id = row["Visualization ID"]

    # Construct the URL for the API request
    url = SCREENSHOT_ENDPOINT.format(visualizationId=viz_id)

    logging.info(f"Screenshot endpoint url: {url}")

    try:
        # Make the API request and store the result
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the response content (which is the PNG file) to a .png file
            image_file_name = f"{quote(viz_id)}.png"
            with open(image_file_name, "wb") as f:
                f.write(response.content)

            # Add the image file name to the list
            image_files.append(image_file_name)

            # Upload the image to S3
            with open(image_file_name, "rb") as data:
                s3.upload_fileobj(
                    data, AWS_S3_BUCKET_NAME, "everest/" + image_file_name
                )

            # Construct the S3 public url
            s3_url = f"{AWS_S3_BUCKET_IMAGES_URL}/{image_file_name}"

            # Update the Image Link column for this row in the DataFrame
            df.at[index, "Image Link"] = s3_url
            logging.info(f"Successfully processed {viz_id} and wrote to CSV")
        else:
            logging.error(f"Error for {viz_id}: {response.status_code}")
    except Exception as e:
        logging.error(f"Exception occurred for {viz_id}: {str(e)}")

# Save the DataFrame to a new CSV file
df.to_csv("output.csv", index=False)

# Remove the downloaded image files
for image_file in image_files:
    os.remove(image_file)
