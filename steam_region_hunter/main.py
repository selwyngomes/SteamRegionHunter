import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm
from tabulate import tabulate
from difflib import SequenceMatcher
import unidecode
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

@dataclass
class GamePrice:
    title: str
    standard_price: str
    discount_price: str

class SteamRegionHunter:
    def __init__(self, driver_path: str, output_directory: str):
        self.driver_path = driver_path
        self.output_directory = output_directory
        self.setup_logging()
        
    def setup_logging(self):
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        log_file_path = os.path.join(self.output_directory, f"SteamRegLogs-{timestamp}.txt")
        
        logging.basicConfig(
            filename=log_file_path,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='w'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger('').addHandler(console_handler)

    @staticmethod
    def setup_chrome_options() -> Options:
        chrome_options = Options()
        options = [
            "--headless", "--disable-gpu", "--no-sandbox", "--log-level=3",
            "--disable-dev-shm-usage", "--disable-extensions",
            "--window-size=1920,1080", "--disable-logging"
        ]
        for option in options:
            chrome_options.add_argument(option)
        return chrome_options

    def create_driver(self) -> webdriver.Chrome:
        service = Service(self.driver_path)
        return webdriver.Chrome(service=service, options=self.setup_chrome_options())

    @staticmethod
    def similar(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    @staticmethod
    def normalize_title(title: str) -> str:
        # Convert Roman numerals to Arabic numbers
        roman_map = {
            'VII': '7', 'VIII': '8', 'VI': '6', 'IV': '4', 'V': '5',
            'III': '3', 'II': '2', 'I': '1', 'IX': '9', 'X': '10'
        }
        title = title.upper()
        for roman, arabic in roman_map.items():
            title = title.replace(roman, arabic)
            
        # Remove special characters and normalize
        title = unidecode.unidecode(title).replace("'", "'").replace("®", "")
        # Remove common suffixes and prefixes
        title = re.sub(r'\b(HD|REMASTER|DEFINITIVE EDITION|DELUXE|STANDARD|EDITION)\b', '', title, flags=re.IGNORECASE)
        return title.strip()

    @staticmethod
    def clean_price(price: str, is_ukraine: bool = False, is_discount: bool = False) -> str:
        price = price.replace('₴', '').replace('₹', '').replace(',', '').strip().replace(' ', '')
        if price.lower() == "free":
            return "0.00"
        if is_ukraine:
            price = price.split('.')[0]
        try:
            return str(round(float(price) / 100, 2)) if price and price != "N/A" else "N/A"
        except ValueError:
            return "N/A"

    def get_game_price_from_steam(self, store_url: str, driver: webdriver.Chrome, 
                                game_name: str) -> GamePrice:
        logging.info(f"Searching for '{game_name}' at URL: {store_url}")
        try:
            driver.get(store_url)
            wait = WebDriverWait(driver, 10)
            
            titles = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//span[contains(@class, 'title')]")))
            prices = driver.find_elements(By.XPATH, "//div[contains(@class, 'search_price')]")

            if not titles or not prices:
                logging.warning(f"No results found for '{game_name}'.")
                return GamePrice("N/A", "N/A", "N/A")

            best_match, best_idx = self._find_best_match(titles, game_name)
            if not best_match:
                return GamePrice("N/A", "N/A", "N/A")

            return self._extract_prices(prices[best_idx], best_match)

        except Exception as e:
            logging.error(f"Error fetching price for '{game_name}': {str(e)}", exc_info=True)
            return GamePrice("N/A", "N/A", "N/A")

    def _find_best_match(self, titles: List, game_name: str) -> Tuple[Optional[str], int]:
        best_match = None
        best_idx = -1
        highest_similarity = 0
        
        normalized_game_name = self.normalize_title(game_name)
        logging.debug(f"Normalized search game name: {normalized_game_name}")
        
        for idx, title in enumerate(titles):
            title_text = self.normalize_title(title.text.strip())
            logging.debug(f"Normalized title: {title_text}")
            
            # Check for exact matches first
            if title_text.lower() == normalized_game_name.lower():
                return title_text, idx
                
            similarity = self.similar(title_text, normalized_game_name)
            logging.debug(f"Comparing '{title_text}' with '{normalized_game_name}' - Similarity: {similarity}")
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = title_text
                best_idx = idx
                logging.debug(f"New best match found: '{best_match}' with similarity {similarity}")

        # Lower the similarity threshold
        if highest_similarity < 0.65:  # Changed from 0.80 to 0.65
            logging.warning(f"No sufficiently similar match found for '{game_name}'. Best similarity was {highest_similarity}")
            return None, -1

        # Check if main keywords are present
        key_words = [word.lower() for word in normalized_game_name.split() if len(word) > 2]
        key_words = [word for word in key_words if word not in ['the', 'and', 'for', 'of']]
        logging.debug(f"Key words to match: {key_words}")
        
        if not any(word in best_match.lower() for word in key_words):
            logging.warning(f"Match '{best_match}' does not contain key words from '{game_name}'.")
            return None, -1

        logging.info(f"Final match for '{game_name}': '{best_match}' with similarity {highest_similarity}")
        return best_match, best_idx

    def _extract_prices(self, price_element: webdriver.Remote, game_name: str) -> GamePrice:
        price = price_element.text.strip()
        logging.debug(f"Raw price text for '{game_name}': {price}")
        
        price_parts = price.split("\n")
        logging.debug(f"Price parts: {price_parts}")

        if len(price_parts) >= 2:
            standard_price = price_parts[1]
            discount_price = price_parts[2] if len(price_parts) > 2 else standard_price
        else:
            standard_price = discount_price = price

        logging.info(f"Extracted prices for '{game_name}': Standard={standard_price}, Discount={discount_price}")
        return GamePrice(game_name, standard_price, discount_price)

    def compare_prices(self, game_name: str, driver: webdriver.Chrome) -> Optional[Dict]:
        base_url = "https://store.steampowered.com/search/?term={}&cc={}"
        india_url = base_url.format(game_name.replace(' ', '+'), 'in')
        ukraine_url = base_url.format(game_name.replace(' ', '+'), 'ua')

        india_data = self.get_game_price_from_steam(india_url, driver, game_name)
        if india_data.standard_price == "N/A":
            logging.warning(f"Game '{game_name}' not found in India region.")
            return None

        ukraine_data = self.get_game_price_from_steam(ukraine_url, driver, game_name)
        
        return self._calculate_price_differences(game_name, india_data, ukraine_data)

    def _calculate_price_differences(self, game_name: str, india_data: GamePrice, 
                                   ukraine_data: GamePrice) -> Dict:
        ukraine_standard = self.clean_price(ukraine_data.standard_price, is_ukraine=True)
        ukraine_discount = self.clean_price(ukraine_data.discount_price, is_ukraine=True, 
                                          is_discount=True)

        standard_converted = self._convert_price(ukraine_standard)
        discount_converted = self._convert_price(ukraine_discount)

        india_standard = india_data.standard_price.replace('₹', '').replace(',', '').strip()
        india_discount = india_data.discount_price.replace('₹', '').replace(',', '').strip()

        return {
            "Game Name": game_name,
            "Standard Price (India)": india_standard,
            "Discount Price (India)": india_discount,
            "Standard Price (Ukraine)": ukraine_standard,
            "Standard Converted Price (Ukraine)": standard_converted,
            "Difference (Standard)": self._calculate_difference(india_standard, standard_converted),
            "Discount Price (Ukraine)": ukraine_discount,
            "Discount Converted Price (Ukraine)": discount_converted,
            "Difference (Discount)": self._calculate_difference(india_discount, discount_converted)
        }

    @staticmethod
    def _convert_price(price: str, conversion_rate: float = 2.03) -> str:
        try:
            return str(round(float(price) * conversion_rate, 2)) if price != "N/A" else "N/A"
        except ValueError:
            return "N/A"

    @staticmethod
    def _calculate_difference(india_price: str, ukraine_price: str) -> str:
        try:
            if india_price != "N/A" and ukraine_price != "N/A":
                return str(round(float(india_price) - float(ukraine_price), 2))
            return "N/A"
        except ValueError:
            return "N/A"

    def create_output_files(self, results: List[Dict]):
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        output_file = os.path.join(self.output_directory, f"SteamRegHun-{timestamp}.xlsx")
        
        df = pd.DataFrame(results)
        numeric_columns = [col for col in df.columns if col != "Game Name"]
        
        for column in numeric_columns:
            df[column] = df[column].replace({',': '', 'Free': '0', 'N/A': '0'}, regex=True).astype(float)

        totals = df[numeric_columns].sum()
        totals_row = pd.DataFrame([{"Game Name": "Total", **totals}])
        df = pd.concat([df, totals_row], ignore_index=True)
        
        df.to_excel(output_file, index=False)
        logging.info(f"Results saved to {output_file}")

    @staticmethod
    def print_table(results: List[Dict]):
        print("\nGame Price Comparison Results:\n")
        print(tabulate(results, headers='keys', tablefmt='pretty', showindex=False))

        df = pd.DataFrame(results)
        numeric_columns = [col for col in df.columns if col != "Game Name"]
        for column in numeric_columns:
            df[column] = df[column].replace({',': '', 'Free': '0', 'N/A': '0'}, 
                                          regex=True).astype(float)
        
        totals = df[numeric_columns].sum()
        print("\nTotal Summary:\n")
        for column, total in totals.items():
            print(f"{column}: {total:.2f}")

def main():
    output_directory = r"C:\Users\Selly\Documents\SteamRegionHunter"
    os.makedirs(output_directory, exist_ok=True)
    
    hunter = SteamRegionHunter(
        driver_path=r"C:\Users\Selly\.wdm\drivers\chromedriver\win64\131.0.6778.204\chromedriver-win32\chromedriver.exe",
        output_directory=output_directory
    )

    print("Welcome to the Steam Region Hunter!")
    games = [game.strip() for game in input("Enter Game Names (comma-separated): ").split(',')]
    
    results = []
    with hunter.create_driver() as driver:
        for game in tqdm(games, desc="Fetching game prices", ncols=100):
            game_data = hunter.compare_prices(game, driver)
            if game_data:
                results.append(game_data)

    hunter.create_output_files(results)
    hunter.print_table(results)

if __name__ == "__main__":
    main()
