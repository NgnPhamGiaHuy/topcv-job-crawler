<div align="center">
  <h1>🔍 TopCV Job Crawler</h1>
  <p>A production-grade tool for continuously crawling job listings from job sites.</p>

  <p>
    <img src="https://img.shields.io/badge/python-3.7%2B-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" />
  </p>
</div>

## 📋 Overview

TopCV Job Crawler is a robust Python application designed to efficiently crawl job listings from various job posting sites. Currently, it focuses on [TopCV.vn](https://www.topcv.vn), a major Vietnamese job portal, but features an extensible architecture for adding support for other job sites.

The tool is built with a focus on reliability, configurability, and data consistency, making it suitable for both one-time data extraction and continuous monitoring of job postings.

## ✨ Key Features

- **Multiple Crawling Modes**:
  - 🔄 Continuous mode with configurable intervals
  - 🏃‍♂️ One-time execution mode
  - 🌐 Full crawl of all available pages

- **Robust Implementation**:
  - ⏱️ Rate limiting to respect server resources
  - 🔁 Automatic retries with exponential backoff
  - 🛡️ Proxy support for distributed crawling
  - 🧩 Modular architecture with clean interfaces

- **Data Management**:
  - 💾 Multiple output formats (JSON, CSV)
  - 🔄 Incremental updates to avoid duplicates
  - 📊 Structured data for easy analysis

- **Developer-Friendly**:
  - 📝 Comprehensive logging
  - 🔧 Highly configurable via YAML
  - 🧪 Clean code with separation of concerns

## 🛠️ Tech Stack

- **Core**: Python 3.7+
- **Web Scraping**: BeautifulSoup4, Requests
- **Data Processing**: Pandas
- **Configuration**: PyYAML
- **Scheduling**: Schedule library

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Option 1: Using the Setup Script (Recommended)

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

For Docker deployment:

```bash
# Setup with Docker
./setup.sh --docker

# Build and setup with Docker
./setup.sh --build-docker
```

### Option 2: Manual Installation

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

# Run the container with volumes for data persistence
docker run -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs topcv-job-crawler
```

## 🚀 Usage

### Running the Crawler

```bash
# Run in continuous mode (default)
python crawler.py

# Run once and exit
python crawler.py --once

# Run a full crawl (all pages)
python crawler.py --full

# Specify a custom config file
python crawler.py --config my_config.yaml
```

### Command Line Options

```
python crawler.py --help
```

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to the configuration file (default: config.yaml) |
| `--once`, `-o` | Run once and exit (for development/testing) |
| `--full`, `-f` | Crawl all available pages, not just the configured number |

### Example Commands

```bash
# Development: Run once for testing
python crawler.py --once

# Production: Run with a specific config file
python crawler.py --config production.yaml

# Full data collection: Crawl all pages once
python crawler.py --once --full
```

## ⚙️ Configuration

The crawler is configured through the `config.yaml` file:

```yaml
# Base URL and pagination settings
crawling:
  base_url: "https://www.topcv.vn/tim-viec-lam-moi-nhat"
  pages_to_scan: 3  # Number of pages to scan per cycle
  sleep_interval: 1800  # Time between cycles in seconds (30 minutes)
  timeout: 30  # Request timeout in seconds
  max_retries: 5  # Maximum retries for failed requests
  user_agent: "Mozilla/5.0 ..."

# Proxy settings
proxy:
  enabled: false  # Set to true to enable proxy
  http: ""  # HTTP proxy URL
  https: ""  # HTTPS proxy URL

# Output paths for storing job data
output:
  jobs_json: "data/jobs.json"
  jobs_csv: "data/jobs.csv"
  job_cache_file: "data/job_cache.pkl"  # For deduplication

# Logging configuration
logging:
  log_file: "logs/crawler.log"
  log_level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Runtime configuration
runtime:
  max_runtime: 0  # Maximum runtime in seconds (0 = unlimited)
  daemon_mode: true  # Run continuously in a loop
```

## 📊 Output Data

The crawler generates data files in the `data/` directory:

### Data Format

The job data includes:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier for the job |
| `title` | Job title |
| `company_name` | Name of the hiring company |
| `location` | Job location |
| `salary_min` | Minimum salary (if available) |
| `salary_max` | Maximum salary (if available) |
| `salary_currency` | Currency for salary figures |
| `job_description` | Full job description |
| `job_requirements` | Job requirements and qualifications |
| `job_benefits` | Benefits offered |
| `posting_date` | Date when job was posted |
| `application_deadline` | Deadline for applications |
| `job_url` | URL to the original job posting |
| `crawled_at` | Timestamp when job was crawled |

## 🏗️ Architecture

The crawler follows clean code principles with a modular, extensible architecture:

### Core Components

```
src/
├── core/
│   ├── interfaces.py       # Core interfaces for components
│   ├── crawler_engine.py   # Main crawler orchestration
│   ├── http_client.py      # HTTP client with rate limiting
│   ├── job_crawler.py      # Site-specific crawler implementations
│   ├── pagination.py       # Pagination handling
│   └── storage.py          # Data persistence
├── parser/
│   ├── topcv_parser.py     # TopCV-specific parser
│   ├── details_parser.py   # Job details parsing
│   ├── listing_parser.py   # Job listing parsing
│   ├── html_tools.py       # HTML parsing utilities
│   ├── salary_parser.py    # Salary information parsing
│   └── templates/          # Site-specific HTML templates
├── utils/
│   ├── config.py           # Configuration loading
│   ├── filesystem.py       # File system operations
│   └── signal_handler.py   # Signal handling for graceful shutdown
└── cli/
    └── parser.py           # Command-line argument parsing
```

### Design Patterns Used

- **Strategy Pattern**: Different crawler implementations for different job sites
- **Factory Pattern**: Creates appropriate parser and crawler instances
- **Decorator Pattern**: Implements retry logic for HTTP requests
- **Repository Pattern**: Abstracts data storage operations

## 🔧 Extending

### Adding Support for a New Job Site

1. Create a new crawler implementation in `src/core/job_crawler.py` extending `JobCrawlerBase`
2. Create a parser implementation in `src/parser/` implementing `ParserInterface`
3. Add HTML templates in `src/parser/templates/` if needed
4. Add new crawler and parser to their respective factory functions
5. Update configuration file with site-specific settings

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository on GitHub
2. **Clone** your fork to your local machine
3. **Create a branch** for your feature or bug fix
4. **Make your changes** and commit them
5. **Push** your changes to your fork
6. Submit a **Pull Request** to the main repository

Please ensure your code follows the project's coding style and includes appropriate tests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

For questions or suggestions, please open an issue on the GitHub repository. 