# Ken Article Scraper

This project contains various web scrapers for different news websites and platforms.

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Email credentials
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# API Keys
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Website specific passwords
ECONOMIC_TIMES_PASSWORD=your_economic_times_password
CAPTABLE_PASSWORD=your_captable_password
```

### 3. Setting up Gmail App Password

For the Gmail app password:

1. Go to your Google Account settings
2. Enable 2-factor authentication
3. Generate an App Password for this application
4. Use that 16-character password in `GMAIL_APP_PASSWORD`

### 4. API Keys

- **Google API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## Available Scrapers

- `inc42_scrapper.py` - Inc42 articles
- `ken_scraper.py` - The Ken articles
- `ET_scrapper.py` - Economic Times articles
- `livemint_scraper.py` - LiveMint articles
- `captable_scrapper.py` - CapTable articles
- `the_morning_context_scrapper.py` - The Morning Context articles
- `vccircle_scrapper.py` - VCCircle articles

## Usage

Run any scraper with:

```bash
python scripts/script_name.py
```

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already added to `.gitignore`
- Use `.env.example` as a template for your own `.env` file
