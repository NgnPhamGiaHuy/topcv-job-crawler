# 🕸️ TopCV Job Crawler

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 📝 Description

TopCV Job Crawler is a powerful Python-based web scraping tool designed to automatically extract job listings from TopCV.vn. The crawler efficiently collects job information, including titles, companies, salaries, and detailed descriptions, storing them in structured formats for further analysis.

Built with scalability and reliability in mind, this tool supports both one-time and continuous crawling operations with configurable parameters to suit different use cases.

## ✨ Features

- Extracts comprehensive job details from TopCV.vn
- Supports both one-time and continuous crawling modes
- Configurable crawling parameters (pages, intervals, timeouts)
- Structured data output in JSON and CSV formats
- Intelligent duplicate detection
- Proxy support for distributed crawling
- Robust error handling and retries
- Detailed logging system
- Docker support for containerized deployment

## ⚙️ Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/NgnPhamGiaHuy/topcv-job-crawler.git
cd topcv-job-crawler

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/NgnPhamGiaHuy/topcv-job-crawler.git
cd topcv-job-crawler

# Build and run with Docker
./setup.sh --build-docker
```

## 🚀 Usage

### Basic Usage

```bash
# Activate the virtual environment (if using standard installation)
source venv/bin/activate

# Run the crawler in daemon mode (continuous crawling)
python crawler.py
```

### Command-line Options

```bash
# Run once and exit
python crawler.py --once

# Perform a full crawl of all available pages
python crawler.py --full

# Specify a custom config file
python crawler.py --config custom_config.yaml
```

### Docker Usage

```bash
# View logs
docker logs -f topcv-job-crawler

# Stop the container
docker stop topcv-job-crawler
```

## 🔧 Configuration

The crawler is highly configurable through the `config.yaml` file:

```yaml
# Base URL and pagination settings
crawling:
  base_url: "https://www.topcv.vn/tim-viec-lam-moi-nhat"
  pages_to_scan: 3  # Number of pages per cycle
  sleep_interval: 1800  # Time between cycles (seconds)

# Proxy settings
proxy:
  enabled: false
  http: ""
  https: ""

# Output paths
output:
  jobs_json: "data/jobs.json"
  jobs_csv: "data/jobs.csv"

# Runtime configuration
runtime:
  max_runtime: 0  # 0 = unlimited
  daemon_mode: true  # Run continuously
```

## 🗂️ Folder Structure

```
├── src/              # Source code
│   ├── cli/          # Command-line interface
│   ├── core/         # Core crawler engine
│   ├── parser/       # HTML parsing modules
│   └── utils/        # Utility functions
├── data/             # Output data directory
├── logs/             # Log files
├── config.yaml       # Configuration file
├── crawler.py        # Entry point
├── requirements.txt  # Python dependencies
├── setup.sh          # Setup script
└── Dockerfile        # Docker configuration
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/your-username/topcv-job-crawler.git

# Create a feature branch
git checkout -b feature/my-feature

# Make your changes
# Commit and push
git commit -m "Add new feature"
git push origin feature/my-feature

# Open a Pull Request
```

## 📄 License

Licensed under the MIT License. See [LICENSE](./LICENSE) for more information.

## 👤 Author

**NgnPhamGiaHuy**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/NgnPhamGiaHuy)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/nguyenphamgiahuy)

## 🙏 Acknowledgements

- Built using Python and BeautifulSoup4
- Inspired by the need for efficient job market data collection
- Thanks to TopCV.vn for providing a structured job listing platform 