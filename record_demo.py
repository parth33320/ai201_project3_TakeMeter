import os
import time
import subprocess
import socket
from playwright.sync_api import sync_playwright

def slow_scroll(page, target_selector, duration_seconds):
    """
    Smoothly scrolls to the target selector over a given duration.
    """
    # Get current scroll position and target position
    current_scroll = page.evaluate("window.scrollY")
    target_element = page.locator(target_selector)
    target_scroll = target_element.evaluate("el => el.getBoundingClientRect().top + window.scrollY")

    # Calculate steps (approx 60fps)
    steps = int(duration_seconds * 60)
    if steps == 0: return

    increment = (target_scroll - current_scroll) / steps

    for _ in range(steps):
        current_scroll += increment
        page.evaluate(f"window.scrollTo(0, {current_scroll})")
        time.sleep(1/60)

def record_demo():
    gradio_process = None
    try:
        # 1. Start Gradio server
        print("Starting Gradio server...")
        gradio_process = subprocess.Popen(["python3", "app.py"])

        # Wait for the port to be active
        print("Waiting for Gradio to start...")
        max_retries = 30
        for i in range(max_retries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 7860)) == 0:
                    print("Gradio is up!")
                    break
            time.sleep(1)
        else:
            print("Gradio failed to start.")
            return

        with sync_playwright() as p:
            # 2. Launch browser with video recording
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir="videos/"
            )
            page = context.new_page()

            # --- Part 1: README Walkthrough ---
            print("Starting README walkthrough...")
            readme_path = "file://" + os.path.abspath("README.html")
            page.goto(readme_path)
            # Set zoom to 125% for better visibility
            page.evaluate("document.body.style.zoom = '1.25'")
            time.sleep(2)

            # Slow scroll to Inter-Annotator Reliability (20 seconds)
            print("Scrolling to Inter-Annotator Reliability...")
            slow_scroll(page, "h2:has-text('1. Inter-Annotator Reliability')", 5)
            time.sleep(15) # Total 20s

            # Slow scroll to Confidence Calibration (20 seconds)
            print("Scrolling to Confidence Calibration Analysis...")
            slow_scroll(page, "h2:has-text('2. Confidence Calibration Analysis')", 5)
            time.sleep(15) # Total 20s

            # --- Part 2: Live Classification Demo ---
            print("Starting Gradio demo...")
            page.goto("http://127.0.0.1:7860")
            page.evaluate("document.body.style.zoom = '1.25'")

            # Wait for Gradio to load
            page.wait_for_selector('textarea[placeholder="Enter a comment here..."]', timeout=30000)

            posts = [
                "Online 'fan theories' that are simply the basic, explicit plot points of the movie.",
                "I’m a nanny and I’ve worked with 9 year olds who are in school full time yet can barely get through a book meant for a kindergarten reading level.",
                "Where people in the future are brain dead zombies who want for nothing, but don't know anything or how to do anything but be food for the Morlocks.",
                "College programs adding two levels of remedial math previously unnecessary for entry.",
                "It was the iPad, almost entirely. Easily the most destructive experiment inflicted on children since thalidomide."
            ]

            for post in posts:
                print(f"Processing post: {post[:50]}...")

                # Clear previous inputs to make transition distinct
                page.fill('textarea[placeholder="Enter a comment here..."]', "")
                time.sleep(1)

                # Fill the post
                page.fill('textarea[placeholder="Enter a comment here..."]', post)
                time.sleep(1)

                # Click Predict
                page.click('button:has-text("Predict")')

                # Wait for output to be updated (using a trick to ensure it's the NEW value)
                # For simplicity in this simulated environment, we'll just wait for the non-empty value
                # but with the 'clear' step above, it's more distinct.
                page.wait_for_function(
                    'Array.from(document.querySelectorAll("label")).find(el => el.textContent.includes("Predicted Label"))?.parentElement.querySelector("textarea")?.value !== ""',
                    timeout=10000
                )

                # 15 seconds per post for narration sync
                time.sleep(13) # minus the clear/fill time

            # Cleanup browser
            context.close()
            browser.close()

            # Identify the recording and move it
            video_path = page.video.path()
            print(f"Moving video from {video_path} to demo_video.webm")
            os.rename(video_path, "demo_video.webm")

    finally:
        if gradio_process:
            print("Terminating Gradio server...")
            gradio_process.terminate()
            gradio_process.wait()
            print("Gradio server terminated.")

if __name__ == "__main__":
    if not os.path.exists("videos"):
        os.makedirs("videos")
    record_demo()
