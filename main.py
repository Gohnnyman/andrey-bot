from datetime import datetime, timedelta
from time import sleep
from playwright.sync_api import sync_playwright, TimeoutError
import json


def click_input(tab, input, test=False):
    if test:
        # Inject CSS to highlight only the specific button
        tab.evaluate("""
            (button) => {
                button.style.border = '2px solid red';
                button.style.backgroundColor = 'yellow';
            }
        """, input.element_handle())
    else:
        input.click()


def wait_until(target_time):
    """
    Waits precisely until the specified target_time on the same day.
    If the target_time has already passed, the function returns immediately.
    """
    now = datetime.now()
    current_time = now.time()

    # If the target time has already passed, return immediately
    if current_time >= target_time:
        print(f"The target time {target_time} has already passed.")
        return

    # Calculate the time difference between now and the target time
    target_datetime = datetime.combine(now.date(), target_time)
    remaining_time = (target_datetime - now).total_seconds()

    print(f"Waiting for {remaining_time:.3f} seconds until {target_time}...")

    # Sleep for the remaining time minus a small buffer
    if remaining_time > 0:
        sleep(remaining_time)  # Sleep until the target time

    # Busy-wait for the last few milliseconds to ensure precision
    while datetime.now() < target_datetime:
        pass  # Busy-wait loop for final precision


def run_bot():
    # Load settings from the JSON file with UTF-8 encoding
    with open("settings.json", "r", encoding="utf-8") as file:
        settings = json.load(file)


    # Start Playwright
    playwright = sync_playwright().start()

    # Launch a browser (headless=False opens a visible browser)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()  # Shared browser context
    page = context.new_page()

    # Open the website
    print("Navigating to the website...")
    page.goto("https://bach.wu.ac.at/mywu/", timeout=60000)  # Wait up to 60 seconds for the page to load

    # Click the link and handle pop-up
    try:
        print("Clicking the LPIS link and waiting for the popup...")
        with page.expect_popup() as popup_info:
            page.click("a:text('LPIS - Anmeldung für LVs & Prüfungen')", timeout=30000)  # Wait for the click to trigger the popup
        new_tab = popup_info.value
        new_tab.wait_for_load_state("domcontentloaded", timeout=60000)  # Ensure the new tab is fully loaded
    except TimeoutError:
        print("Failed to load the LPIS popup. Exiting.")
        return

    course_name = settings.get("course_name")
    course_id = settings.get("course_id")
    target_time = settings.get("time")
    is_test = settings.get("is_test", False)

    target_time = datetime.strptime(target_time, "%H:%M").time()

    # Login process
    print("Filling in login credentials...")
    new_tab.locator("//td[text()='Matrikelnummer']/following-sibling::td/input").fill(settings.get("login"), timeout=30000)
    new_tab.locator("//td[text()='Accountpasswort']/following-sibling::td/input").fill(settings.get("password"), timeout=30000)
    new_tab.locator("input[value='Login']").click()
    new_tab.wait_for_load_state("networkidle", timeout=60000)  # Wait for the login process to complete

    # Navigate to the course
    print(f"Navigating to the course: {course_name}...")
    new_tab.click(f"//span[text()='{course_name}']/following::a[1]", timeout=30000)
    new_tab.wait_for_load_state("networkidle", timeout=60000)

    # Wait until the specified time
    wait_until(target_time)

    # Refresh the page
    print("Refreshing the page...")
    new_tab.reload(wait_until="networkidle", timeout=60000)
    new_tab.wait_for_load_state("networkidle", timeout=60000)  # Wait for the login process to complete

    # Locate the "anmelden" button
    print(f"Locating the 'anmelden' button for course ID {course_id}...")
    anmelden_button = new_tab.locator(
        f"//table[@class='b3k-data']//tr[td[@class='ver_id']/a[text()='{course_id}']]//td[@class='action']/form/input[@value='anmelden']"
    )

    # Check if the button is enabled
    while anmelden_button.get_attribute("disabled") and not is_test:
        print("The 'anmelden' button is disabled. Waiting for 1 second and refreshing the page...")
        sleep(1)
        new_tab.reload(wait_until="networkidle", timeout=60000)
        anmelden_button = new_tab.locator(
            f"//table[@class='b3k-data']//tr[td[@class='ver_id']/a[text()='{course_id}']]//td[@class='action']/form/input[@value='anmelden']"
        )

    # Click the button or highlight it
    click_input(new_tab, anmelden_button, is_test)

    print("Action completed successfully.")

    # Keep the browser open for debugging
    input("Press Enter to exit...")


# Run the bot
if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
