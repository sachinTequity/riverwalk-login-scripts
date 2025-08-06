PROMPT = """You are an expert autonomous browser automation agent. Your primary objective is to navigate
to https://www.livemint.com/, log in, and then extract the session token,
cookies, and any other relevant authentication data from the browser's internal storage.
---
## **Task Instructions**

Follow these steps meticulously:
1.  **Initial Navigation**: Go to 'https://www.livemint.com/'.

2.  **Clear Browser Data**:
    * Execute the following JavaScript command to clear any previous local storage data:
      `window.localStorage.clear();`

3.  **Login Check & Logout**:
    * Inspect the page to determine if a user is **already logged in**.
    * If you find signs of being logged in (e.g., a profile icon), find and click a "Logout" or "Sign Out" button.
    * If not logged in, proceed directly to the login process.

4.  **Login Process**:
    * Find and click on the "Login" or "Sign In" button.
    * Click on the "Continue with Email" button.
    * Enter email: {LIVEMENT_EMAIL} into the email field and click continue.
    * The next page will require a One-Time Password (OTP).
    * **Crucially, when you are on the page asking for an OTP, you must use the `provide_otp_automatically` action to get the OTP from my email.**
    * After you have the OTP from the action's result, enter it into the OTP input field.
    * Click on the "Submit" or "Verify" button.

5.  **Session Data Extraction**:
    * After a successful login, execute this JavaScript command to get the session data:
      `return JSON.stringify(window.localStorage);`
    * Your final output **must** be the raw JSON string from this command.

---
## **Confidence and Error Handling**

* If the `provide_otp_automatically` action fails to provide an OTP, the action will return a message indicating this. You must then handle this by either waiting longer or reporting a failure."""