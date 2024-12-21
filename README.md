
# Steam Region Hunter

**Steam Region Hunter** is a Python-based utility that allows users to compare game prices between two Steam regions: India and Ukraine. It retrieves real-time pricing information using Selenium and displays the results in a tabular format on the command line, as well as saves them to an Excel file. The utility provides several powerful features:

## Features

**1. Real-time Price Comparison:**

- Fetches and compares standard and discounted prices for games between Steam India and Steam Ukraine.

**2. Price Conversion:**

- Converts Ukrainian prices into Indian Rupees for easier comparison.

**3. Difference Calculation:**

- Calculates and displays the difference between Indian prices and converted Ukrainian prices for both standard and discounted prices.

**4. Excel File Export:**

- Saves the results to an Excel file, including all calculated fields (converted prices and differences).

**5. Tabular CLI Output:**

- Displays the results in a well-organized table format for easy reading.

**6. Error Handling:**

- Gracefully handles unavailable prices or unexpected issues during data retrieval.

**7. User Input Flexibility:**

- Accepts a list of comma-separated game names from the user for batch processing.

**8. Real-time ETA Timer:**

- Displays the estimated time remaining for processing games dynamically.
# Deployment

To deploy Steam Region Hunter, ensure your system meets the following prerequisites

**Prerequisites**

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- pip packages: selenium, pandas, tabulate, tqdm

## Steps to Deploy

**1. Clone or Download the Code:**

- Save the script to a desired folder on your system.

**2. Install Required Python Libraries:**

```bash
  pip install selenium pandas tabulate tqdm
```
**3. Setup ChromeDriver:**

- Download the appropriate ChromeDriver version from here.

- Update the driver_path variable in the script to point to the location of your ChromeDriver executable.

**4. Create the Output Directory:**

- Ensure the output directory specified in the script (output_directory) exists, or create it manually.

**5. Run the Script:**

- Open a terminal or command prompt in the folder containing the script.

- Run the script using the following command:
```bash
  python steam_region_hunter.py
```
**6. Input Game Names:**

- Enter a comma-separated list of game names when prompted.

**7. View Results:**

- The CLI will display a formatted table of the results.

- An Excel file named steamrgnhntr.xlsx will be saved to the output directory.
# Installation

**1. Clone the repository:**
```bash
  git clone https://github.com/yourusername/SteamRegionHunter.git
  cd SteamRegionHunter
```
**2. Run the setup script:**
```bash
  ./run.sh
```
**3. Use the app:**
```bash
  steam-region-hunter
```
    
## Future Enhancements

Here are some ideas to expand the functionality and usability of Steam Region Hunter:

**1. Additional Region Support:**

- Extend the comparison to include more regions like the USA, EU, etc.

**2. Automated Game List Retrieval:**

- Scrape popular game lists or wishlists directly from Steam to avoid manual input.

**3. Improved Price Parsing:**

- Handle more edge cases for price formats, including regional-specific variations.

**4. Historical Price Tracking:**

- Maintain a database to track price trends over time.

**5. GUI Version:**

- Develop a graphical user interface for easier interaction.

**6. Dockerization:**

- Create a Docker container for easier setup and deployment.

**7. Currency Conversion API:**

- Integrate with a live currency conversion API to dynamically adjust the conversion rate.

**8. Multi-threading:**
- Implement multi-threading to speed up the data fetching process for larger game lists.

**9. Cloud Integration:**

- Allow users to save their results to cloud platforms like Google Drive or Dropbox.

**10. Comprehensive Error Reporting:**

- Provide detailed error logs for troubleshooting.
## License

[MIT](https://choosealicense.com/licenses/mit/)

