import requests
import time
import sys
from pandas import DataFrame


class ConnectionFailed(Exception):
    pass


class GymManager:
    def __init__(self):
        """Initializes connection with Gym Manager API. Use your credentials to log in."""
        self.base_url = "https://trainmore-apiv6.gymmanager.eu/api/v1"
        self.authentication_response = {}
        self.headers = {}
        self.responses = []
        self.duration = 0

    def authenticate(self, user_name: str, password: str) -> None:
        self.user_name = user_name
        self.password = password

        self.authentication_response = requests.post(
            url="https://trainmore-apiv6.gymmanager.eu/api/v1/Authorize/AuthenticateJson",
            json={
                "username": self.user_name,
                "password": self.password,
                "apiLicense": "",
                "macAddress": "",
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        ).json()

        print(self.authentication_response)

        if self.authentication_response["status"]["success"] == False:
            raise ConnectionFailed(
                f"Code: {self.authentication_response['status']['code']}, Message: {self.authentication_response['status']['message']}"
            )
        else:
            print(self.authentication_response)
            self.headers = {
                "Authorization": f"{self.authentication_response['data']}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }

    def connection_test(self) -> str:
        """Test the connection. Continue execution when response status code is 200."""
        url = "https://trainmore-apiv6.gymmanager.eu/api/v1/Clubs?onlyActive=true"
        headers = self.headers
        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            result = "Connection was successful!"
        else:
            raise ConnectionFailed(
                f"Connection Failed with error {response.status_code}: {response.text}"
            )

        return result

    def post_data(self, data: dict, callbck: None = None) -> list[dict]:
        """Posts the transformed data to Gym Manager. Returns a report with status code and message per row."""
        timestamp_start = time.time()
        for i, row in enumerate(data):
            response = requests.post(
                url=row["url"], json=row["body"], headers=self.headers
            )

            self.responses.append(
                {
                    "ppl_mshp_id": row["ppl_mshp_id"],
                    "status_code": response.status_code,
                    "message": response.json()["status"]["message"],
                    "post_url": row["url"],
                    "body": row["body"],
                }
            )

            progress = (i + 1) / len(data)
            callbck(progress=progress, step=i, item_count=len(data))
            print(progress)

            # report progress to console

            # sys.stdout.write("\r")
            # sys.stdout.write("[%-20s] %d%%" % ("=" * int(20 * j), 100 * j))
            # sys.stdout.flush()

        timestamp_end = time.time()
        self.duration = round(timestamp_end - timestamp_start, 2)

    def report(self) -> str:
        """Returns a report of all processed records and their status."""
        return f"All {len(self.responses)} records processed.\nReport was saved to report.csv. Please check for errors.\nPosting these records took {self.duration} seconds.\nTime saved is {len(self.responses) * 5} minutes."

    def export_report(self) -> None:
        self.report = DataFrame(self.responses).to_csv(
            "report.csv", sep=";", index=False
        )
        self.report_export = DataFrame(self.responses).to_csv(
            sep=";", index=False, lineterminator="\n"
        )
        return self.report
