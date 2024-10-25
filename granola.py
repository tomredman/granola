import os
import json
import time  # For generating timestamps
import argparse
import requests
from flask import Flask, request, jsonify
import queue
import threading  # For thread-safe operations

from colorama import Fore, Style, init

init(autoreset=True)

# Parse command-line arguments for the repository name and port
parser = argparse.ArgumentParser(
    description="Start a repository server and interact with the TC."
)
parser.add_argument("--name", required=True, help="Name of the repository")
parser.add_argument(
    "--port", type=int, required=True, help="Port number for the server"
)
args = parser.parse_args()


class FileStorageRepository:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.transaction_log = {}  # Transaction ID -> Operations
        self.file_metadata = {}  # Filename -> Last modification timestamp
        self.execution_lock = threading.Lock()  # Ensure thread-safe execution

    def prepare_transaction(self, tid, operation, filename, data):
        """Prepare transaction with optimistic execution."""
        with self.execution_lock:
            # Check for conflicts based on file modification times
            if filename in self.file_metadata and self.file_metadata[filename] > tid:
                return False  # Conflict detected
            # Log transaction operation for later execution
            self.transaction_log[tid] = (operation, filename, data)
            return True

    def commit_transaction(self, tid):
        """Commit transaction after validation."""
        with self.execution_lock:
            if tid in self.transaction_log:
                operation, filename, data = self.transaction_log[tid]
                if self._execute_operation(operation, filename, data):
                    del self.transaction_log[tid]  # Remove transaction from log
                    print(f"Transaction {tid} committed.")
                    return True
                return False
            return False

    def abort_transaction(self, tid):
        if tid in self.transaction_log:
            del self.transaction_log[tid]

    def _execute_operation(self, operation, filename, data):
        """Execute a single file operation."""
        filepath = os.path.join(self.storage_path, filename)
        if operation == "create" or operation == "update":
            try:
                with open(filepath, "w") as file:
                    json.dump(data, file)

                # In production, this strategy would need to be extended to support non-Unix-like systems
                # and other supported targets
                self.file_metadata[filename] = (
                    time.time()
                )  # Update file's last modification timestamp
            except Exception as e:
                print(f"Error executing operation: {e}")
                return False
        elif operation == "delete":
            if os.path.exists(filepath):
                os.remove(filepath)
            if filename in self.file_metadata:
                del self.file_metadata[filename]
        return True


# Flask app to simulate Granola server interactions with the file storage repository
app = Flask(__name__)
repo = FileStorageRepository("storage/" + args.name)


@app.route("/")
def index():
    return jsonify({"message": f"Hello from {args.name} Repository Server!"})


@app.route("/prepare", methods=["POST"])
def prepare():
    data = request.json
    tid = data["tid"]
    operation = data["operation"]
    data_content = data["data"]
    filename = data["filename"]

    if repo.prepare_transaction(tid, operation, filename, data_content):
        return jsonify(
            {
                "status": "prepared",
                "tid": tid,
                "operation": operation,
                "filename": filename,
                "data": data_content,
            }
        )
    else:
        return jsonify({"status": "conflict", "tid": tid}), 409


@app.route("/commit", methods=["POST"])
def commit():
    tid = request.json["tid"]
    if repo.commit_transaction(tid):
        return jsonify({"status": "committed", "tid": tid})
    else:
        return jsonify({"status": "error", "message": "Commit failed", "tid": tid}), 500


@app.route("/abort", methods=["POST"])
def abort():
    tid = request.json["tid"]
    # Assuming abort simply removes the transaction from the log without executing
    repo.abort_transaction(tid)
    return jsonify({"status": "aborted", "tid": tid})


def register_with_coordinator():
    # Assume the Transaction Coordinator's register endpoint is known and fixed
    tc_url = "http://localhost:8000/register"
    repo_url = f"http://localhost:{args.port}"
    response = requests.post(
        tc_url, json={"repo_name": args.name, "repo_url": repo_url}
    )
    if response.status_code == 200:
        print(f"Successfully registered {args.name} with the TC.")
    else:
        print(
            f"Failed to register {args.name} with the TC. Status code: {response.status_code}"
        )


if __name__ == "__main__":
    # Ensure the storage directory exists
    os.makedirs(os.path.join("storage", args.name), exist_ok=True)

    # Register this repository with the TC
    register_with_coordinator()

    # Start the Flask app
    app.run(debug=True, port=args.port)
