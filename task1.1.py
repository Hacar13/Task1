import requests
import time
import matplotlib.pyplot as plt

# URLs
balance_url = "https://latest-960957615762.me-central1.run.app/getbalance"
logs_url = "https://latest-960957615762.me-central1.run.app/getlogs"
log_file = "bank_log.txt"
total_requests = 100

# Send requests
def send_requests(total_requests, url):
    print("Starting the reliability test...\n")
    for i in range(total_requests):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f"Request {i+1}: {r.status_code}")
            else:
                print(f"Request {i+1}: {r.status_code}, {r.text[:100]}")
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
        time.sleep(0.2)
    print("\nAll requests completed.\n")

# Download logs
def download_logs(logs_url, log_file):
    print("Downloading logs from server...")
    try:
        r = requests.get(logs_url, timeout=10)
        if r.status_code == 200:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(r.text)
            print("✓ Log file saved successfully.\n")
        else:
            print("✗ Could not download logs. Server returned:", r.status_code)
    except Exception as e:
        print("✗ Error while downloading logs:", e)

# Analyze logs
def analyze_logs(log_file):
    print("Analyzing log file...\n")
    success = 0
    error = 0
    warning = 0
    internal_500 = 0
    db_pool_error = 0

    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "Processing GET request" in line:
                success += 1
            elif "ERROR" in line:
                error += 1
                if "Internal Server Error" in line or "500" in line:
                    internal_500 += 1
                elif "Database Connection Pool Empty" in line:
                    db_pool_error += 1
            elif "WARNING" in line:
                warning += 1

    total = success + error + warning
    reliability = (success / (success + error)) * 100 if (success + error) > 0 else 0

    print("=== BANK LOG SUMMARY ===")
    print(f"Successful Requests: {success}")
    print(f"Errors: {error}")
    print(f"Warnings: {warning}")
    print(f"Internal Server Error (500): {internal_500}")
    print(f"Database Connection Pool Empty: {db_pool_error}")
    print(f"Total Log Entries: {total}")
    print(f"\nService Reliability: {reliability:.2f}%\n")

    return success, error, warning, internal_500, db_pool_error, reliability

# Plot results
def plot_results(success, error, warning, internal_500, db_pool_error, reliability):
    print("Creating reliability graph...\n")
    labels = ["Success", "Error", "Warning", "Error 500", "DB Pool Empty"]
    values = [success, error, warning, internal_500, db_pool_error]
    colors = ["green", "red", "orange", "purple", "blue"]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, values, color=colors, alpha=0.7, edgecolor="black")

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                 f"{int(height)}", ha='center', va='bottom', fontsize=9)

    plt.text(0.5, max(values) * 0.9, f"Reliability: {reliability:.2f}%",
             fontsize=12, fontweight="bold", color="blue", ha="center")

    plt.title("Banking App Reliability Test", fontsize=13, fontweight="bold")
    plt.xlabel("Response Type")
    plt.ylabel("Count")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("bank_reliability.png", dpi=300)
    plt.show()
    print("✓ Graph saved as bank_reliability.png\n")

# Main execution
def main():
    send_requests(total_requests, balance_url)
    download_logs(logs_url, log_file)
    success, error, warning, internal_500, db_pool_error, reliability = analyze_logs(log_file)
    plot_results(success, error, warning, internal_500, db_pool_error, reliability)
    print("All steps finished successfully.")


if __name__ == "__main__":
    main()
