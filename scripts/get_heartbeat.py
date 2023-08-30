"""
    Create a HTTP GET request to the following URL:

        http://localhost/api/v1/heartbeat

    The response should be a JSON object. Print the response to the console.

"""
import json

import requests


def main():

    endpoint_url = "http://localhost/api/v1/heartbeat"

    # 1. Create a HTTP GET request to the following URL:
    #    http://localhost/api/v1/heartbeat
    # 2. The response should be a JSON object. Print the response to the console.

    response = requests.get(endpoint_url, headers={
        "Accept": "application/json"}, timeout=10)
    print(json.dumps(response.json(), indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
