from time import sleep
from playwright.sync_api import sync_playwright
import json


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

    # Wait for the new tab to load
    # new_tab.wait_for_load_state("networkidle") # Wait for the network to be idle
    new_tab.locator("//td[text()='Matrikelnummer']/following-sibling::td/input").fill(settings.get("login"))
    new_tab.locator("//td[text()='Accountpasswort']/following-sibling::td/input").fill(settings.get("password"))
    new_tab.locator("input[value='Login']").click()
    new_tab.click(f"//span[text()='{course_name}']/following::a[text()='VUE anmelden'][1]")


    # Locate the lector's name in the row with 5738
    anmelden_button = new_tab.locator(f"//table[@class='b3k-data']//tr[td[@class='ver_id']/a[text()='{course_id}']]//td[@class='action']/form/input[@value='anmelden']")


    # Inject CSS to highlight only the specific button
    new_tab.evaluate("""
        (button) => {
            button.style.border = '2px solid red';
            button.style.backgroundColor = 'yellow';
        }
    """, anmelden_button.element_handle())




    # Keep the browser open for debugging
    input("Press Enter to exit...")

    # Stop Playwright
    # playwright.stop()


# Run the bot
if __name__ == "__main__":

    run_bot()
