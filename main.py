from datetime import datetime, timedelta
from time import sleep
from playwright.sync_api import sync_playwright
import json


def click_input(tab, input, test = False):
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
    # Load settings from the JSON file
    with open("settings.json", "r") as file:
        settings = json.load(file)


    # Start Playwright
    playwright = sync_playwright().start()

    # Launch a browser (headless=False opens a visible browser)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()  # Shared browser context
    page = context.new_page()

    # Open the website
    page.goto("https://bach.wu.ac.at/mywu/")

    # Click the link
    with page.expect_popup() as popup_info:
        page.click("a:text('LPIS - Anmeldung für LVs & Prüfungen')")

    new_tab = popup_info.value


    course_name = settings.get("course_name")
    course_id = settings.get("course_id")
    target_time = settings.get("time")
    is_test = settings.get("is_test")

    target_time = datetime.strptime(target_time, "%H:%M").time()


    # Wait for the new tab to load
    # new_tab.wait_for_load_state("networkidle") # Wait for the network to be idle
    new_tab.locator("//td[text()='Matrikelnummer']/following-sibling::td/input").fill(settings.get("login"))
    new_tab.locator("//td[text()='Accountpasswort']/following-sibling::td/input").fill(settings.get("password"))
    new_tab.locator("input[value='Login']").click()
    new_tab.click(f"//span[text()='{course_name}']/following::a[text()='VUE anmelden'][1]")


    # Wait until the specified time
    wait_until(target_time)

    print("Refreshing the page...")
    new_tab.reload()



    # Locate the anmelden button name in the row with the course_id
    anmelden_button = new_tab.locator(f"//table[@class='b3k-data']//tr[td[@class='ver_id']/a[text()='{course_id}']]//td[@class='action']/form/input[@value='anmelden']")
    while anmelden_button.get_attribute("disabled") and not is_test:
        print("The anmelden button is disabled. Waiting for 1 second and refreshing the page...")
        sleep(1)
        new_tab.reload()
        anmelden_button = new_tab.locator(f"//table[@class='b3k-data']//tr[td[@class='ver_id']/a[text()='{course_id}']]//td[@class='action']/form/input[@value='anmelden']")


    click_input(new_tab, anmelden_button, is_test)





    # Keep the browser open for debugging
    input("Press Enter to exit...")



# Run the bot
if __name__ == "__main__":
    try: 
        run_bot()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
