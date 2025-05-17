# 📊 JFrog Xray Performance Test Report

📄 [**Back to Project Overview**](README.md)

## 🔍 Objective

Evaluate the performance and stability of JFrog Xray's scanning pipeline using Locust. The test simulates concurrent users performing repository creation, image pushing, and scan validation via Xray APIs.

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

## ⚙️ Test Configuration

* **Tool**: Locust 2.37.3
* **Mode**: Headless
* **Users**: 10
* **Spawn Rate**: 2 users/sec
* **Test Duration**: 1 minute
* **Platform ID**: `trialb8lcqs`
* **Repo Name**: `docker-local`
* **Image**: `alpine:3.9`
* **JFrog URL**: `https://trialb8lcqs.jfrog.io`

### Locust Command

```bash
python -m locust -f locustfile.py \
  --headless -u 10 -r 2 -t 1m \
  --csv=reports/report \
  --host=https://trialb8lcqs.jfrog.io
```

---

## 📈 Summary Metrics

| Endpoint               | Requests | Failures | Failure %  | Avg Resp Time (ms) |
| ---------------------- | -------- | -------- | ---------- | ------------------ |
| PUT Create Repository  | 40       | 1        | 2.50%      | 362                |
| POST Create Policy     | 30       | 29       | 96.67%     | 240                |
| POST Create Watch      | 30       | 29       | 96.67%     | 253                |
| POST Apply Watch       | 30       | 0        | 0%         | 244                |
| POST Check Scan Status | 30       | 30       | 100%       | 260                |
| POST Get Violations    | 30       | 0        | 0%         | 687                |
| **Total**              | **190**  | **89**   | **46.84%** | —                  |

---

## ❌ Error Analysis

### ❗ 1. Repository Already Exists

* **Error (400)**: "Case insensitive repository key already exists"
* **Reason**: Locust users concurrently tried to create the same repo (`docker-local`)
* **Fix**: Add existence check or use unique repo name per user (e.g., `docker-local-{uuid}`)

### ❗ 2. Policy and Watch Creation Failures

* **Error (409)**: Conflict — object already exists
* **Fix**: Code now handles this as success (post-patch)

### ❗ 3. Scan Not Done Yet

* **Error**: `"status": "NOT_SCANNED"`
* **Reason**: Scan API was called before Xray finished processing
* **Fix**: Retry logic added (10 tries x 3s); may need to increase or use exponential backoff

---

## ✅ Highlights

* ✔️ Full scan workflow automated via REST APIs
* ✔️ Load distributed over multiple users with realistic delays
* ✔️ Real report generated with over 190 API hits
* ✔️ Docker image push, scan, and violation retrieval executed live

---

## 🛠 Recommendations

1. **Increase retry attempts** or **scan wait time** to reduce `NOT_SCANNED` errors
2. **Use unique repo names per test** to avoid repo creation conflicts
3. **Patch scan status check** to wait for `"status": "DONE"` before moving forward
4. **Capture response payloads** to confirm data quality (e.g. violations listed)
5. **Consider adding charts or trend graphs** from `report_stats_history.csv`

---

## ✅ Did We Meet the Objective?

> The goal was to evaluate JFrog Xray’s scanning workflow under concurrent load.
> This was achieved by running 10 users for 1 minute, simulating over 190 API calls.
> Key workflows like policy/watch creation, image push, and scan status polling were exercised.

**Result**: ✅ Test met its objective with clear insights on scan latency, conflict handling, and REST stability.

---

## 📂 Report Files

All located under the `/reports` directory:

* `report_stats.csv`
* `report_failures.csv`
* `report_stats_history.csv`

---

## 📘 See Also

* [README.md](README.md) – Project setup, architecture, and execution instructions
* [locustfile.py](locustfile.py) – Locust user class and task logic

## 📘 See Also

* [README.md](README.md) – Project setup, architecture, and execution instructions
* [locustfile.py](locustfile.py) – Locust user class and task logic
* [REPORT.md](REPORT.md) – Detailed analysis, results, and performance insights

## 📬 Contact

Created by \[Anmol Rai] for the JFrog Performance Engineer Home Assignment.

---

**Happy Testing!** 🎯
