from locust import HttpUser, task, between
import base64
import os
import json
import subprocess
import logging
import time
from datetime import datetime, timezone, timedelta

USERNAME = os.getenv("JFROG_USERNAME")
PASSWORD = os.getenv("JFROG_PASSWORD")
PLATFORM_ID = os.getenv("JFROG_PLATFORM_ID")
REPO_NAME = os.getenv("JFROG_REPO_NAME", "docker-local")
IMAGE_NAME = os.getenv("DOCKER_IMAGE_NAME", "alpine")
TAG = os.getenv("DOCKER_IMAGE_TAG", "3.9")

class JFrogXrayUser(HttpUser):
    wait_time = between(1, 3)
    host = f"https://{PLATFORM_ID}.jfrog.io"

    # moved inside on_start

    def on_start(self):
        self.WATCH_NAME = f"watch_{int(time.time())}"
        self.auth_header = self._generate_auth_header()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth_header
        }

    def _generate_auth_header(self):
        token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
        return f"Basic {token}"

    @task
    def run_full_scan_pipeline(self):
        self.create_repository()
        self.push_docker_image()
        self.create_policy()
        self.create_watch()
        self.apply_watch()
        self.check_scan_status()
        self.get_violations()

    def create_repository(self):
        url = f"{self.host}/artifactory/api/repositories/{REPO_NAME}"
        payload = {
            "key": REPO_NAME,
            "packageType": "docker",
            "rclass": "local",
            "xrayIndex": True
        }
        with self.client.put(url, headers=self.headers, json=payload, name="Create Repository", catch_response=True) as response:
            if response.status_code == 200 or response.status_code == 409:
                response.success()
            else:
                response.failure(response.text)

    def push_docker_image(self):
        try:
            subprocess.run(["docker", "pull", f"{IMAGE_NAME}:{TAG}"], check=True)
            subprocess.run(["docker", "login", f"{PLATFORM_ID}.jfrog.io", "-u", USERNAME, "-p", PASSWORD], check=True)
            subprocess.run(["docker", "tag", f"{IMAGE_NAME}:{TAG}", f"{PLATFORM_ID}.jfrog.io/{REPO_NAME}/{IMAGE_NAME}:{TAG}"], check=True)
            subprocess.run(["docker", "push", f"{PLATFORM_ID}.jfrog.io/{REPO_NAME}/{IMAGE_NAME}:{TAG}"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error("Docker push failed: %s", e)

    def create_policy(self):
        url = f"{self.host}/xray/api/v2/policies"
        payload = {
            "name": "sec_policy_1",
            "description": "High severity CVEs",
            "type": "security",
            "rules": [{
                "name": "block_high",
                "criteria": {"min_severity": "high"},
                "actions": {"block_download": {"active": False}},
                "priority": 1
            }]
        }
        with self.client.post(url, headers=self.headers, json=payload, name="Create Policy", catch_response=True) as response:
            if response.status_code == 200 or response.status_code == 409:
                response.success()
            else:
                response.failure(response.text)

    def create_watch(self):
        url = f"{self.host}/xray/api/v2/watches"
        payload = {
            "general_data": {
                "name": self.WATCH_NAME,
                "description": "Watch for docker repo",
                "active": True
            },
            "project_resources": {
                "resources": [{
                    "type": "repository",
                    "bin_mgr_id": "default",
                    "name": REPO_NAME,
                    "filters": [{"type": "regex", "value": ".*"}]
                }]
            },
            "assigned_policies": [{"name": "sec_policy_1", "type": "security"}]
        }
        with self.client.post(url, headers=self.headers, json=payload, name="Create Watch", catch_response=True) as response:
            if response.status_code == 200 or response.status_code == 409:
                response.success()
            else:
                response.failure(response.text)

    def apply_watch(self):
        url = f"{self.host}/xray/api/v1/applyWatch"
        now = datetime.now(timezone.utc)
        payload = {
            "watch_names": [self.WATCH_NAME],
            "date_range": {
                "start_date": (now - timedelta(minutes=5)).isoformat(),
                "end_date": now.isoformat()
            }
        }
        with self.client.post(url, headers=self.headers, json=payload, name="Apply Watch", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(response.text)

    def check_scan_status(self):
        url = f"{self.host}/xray/api/v1/scanArtifact"
        payload = {
            "component_id": f"docker://{REPO_NAME}/{IMAGE_NAME}:{TAG}"
        }
        with self.client.post(url, headers=self.headers, json=payload, name="Trigger Scan", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(response.text)
                return False

        status_url = f"{self.host}/xray/api/v1/scan/status"
        for _ in range(10):
            with self.client.post(status_url, headers=self.headers, json=payload, name="Check Scan Status", catch_response=True) as response:
                if '"status":"DONE"' in response.text:
                    response.success()
                    return True
                else:
                    response.failure("Scan not done yet")
            time.sleep(6)
        return False

    def get_violations(self):
        time.sleep(10)  # Give Xray time to index violations
        if not self.check_scan_status():
            return
        url = f"{self.host}/xray/api/v1/violations"
        payload = {
            "filters": {
                "watch_name": self.WATCH_NAME,
                "violation_type": "Security",
                "min_severity": "High",
                "resources": {
                    "artifacts": [{
                        "repo": REPO_NAME,
                        "path": f"{IMAGE_NAME}/{TAG}/manifest.json"
                    }]
                }
            },
            "pagination": {"order_by": "created", "direction": "asc", "limit": 100, "offset": 1}
        }
        self.client.post(url, headers=self.headers, json=payload, name="Get Violations")
