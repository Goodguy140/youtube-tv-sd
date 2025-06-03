import pygame
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--user-data-dir=./chrome-profile") # Store Chrome profile in the current directory
options.add_argument("--kiosk") 
options.add_argument("--disable-infobars")
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument("--disable-features=MediaEngagementBypassAutoplayPolicies")
options.add_argument(
    "--user-agent=Mozilla/5.0 (PS4; Leanback Shell) Cobalt/24.lts.13.1032728-gold "
    "v8/8.8.278.8-jit gles Starboard/14, SystemIntegratorName_PS4_ChipsetModelNumber_2024/"
    "FirmwareVersion (Sony, PS4, Wired)"
)
# Initialize the Chrome WebDriver with the specified options
driver = webdriver.Chrome(options=options)
driver.get("https://www.youtube.com/tv")

wait = WebDriverWait(driver, 15)
body = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))

# --- Initialize Pygame for controller input ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() >= 1: # If at least one joystick is connected, initialize it
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Connected joystick on launch: {joystick.get_name()}")

# --- Controller button mappings ---
BUTTON_CROSS = 0  # PS4 Cross (A equivalent) - Select / Play-Pause
BUTTON_CIRCLE = 1 # PS4 Circle - Back / Exit

def press_key(key):
    # Send a key press to the browser
    body.send_keys(key)

def detect_close(driver):
    seen_entries = set()
    logs = driver.get_log('browser')
    for entry in logs[-5:]:  # Only check the last 5 log lines
            msg = entry['message']
            if msg in seen_entries:
                continue
            seen_entries.add(msg)
            if "Scripts may close only the windows that were opened by them." in msg:
                print("Close attempt detected.")
                return True
    time.sleep(0.01)
    return False

# --- Main loop to handle controller input ---
try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                joystick.init()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_CROSS:
                    press_key(Keys.ENTER)
                elif event.button == BUTTON_CIRCLE:
                    press_key(Keys.ESCAPE) # Back / Exit   
                elif event.button == 3: # Square
                    press_key(Keys.BACKSPACE)
                elif event.button == 4: #Triangle
                    press_key("s") # Search
                elif event.button == 6: # L1
                    press_key("h")
                elif event.button == 7: # R1
                    press_key(Keys.SEMICOLON)
            elif event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == 1:
                    press_key(Keys.ARROW_UP)
                elif hat_y == -1:
                    press_key(Keys.ARROW_DOWN)
                if hat_x == 1:
                    press_key(Keys.ARROW_RIGHT)
                elif hat_x == -1:
                    press_key(Keys.ARROW_LEFT)
            elif event.type == pygame.JOYAXISMOTION:
                axis_x = joystick.get_axis(0)
                axis_y = joystick.get_axis(1)
                if abs(axis_x) > 0.75:
                    if axis_x > 0:
                        press_key(Keys.ARROW_RIGHT)
                    else:
                        press_key(Keys.ARROW_LEFT)
                if abs(axis_y) > 0.75:
                    if axis_y > 0:
                        press_key(Keys.ARROW_DOWN)
                    else:
                        press_key(Keys.ARROW_UP)
        # Check for close attempts
        # and quit if detected
        if detect_close(driver):
            driver.quit()
            pygame.quit()
        time.sleep(0.06)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    driver.quit()
    pygame.quit()
