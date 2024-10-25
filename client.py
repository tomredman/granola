import argparse
import random
import string
import time
import requests
import json
import logging

from colorama import Fore, Style, init

# Parse command-line arguments for the repository name and port
parser = argparse.ArgumentParser(description="Fire off requests to the TC.")
parser.add_argument("--file", required=True, help="Name of the file to create & update")
args = parser.parse_args()

init(autoreset=True)

# Create a custom logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)


class GranolaClient:
    def __init__(self, server_url):
        self.server_url = server_url

    def invokeSingle(self, repository_id, transaction_data, read_only=False):
        """Invoke a transaction on a single repository."""
        payload = {
            "repository_id": repository_id,
            "transaction_data": transaction_data,
            "read_only": read_only,
        }
        response = requests.post(f"{self.server_url}/invokeSingle", json=payload)
        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            response_json = None
        return response_json

    def invokeIndep(self, repositories, transaction_data):
        """Invoke independent transactions on multiple repositories."""
        payload = {"repositories": repositories, "transaction_data": transaction_data}
        response = requests.post(f"{self.server_url}/invokeIndep", json=payload)
        return response.json()

    def invokeCoord(self, repositories, transaction_data):
        """Invoke a coordinated transaction across multiple repositories."""
        payload = {"repositories": repositories, "transaction_data": transaction_data}
        response = requests.post(f"{self.server_url}/invokeCoord", json=payload)
        return response.json()


# Example usage
if __name__ == "__main__":
    tc_url = "http://localhost:8000"
    client = GranolaClient(tc_url)

    # Single repository transaction
    # single_result = client.invokeSingle("repo1", {"operation": "read", "key": "value1"}, True)
    # print("Single transaction result:", single_result)

    # Independent transactions
    # indep_result = client.invokeIndep(["repo1", "repo2"], {"operation": "create", "data": {"key1": "value1"}})
    # print("Independent transaction result 1:", indep_result)
    for i in range(500):
        should_sleep = random.randint(0, 3)

        # throw a wrench in the works
        if should_sleep == 1:
            sleep_time = random.uniform(0.1, 0.8)
            logger.info(
                Fore.YELLOW + "Sleeping for " + str(sleep_time) + "s" + Style.RESET_ALL
            )
            time.sleep(sleep_time)

        random_length = random.randint(1, 10000)
        random_value = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=random_length)
        )

        filename = (
            args.file
        )  # this is the file that the transaction will be performed on, or the resource a user is "editing"
        tid = int(time.time() * 1000)
        indep_result = client.invokeIndep(
            ["repo1", "repo2", "repo3", "repo4"],
            {
                "operation": "create",
                "filename": filename,
                "data": {"tid": tid, "autoKey" + str(i): random_value},
            },
        )

        logger.info(
            Fore.GREEN
            + "Independent transaction result "
            + str(i)
            + " for file "
            + filename
            + Style.RESET_ALL
        )
        # print("Independent transaction result AUTO "+str(i)+":", indep_result)

    # Coordinated transaction
    # coord_result = client.invokeCoord(["repo4", "repo5"], {"operation": "update", "data": {"key4": "new_value4"}})
    # print("Coordinated transaction result:", coord_result)
