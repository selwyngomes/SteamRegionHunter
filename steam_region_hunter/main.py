import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from tabulate import tabulate

driver_path = r"C:\Users\Selly\.wdm\drivers\chromedriver\win64\131.0.6778.204\chromedriver-win32\chromedriver.exe"
output_directory = r"C:\Users\Selly\Documents\SteamRegionHunter"
os.makedirs(output_directory, exist_ok=True)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-logging")
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def clean_price(price, is_ukraine=False, is_discount=False):
    price = price.replace('₴', '').replace('₹', '').replace(',', '').strip().replace(' ', '')
    if price.lower() == "free":
        return "0.00"
    if is_ukraine:
        price = price.split('.')[0]
    try:
        return str(float(price) / 100) if price and price != "N/A" else "N/A"
    except ValueError:
        return "N/A"

def get_game_price_from_steam(store_url, driver):
    driver.get(store_url)
    time.sleep(3)
    try:
        price_element = driver.find_element(By.XPATH, "(//div[contains(@class, 'search_price')])[1]")
        price = price_element.text.strip()
    except:
        return "N/A", "N/A"
    
    price_parts = price.split("\n")
    
    if len(price_parts) >= 2:
        standard_price = price_parts[1]
        discount_price = price_parts[2] if len(price_parts) > 2 else standard_price
    else:
        standard_price = price
        discount_price = price
    
    return standard_price, discount_price

def compare_prices(game_name, driver):
    india_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ', '+')}&cc=in"
    india_price, india_discount_price = get_game_price_from_steam(india_url, driver)
    if india_price == "N/A":
        return None
    ukraine_url = f"https://store.steampowered.com/search/?term={game_name.replace(' ', '+')}&cc=ua"
    ukraine_standard_price, ukraine_discount_price = get_game_price_from_steam(ukraine_url, driver)
    if ukraine_standard_price == "N/A":
        return None
    ukraine_standard_price = clean_price(ukraine_standard_price, is_ukraine=True)
    ukraine_discount_price = clean_price(ukraine_discount_price, is_ukraine=True, is_discount=True)

    standard_converted_price = "N/A"
    discount_converted_price = "N/A"
    if ukraine_standard_price != "N/A":
        standard_converted_price = str(float(ukraine_standard_price) * 2.03)
    if ukraine_discount_price != "N/A":
        discount_converted_price = str(float(ukraine_discount_price) * 2.03)

    difference_standard = "N/A"
    difference_discount = "N/A"
    
    if india_price != "N/A" and standard_converted_price != "N/A":
        try:
            india_price_float = float(india_price.replace('₹', '').replace(',', '').strip())
            difference_standard = f"₹{india_price_float - float(standard_converted_price):,.2f}"
        except ValueError:
            difference_standard = "N/A"
    
    if india_discount_price != "N/A" and discount_converted_price != "N/A":
        try:
            india_discount_float = float(india_discount_price.replace('₹', '').replace(',', '').strip())
            difference_discount = f"₹{india_discount_float - float(discount_converted_price):,.2f}"
        except ValueError:
            difference_discount = "N/A"
    
    return {
        "Game Name": game_name,
        "Standard Price (India)": india_price,
        "Discount Price (India)": india_discount_price,
        "Standard Price (Ukraine)": f'₴{float(ukraine_standard_price):,.2f}' if ukraine_standard_price != "N/A" else "N/A",
        "Standard Converted Price (Ukraine)": f'₹{float(standard_converted_price):,.2f}' if standard_converted_price != "N/A" else "N/A",
        "Difference (Standard)": difference_standard,
        "Discount Price (Ukraine)": f'₴{float(ukraine_discount_price):,.2f}' if ukraine_discount_price != "N/A" else "N/A",
        "Discount Converted Price (Ukraine)": f'₹{float(discount_converted_price):,.2f}' if discount_converted_price != "N/A" else "N/A",
        "Difference (Discount)": difference_discount
    }

def create_output_files(results):
    df = pd.DataFrame(results, columns=["Game Name", "Standard Price (India)", "Discount Price (India)", 
                                        "Standard Price (Ukraine)", "Standard Converted Price (Ukraine)", 
                                        "Difference (Standard)", "Discount Price (Ukraine)", 
                                        "Discount Converted Price (Ukraine)", "Difference (Discount)"])
    output_file_path = os.path.join(output_directory, "steamrgnhntr.xlsx")
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    df.to_excel(output_file_path, index=False)

def print_table(results):
    print("\nGame Price Comparison Results:\n")
    print(tabulate(results, headers='keys', tablefmt='pretty', showindex=False))

def main():
    print("Welcome to the Steam Region Hunter!")
    print("Please enter the names of the Games you want to compare (comma-separated).")
    games = [game.strip() for game in input("Enter Game Names: ").split(',')]
    results = []
    driver = setup_driver()
    print("\nLoading prices... Please wait.")
    for game in tqdm(games, desc="Fetching game prices", ncols=100):
        result = compare_prices(game, driver)
        if result:
            results.append(result)
    create_output_files(results)
    print("\nResults have been successfully saved in the Excel file!")
    print_table(results)
    driver.quit()

if __name__ == "__main__":
    main()