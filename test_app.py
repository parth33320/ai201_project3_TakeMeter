import os
import time
import subprocess
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def gradio_server():
    # Start the Gradio app in the background
    process = subprocess.Popen(["python3", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the server to start (Gradio usually starts on 7860)
    time.sleep(10)

    yield "http://127.0.0.1:7860"

    # Cleanup
    process.terminate()

def test_gradio_interface(gradio_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(gradio_server)

        # Wait for the interface to load
        page.wait_for_selector('textarea[placeholder="Enter a comment here..."]', timeout=30000)

        # Fill in a sample text
        page.fill('textarea[placeholder="Enter a comment here..."]', "The students cannot read analog clocks.")

        # Click the 'Submit' button
        submit_button = page.get_by_role("button", name="Submit")
        submit_button.click()

        # Wait for the output to appear
        # Using a more robust way to find the label text in a cross-browser compatible way
        page.wait_for_function(
            'Array.from(document.querySelectorAll("label")).find(el => el.textContent.includes("Predicted Label"))?.parentElement.querySelector("textarea")?.value !== ""',
            timeout=10000
        )

        label_val = page.locator('label:has-text("Predicted Label")').locator("..").locator("textarea").input_value()
        conf_val = page.locator('label:has-text("Confidence Score")').locator("..").locator("textarea").input_value()

        assert label_val in ["professional_obs", "emotional_reaction", "systemic_critique"]
        assert float(conf_val) > 0

        browser.close()

if __name__ == "__main__":
    # This allows running the test script directly if desired
    pytest.main([__file__])
