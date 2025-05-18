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

## 🔐 Environment Setup

1. **Create a `.env` file in your project root**:

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your JFrog credentials and platform ID**:

   ```env
   JFROG_USERNAME=your_admin_user
   JFROG_PASSWORD=your_password
   JFROG_PLATFORM_ID=yourplatformid
   ```

3. **Run the test using the script**:

   ```bash
   bash run.sh
   ```

> ✅ Note: The `.env` file is excluded from Git and should not be committed.

---

## 🚀 How to Run the Test

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Single-Node Test

```bash
python -m locust -f locustfile.py --headless -u 10 -r 2 -t 1m --csv=reports/report --host=https://$JFROG_PLATFORM_ID.jfrog.io
```

### 3. Run Distributed Test (Optional)

**Master Node**

```bash
python -m locust -f locustfile.py --master --csv=reports/report
```

**Worker Nodes**

```bash
python -m locust -f locustfile.py --worker --master-host=<master-ip>
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
├── REPORT.md
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
python -m locust -f locustfile.py --headless -u 20 -r 5 -t 2m --csv=reports/loadtest --host=https://$JFROG_PLATFORM_ID.jfrog.io
```

---

## 📘 See Also

* [REPORT.md](REPORT.md) – Performance test results, metrics, and analysis
* [locustfile.py](locustfile.py) – Load test logic and REST API calls

---

## 📬 Contact

Created for the JFrog Performance Engineer Home Assignment.

Happy Testing! 🎯
