import pygame
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# A Python Script to control Youtube TV using a Controller. Can be used on SteamDeck or Desktop.
options = Options()
# add data directory for Chrome to store user data
options.add_argument("--user-data-dir=./chrome-profile")
options.add_argument("--start-fullscreen")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--autoplay-policy=no-user-gesture-required")
options.add_argument("--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies")
options.add_argument(
    "--user-agent=Mozilla/5.0 (PS4; Leanback Shell) Cobalt/24.lts.13.1032728-gold "
    "v8/8.8.278.8-jit gles Starboard/14, SystemIntegratorName_PS4_ChipsetModelNumber_2024/"
    "FirmwareVersion (Sony, PS4, Wired)"
)

driver = webdriver.Chrome(options=options)
driver.get("https://www.youtube.com/tv")

wait = WebDriverWait(driver, 15)
body = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))


# --- Initialize Pygame and Joystick ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No gamepad detected. Please connect a controller and restart.")
    driver.quit()
    pygame.quit()
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Connected joystick: {joystick.get_name()}")

# --- Controller button mappings ---
BUTTON_CROSS = 0  # PS4 Cross (A equivalent) - Select / Play-Pause
BUTTON_CIRCLE = 1 # PS4 Circle - Back / Exit

def press_key(key):
    """Send keypress event to Selenium."""
    body.send_keys(key)
    print(f"Sent key: {key}")

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

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == BUTTON_CROSS:
                    press_key(Keys.ENTER)
                elif event.button == BUTTON_CIRCLE:
                    press_key(Keys.ESCAPE)
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
        if detect_close(driver):
            driver.quit()
            pygame.quit()
        time.sleep(0.05)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    driver.quit()
    pygame.quit()
