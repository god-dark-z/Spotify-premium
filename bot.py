# import
from typing import Callable
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select

from utils import create_account
import logging
import time
import datetime

def parse_cards(filename):
    cards_dict = {}
    with open(filename, "r") as f:
        for indx, card in enumerate(f.readlines()):
            card = card.strip()
            email, password, card_info = card.split(":")
            cards_dict[indx] = {
                "email": email,
                "password": password, 
                "card": card_info
             }
    return cards_dict

    
class SpotifyBot:
    def __init__(
        self,
        card: str,
        is_headless=True,
        address: dict = None,
        email="",
        password="",
        reference="refer-1",
        logger=None
    ):

        self._error_count = 0

        self.CARD_NUMBER = "5424321678968428"
        self.CARD_MONTH = "11"
        self.CARD_YEAR = "25"  # only last part
        self.CARD_CVV = "821"

        if card:
            tokens = card.split("|")
            try:
                self.CARD_NUMBER = tokens[0]
                self.CARD_MONTH = tokens[1]
                # take last 2 digits if not 2 difgigs
                self.CARD_YEAR = tokens[2] if len(tokens[2]) == 2 else tokens[2][-2:]
                self.CARD_CVV = tokens[3]
                self.CARD_CVV = tokens[3]
                self.CARD_CVV = tokens[3]
            except IndexError:
                self.dprint("Invalid card format", "ERROR", logger=logger)
                raise

        if address is None:
            self.address = {
                "street": "220 Cambridge Rd",
                "city": "Clifton Heights",
                "zip": "19018",
                "state": "PA",
            }
        else:
            self.address = address

        self.user_name = "Undefined"

        self.email = email
        self.password = password

        self.is_headless = is_headless
        self.is_address_filled = False

        self.driver = None
        self.log_file_name = (
            f"log_{reference}.txt" if email == "" else f"log_{email}.txt"
        )

        self.setup_driver()

    def setup_driver(self):
        service = Service(ChromeDriverManager(log_level=logging.ERROR).install())
        options = webdriver.ChromeOptions()
        options.headless = self.is_headless
        options.add_argument("--disable-notifications")
        options.add_argument("--mute-audio")
        options.add_argument("--window-size=1100,1000")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            },
        )

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36"
            },
        )

    def dprint(self, string, d="DEBUG", logger: Callable=None):
        if d == "ERROR":
            self._error_count += 1
        print("")
        txt = f"[{d}]: {string}"
        # print(txt)

        if logger:
            logger(txt)
        else:
            with open(self.log_file_name, "a") as f:
                t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{txt} - {t}\n")

    def create_account(self, user_name=None, email=None, password=None, logger=None):
        if not all([user_name, email, password]):
            response, success = create_account(
                self.user_name, self.email, self.password
            )
            if success:
                self.dprint("Account Created!", logger=logger)
                self.email = email
                self.password = password
                return True
            else:
                self.dprint(
                    "Account Creation Failed! Error: \n" + str(response["title"]),
                    "ERROR",
                    logger,
                )
                return False

    def login(self, email, password, logger=None):
        self.dprint("Setting Up login", logger=logger)
        self.email = email
        self.password = password

    def __str__(self):
        return f"{self.__class__.__name__}({self.user_name=},\n{self.email=},\n{self.password=},\n{self.is_headless=},\n{self.is_address_filled=},\n{self._error_count=},\n{self.STREET=},\n{self.CITY=},\n{self.ZIP=},\n{self.STATE=},\n{self.CARD_NUMBER=},\n{self.CARD_MONTH=},\n{self.CARD_YEAR=},\n{self.CARD_CVV=})"

    def __repr__(self):
        return str(self)

    def premify(self, logger):
        self.dprint("Premifying", logger=logger)
        if self.email == "" or self.password == "":
            msg="Login info not found either use 'login' or 'create_account' function"
            self.dprint(
                msg,
                "ERROR",
                logger,
            )
            return False, msg

        start_time = time.perf_counter()

        self.driver.get("https://accounts.spotify.com/en/login")
        self.driver.implicitly_wait(20)
        time.sleep(1)

        try:
            email = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "login-username"))
            )
            password = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "login-password"))
            )
            email.send_keys(self.email)
            password.send_keys(self.password)
            password.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(70)
            time.sleep(2)
            self.dprint("Logged in", logger=logger)
        except Exception as e:
            print("Error: ", e)
            msg = "Failed to Login Cannot find email or password field: "+ str(e)
            self.dprint(msg, "ERROR", logger=logger)
            return False, msg

        self.dprint("Redirecting to Premium Page...", logger=logger)
        self.driver.get(
            "https://www.spotify.com/ca-en/purchase/offer/default-new-family-master-trial-1m/?marketing-campaign-id=default&psp=billing_cards&country=US"
        )
        self.driver.implicitly_wait(25)
        time.sleep(1.6)
        self.driver.refresh()
        self.driver.implicitly_wait(25)
        time.sleep(1.6)

        if not self.is_address_filled:
            try:
                self.driver.implicitly_wait(30)
                street_adds = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, "address-street"))
                )
                addres_city = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, "address-city"))
                )
                zip_code = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.ID, "address-postal_code_short")
                    )
                )
                select = Select(
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.ID, "address-state"))
                    )
                )
                self.driver.implicitly_wait(30)
                time.sleep(0.2)
                street_adds.send_keys(self.address["street"])
                time.sleep(0.2)
                addres_city.send_keys(self.address["city"])
                time.sleep(0.2)
                zip_code.send_keys(self.address["zip"])
                time.sleep(0.2)

                select.select_by_value(self.address["state"])
                self.dprint("Updated Address Info", logger=logger)
            except Exception as e:
                print(str(e))
                self.dprint(
                    "Address fields not found (Maybe it was already there? dont worry it will work)",
                    "ERROR",
                    logger,
                )

        WebDriverWait(self.driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "pci-iframe"))
        )
        card_num = self.driver.find_element(By.ID, "cardnumber")
        ex_date = self.driver.find_element(By.ID, "expiry-date")
        cvv = self.driver.find_element(By.ID, "security-code")

        card_num.send_keys(self.CARD_NUMBER)
        time.sleep(0.3)
        ex_date.send_keys(f"{self.CARD_MONTH}/{self.CARD_YEAR}")
        time.sleep(0.3)
        cvv.send_keys(self.CARD_CVV)

        self.dprint("Updated card info", logger=logger)
        # submit btn
        time.sleep(1)
        cvv.send_keys(Keys.ENTER)

        self.driver.implicitly_wait(20)
        self.dprint("Clicked submit", logger=logger)

        self.driver.implicitly_wait(30)
        self.dprint("Waiting 10 seconds to get results", logger=logger)
        time.sleep(10)
        self.driver.switch_to.default_content()
        # end timer
        end_time = time.perf_counter()

        self.dprint("Time taken (sec/ms): {}".format(end_time - start_time), logger=logger)

        has_error = False
        try:
            err = self.driver.find_element(
                By.CSS_SELECTOR,
                "#__next > main > div > div > section.PaymentSDKWrapperContainer-meydwk-0.cZEmZE > div > div.sc-jcFkyM.ihvgJG > div > p",
            )
            self.dprint(f"Failed to get Premium Account: {err.text.strip()}", "ERROR", logger)
            has_error = True
            self.driver.save_screenshot(f"proof-{self.email}-failed-to-get.png")
        except Exception as e:
            print(str(e))
            print("No Error Found")

        if not has_error:
            self.dprint(f"Premium Done with {self._error_count} Errors", logger=logger)
            self.dprint(
                f"Info: {('=='*20)}\nEmail: {self.email}\nPassword: {self.password}\nUser Name:{self.user_name}",
                logger=logger,
            )
            self.driver.save_screenshot(f"proof-{self.email}.png")
            self.dprint("Screenshot saved", logger=logger)
            return True
        else:
            self.dprint(f"Script Ended with {self._error_count} errors", logger=logger)
            return False
