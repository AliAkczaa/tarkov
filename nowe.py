import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MyHandler(FileSystemEventHandler):
    def __init__(self, driver):
        self.driver = driver
        self.button_clicked = False

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Get the path of the folder to watch
        folder_to_watch = os.path.dirname(filepath)
        
        # Delete the previous file, if exists
        delete_previous_file(folder_to_watch)
        
        print(f"New file '{filename}' detected.")
        
        # Automate browser action with the new filename
        self.automate_browser_action(filename)

    def automate_browser_action(self, filename):
        if not self.button_clicked:
            try:
                button = self.driver.find_element(By.XPATH, "//button[text()='Where am i?']")
                button.click()
                self.button_clicked = True
            except Exception as e:
                print(f"Error finding/clicking button: {e}")
                return

        try:
            textbox = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Paste file name here']"))
            )
            textbox.clear()
            textbox.send_keys(filename)
            textbox.send_keys(Keys.ENTER)
            
            # Change marker color
            marker_element = self.driver.find_element(By.CSS_SELECTOR, ".marker")
            self.driver.execute_script("arguments[0].style.backgroundColor = 'red';", marker_element)
            
        except Exception as e:
            print(f"Error during browser interaction: {e}")

def delete_previous_file(folder_path):
    try:
        files = os.listdir(folder_path)
        files.sort(key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
        if len(files) > 1:
            previous_file_path = os.path.join(folder_path, files[0])
            os.remove(previous_file_path)
            print(f"Previous file '{files[0]}' deleted.")
    except Exception as e:
        print(f"Error deleting previous file: {e}")

if __name__ == "__main__":
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")  # Avoid CPU probing errors
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://tarkov-market.com/maps/streets')

    folder_to_watch = r'C:\Users\Ali\Documents\Escape from Tarkov\Screenshots'

    # Initialize the observer and event handler
    event_handler = MyHandler(driver)
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    print(f"Monitoring directory '{folder_to_watch}' for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()
        driver.quit()  # Ensure browser is closed on exit
