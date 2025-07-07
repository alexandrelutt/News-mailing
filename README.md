# News-mailing

This project aims to create a system that sends daily news digests via email.

## Installation

To get started, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/alexandrelutt/News-mailing
   cd News
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   python -m nltk.downloader wordnet
   python -m nltk.downloader corpora
   ```

3. **Define your recipients list and your GMail credentials**

4. **Run the script** (I personnaly use Cron jobs to ensure the daily scheduling)

   ```bash
   python3 main.py
   ```