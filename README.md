# JFrog Xray Load Testing with Locust

This project implements a distributed load testing framework using **Locust** and **Python** to evaluate **JFrog Xray's** scanning capabilities under load.

---

## 📌 Objective

Simulate concurrent users who:

* Create Docker repositories
* Push Docker images
* Trigger security scans via Xray
* Check scan statuses
* Retrieve violations

This test helps identify Xray performance bottlenecks and establish baseline metrics.

---

## ⚙️ Prerequisites

1. **JFrog Trial Account**

   * Sign up: [https://jfrog.com/start-free/trialOptions](https://jfrog.com/start-free/trialOptions)
   * Retrieve your Platform ID (e.g. `yourorg.jfrog.io` → `yourorg`)

2. **Create Admin User**

   * Log into the platform → Administration → User Management → Create new user (Admin role)

3. **Docker** installed on the machine (for pushing images)

4. **Python 3.7+** and **Locust** installed:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run the Test

### 1. Set Environment Variables

Create a `.env` file or export manually:

```bash
export JFROG_USERNAME=admin_user
export JFROG_PASSWORD=your_password
export JFROG_PLATFORM_ID=yourplatformid
```

### 2. Run Single-Node Test

```bash
locust -f locustfile.py --headless -u 10 -r 2 -t 1m --csv=reports/report
```

### 3. Run Distributed Test (Optional)

**Master Node**

```bash
locust -f locustfile.py --master --csv=reports/report
```

**Worker Nodes**

```bash
locust -f locustfile.py --worker --master-host=<master-ip>
```

---

## 📊 Reports

Running with `--csv=report` creates:

* `reports/report_stats.csv` → Endpoint stats
* `reports/report_stats_history.csv` → Timeline metrics
* `reports/report_failures.csv` → Errors (if any)

These can be imported into Excel or plotted with matplotlib.

---

## 🗂 Directory Structure

```
.
├── locustfile.py
├── requirements.txt
├── run.sh
├── .env.example
├── README.md
└── reports/
```

---

## 🧠 Assumptions / Notes

* Docker CLI commands are used inside the script to push images
* The image `alpine:3.9` is used as a sample payload
* All operations are REST API based and mapped to Xray/Artifactory endpoints

---

## 📦 Sample Test Command

```bash
locust -f locustfile.py --headless -u 20 -r 5 -t 2m --csv=reports/loadtest
```

---

## 📘 See Also

* [REPORCT.md](REPORT.md) – JFrog Xray Performance Test Report

## 📬 Questions?

Reach out at \[[your\_email@example.com](mailto:your_email@example.com)]

Happy Testing! 🎯
