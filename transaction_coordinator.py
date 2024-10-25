import random
from flask import Flask, request, jsonify
import requests
import time

from colorama import Fore, Style, init

init(autoreset=True)

app = Flask(__name__)


class TransactionCoordinator:
    def __init__(self):
        self.repository_endpoints = {}

    def register_repository(self, repo_name, repo_url):
        self.repository_endpoints[repo_name] = repo_url

    def get_repository_url(self, repo_name):
        return self.repository_endpoints.get(repo_name)

    def generate_timestamp(self):
        return int(time.time() * 1000)

    def start_transaction(self, repository_names, transaction_details, read_only=False):
        tid = self.generate_timestamp()
        filename = transaction_details["filename"]

        repository_urls = [
            self.get_repository_url(name)
            for name in repository_names
            if self.get_repository_url(name)
        ]
        execute_payload = {"tid": tid, "filename": filename, **transaction_details}

        # First, attempt to prepare the transaction at each repository
        preparation_results = [
            requests.post(f"{url}/prepare", json=execute_payload).json()
            for url in repository_urls
        ]
        prepared = all(
            result.get("status") == "prepared" for result in preparation_results
        )

        # Decide the action based on preparation result
        action = "commit" if prepared else "abort"
        # Execute commit or abort action at each repository
        execution_results = [
            requests.post(f"{url}/{action}", json={"tid": tid}).json()
            for url in repository_urls
        ]
        success = all(
            result.get("status") == "committed" for result in execution_results
        )

        if not success:
            errors = [
                result
                for result in execution_results
                if result.get("status") != "committed"
            ]
            # todo: execute rollback!
            return {
                "status": "error",
                "transaction": tid,
                "action": action,
                "message": "Transaction failed, rolling back.",
                "errors": errors,
            }

        return {"status": "success", "transaction": tid, "action": action}


tc = TransactionCoordinator()


@app.route("/")
def index():
    return jsonify({"message": f"Hello from the coordinator!"})


@app.route("/repos")
def list_repos():
    return jsonify(tc.repository_endpoints)


@app.route("/register", methods=["POST"])
def register_repository():
    data = request.json
    tc.register_repository(data["repo_name"], data["repo_url"])
    return jsonify({"message": "Repository registered successfully."})


@app.route("/invokeSingle", methods=["POST"])
def invoke_single_transaction():
    data = request.json
    repository_names = [data["repository_id"]]
    transaction_data = data["transaction_data"]
    read_only = data["read_only"]

    repository_urls = [
        tc.get_repository_url(name)
        for name in repository_names
        if tc.get_repository_url(name)
    ]
    if repository_urls:
        result = tc.start_transaction(repository_names, transaction_data, read_only)
        return jsonify(result)
    else:
        return jsonify({"error": "No valid repositories found"}), 404


@app.route("/invokeIndep", methods=["POST"])
def invoke_independent_transaction():
    data = request.json
    repository_names = data["repositories"]
    transaction_data = data["transaction_data"]

    repository_urls = [
        tc.get_repository_url(name)
        for name in repository_names
        if tc.get_repository_url(name)
    ]
    if repository_urls:
        result = tc.start_transaction(repository_names, transaction_data)
        return jsonify(result)
    else:
        return jsonify({"error": "No valid repositories found"}), 404


@app.route("/invokeCoord", methods=["POST"])
def invoke_coordinated_transaction():
    data = request.json
    repository_names = data["repositories"]
    transaction_data = data["transaction_data"]

    repository_urls = [
        tc.get_repository_url(name)
        for name in repository_names
        if tc.get_repository_url(name)
    ]
    if repository_urls:
        result = tc.start_transaction(repository_names, transaction_data)
        return jsonify(result)
    else:
        return jsonify({"error": "No valid repositories found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=8000)
