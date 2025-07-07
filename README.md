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

3. **Install dependencies** (You may want to define your recipients_list.txt file and your GMail credentials in a .env file at that point)

   ```bash
   . setup.sh
   ```

4. **Run the script** (I personnaly use Cron jobs to ensure the daily scheduling)

   ```bash
   python3 main.py
   ```