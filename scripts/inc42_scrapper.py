
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

from browser_use import Agent, Browser, Controller, ActionResult
from browser_use.llm import ChatGoogle, ChatOpenAI
from utils.otp_utils import get_otp_from_gmail
from prompts.inch42_login_prompt import PROMPT as INC42_PROMPT
GLOBAL_INC42_EMAIL = None
GLOBAL_PASSWORD = None
GLOBAL_OTP_SENDERS = [
    'plus@inc42emails.com'
]

# Initialize the Controller
controller = Controller()

@controller.action('Ask human for OTP', domains=['inc42.com'])
def provide_otp_automatically(question: str) -> ActionResult:
    if GLOBAL_INC42_EMAIL and GLOBAL_PASSWORD:
        print(f"🤖 Agent asked: '{question}'. Attempting to retrieve OTP automatically...")

        otp = get_otp_from_gmail(
            email_address=GLOBAL_INC42_EMAIL,
            password=GLOBAL_PASSWORD,
            valid_senders=GLOBAL_OTP_SENDERS
        )
        if otp:
            print("✅ OTP successfully retrieved automatically.")
            # Return the OTP as extracted content for the agent to use
            return ActionResult(extracted_content=f'The OTP retrieved automatically is: {otp}', include_in_memory=True)
        else:
            # If automatic OTP retrieval fails, inform the user and fall back to manual input
            print("❌ Automatic OTP retrieval failed. Please check your email manually or increase wait time.")
            answer = input(f'{question} > sachin please fill the otp (Automatic retrieval failed)')
            return ActionResult(extracted_content=f'The human responded with OTP: {answer}', include_in_memory=True)
    else:
        # If global credentials are not set, inform the user and request manual input
        print("❌ Email credentials not configured for automatic OTP retrieval. Asking human for OTP.")
        answer = input(f'{question} > sachin please fill the otp')
        return ActionResult(extracted_content=f'The human responded with OTP: {answer}', include_in_memory=True)

class Inc42Scraper:
    def __init__(self, INC42_EMAIL: str, password: str, api_key: str):
        self.INC42_EMAIL = INC42_EMAIL
        self.password = password
        self.api_key = api_key
        self.llm = ChatGoogle(
            model="gemini-2.0-flash-exp", # Using the specified LLM model
            api_key=self.api_key
        )
        # self.llm = ChatOpenAI(
        #     model="gpt-4o-mini",  # Using GPT-4o-mini which supports structured outputs
        #     api_key=self.api_key
        # )

    def get_scraping_prompt(self) -> str:
        formatted_prompt = INC42_PROMPT.format(email=self.INC42_EMAIL)
        print(formatted_prompt,"formatted_prompt")
        return formatted_prompt

    async def scrape(self):
        """
        Executes the scraping process using the browser-use Agent.
        """
        browser = Browser()
        try:
            agent = Agent(
                task=self.get_scraping_prompt(),
                llm=self.llm,
                browser=browser,
                use_vision=True,
                max_actions_per_step=30,
                controller=controller # Pass the configured global controller
            )

            print("🤖 Scraping Inc42 for today's articles...")
            result = await agent.run()
            print("✅ Scraping result:", result)
            print("📦 Raw extracted content:\n", result.extracted_content())
        finally:
            await browser.close() # Ensure the browser is closed even if an error occurs

async def main():
    """
    Main function to set up credentials and initiate the scraping process.
    """

    global GLOBAL_INC42_EMAIL, GLOBAL_PASSWORD

    INC42_EMAIL = os.getenv("GMAIL_EMAIL")
    PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GLOBAL_INC42_EMAIL = INC42_EMAIL
    GLOBAL_PASSWORD = PASSWORD
    # otp = get_otp_from_gmail(
    #     email_address=GLOBAL_INC42_EMAIL,
    #     password=GLOBAL_PASSWORD,
    #     valid_senders=GLOBAL_OTP_SENDERS,
    # )
    # print(f"📧 Retrieved OTP: {otp}")

    scraper = Inc42Scraper(INC42_EMAIL, PASSWORD, GOOGLE_API_KEY)
    await scraper.scrape()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal Error: {e}")

