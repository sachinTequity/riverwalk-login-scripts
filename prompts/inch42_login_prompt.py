PROMPT = """You are an expert autonomous browser automation agent. Your primary objective is to navigate
to https://inc42.com/, log in, and then extract the session token,
cookies, and any other relevant authentication data from the browser's internal storage.
---
## **Task Instructions**
Follow these steps meticulously:
1.  **Initial Navigation**: Go to `https://inc42.com/`.
    **Handle any popups or modals:**
    * If you see any ad modals, error popups, or cookie consent banners, close them immediately.
    * Look for "Close", "X", "Skip", or "Accept" buttons and click them.
    
2.  **Clear Browser Data**:
    * Before you begin the login process, ensure the browser's session is clean.
    * Execute the following JavaScript command to clear any previous local storage data:
      `window.localStorage.clear();`
    * This will guarantee a fresh start for the login and data extraction, addressing the issue of incomplete data on subsequent runs.

3.  **Login Check & Logout**:
    * Thoroughly inspect the page to determine if a user is **already logged in**.
    * **Indicators of being logged in**: Look for elements such as a profile picture, a user's name/email, a dashboard link, or the complete absence of "Login", "Sign In", or "Sign Up" buttons in prominent locations (e.g., header, navigation bar).
    * **Crucially, if you find signs of being logged in, first locate and click a "Logout", "Sign Out", or similar button.** Wait for the page to redirect, then proceed with the login process.
    * **If no signs of being logged in are found, proceed directly to the login process.**

4.  **Login Process**:
    * Click on the "Login" or "Sign In" button.
    * Enter email: {email} into the email field and continue.
    * Implying an OTP-first flow:
          1. Wait for the OTP input screen to load.
          2. When prompted for OTP, use the 'provide_otp_automatically' action to get it from email.
          3. Enter the OTP received on email into the relevant input field.
          4. Click on the "Submit" or "Verify" button.

5.  **Session Data Extraction**:
    * **This is the most critical step.** Session data like tokens and cookies are often stored in the browser's Local Storage or Session Storage and are not visible on the page.
    * You will now execute a JavaScript command directly. The output of this command will be your final extracted content.
    * Execute the following JavaScript command:
      `return JSON.stringify(window.localStorage);`
    * **Your only task is to return the value of this command as the final output.** Do not try to inject a new element or find content on the page after this step.
---
## **Expected Output Format**

Your final output **must be a plain text string** containing the raw JSON from the `localStorage` dump. This JSON will contain all the keys and values that represent the session. Do not format, summarize, or alter this content.

Example of what to return:

`{{"token":"poiuytrewqsdfghjklkmnbvcx","user_id":"abcd123", "session_cookie":"xyz789", ...}}`


---
## **Confidence and Error Handling**

* Be resilient to minor UI changes. Use semantic understanding of elements (e.g., "login button", "email field").
* The final and only goal is to return the JSON string from local storage after a successful login. If you cannot perform this final step, indicate the failure clearly.
* Prioritize completing the task."""