# 🔍 TopCV Job Crawler

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-grade tool for continuously crawling job listings from TopCV.vn. This tool automatically scrapes job information, processes the data, and saves it to both JSON and CSV formats for easy analysis.

## 📘 Features

- Crawls job listings from TopCV.vn with configurable parameters
- Extracts detailed job information including salary, requirements, benefits
- Supports continuous operation with configurable intervals
- Prevents duplicates with intelligent caching
- Handles rate limiting with automatic backoff
- Provides robust logging
- Saves data in both JSON and CSV formats

## 🧰 Tech Stack

- Python 3.7+
- BeautifulSoup4 for HTML parsing
- Pandas for data manipulation
- Requests for HTTP requests
- PyYAML for configuration management
- Schedule for periodic execution

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Option 1: Using the setup script

The easiest way to get started is using the provided setup script:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

This will:
1. Check for required dependencies
2. Create a virtual environment
3. Install all required packages
4. Set up log and data directories

### Option 2: Manual installation

1. Clone this repository:
   ```bash
   git clone https://github.com/ngnphamgiahuy/topcv-job-crawler.git
   cd topcv-job-crawler
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create required directories:
   ```bash
   mkdir -p data logs
   ```

### Option 3: Using Docker

```bash
# Build the Docker image
docker build -t topcv-job-crawler .

# Run the container
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs topcv-job-crawler
```

## 🚀 Usage

### Basic Usage

To start the crawler with default settings:

```bash
python crawler.py
```

By default, the crawler runs continuously, checking for new jobs at the interval specified in the config file.

### Command Line Options

```
python crawler.py --help
```

Available options:
- `--config`, `-c`: Path to the configuration file (default: config.yaml)
- `--once`, `-o`: Run once and exit (for development/testing)
- `--full`, `-f`: Crawl all available pages, not just the configured number

### Examples

Run once for testing:
```bash
python crawler.py --once
```

Run with a specific config file:
```bash
python crawler.py --config my-config.yaml
```

Perform a full crawl and then exit:
```bash
python crawler.py --once --full
```

## 🛠️ Configuration

The crawler is configured through the `config.yaml` file. Here are the key settings:

```yaml
crawling:
  base_url: "https://www.topcv.vn/tim-viec-lam-moi-nhat"
  pages_to_scan: 3  # Number of pages to scan per cycle
  sleep_interval: 1800  # Time to wait between cycles in seconds (30 minutes)
  timeout: 30  # Request timeout in seconds
  max_retries: 5  # Maximum number of retries for failed requests
  user_agent: "Mozilla/5.0 ..."

output:
  jobs_json: "data/jobs.json"
  jobs_csv: "data/jobs.csv"
  job_cache_file: "data/job_cache.pkl"

logging:
  log_file: "logs/crawler.log"
  log_level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

runtime:
  max_runtime: 0  # Maximum runtime in seconds (0 = unlimited)
  daemon_mode: true  # Run continuously in a loop
```

## 📊 Output Data

The crawler generates two main output files:

1. `data/jobs.json`: Contains the raw job data in JSON format
2. `data/jobs.csv`: Contains the same data in CSV format for easy import into data analysis tools

The data includes:
- Job title, company name, and location
- Salary information (including min/max values and currency)
- Job description, requirements, and benefits
- Posted date and application deadline
- URL to the original job posting

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 