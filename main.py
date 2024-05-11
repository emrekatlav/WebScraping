from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import requests
from PIL import Image
import pytesseract


# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

# Initialize Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Total pages to scrape
totalPages = 115

# File paths for link and info data
link_file_path = r"E:\\Programming\\Python\\Projects\\apps\\Selenium\\ClinicLinks.txt"
info_file_path = r"E:\\Programming\\Python\\Projects\\apps\\Selenium\\ClinicInfos.txt"

# Path for Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Function to extract phone number from a GIF image
def extract_phone_number(driver):
    try:
        phone_element = driver.find_element(By.CSS_SELECTOR, "tr td.value img")
        phone_element.screenshot("phone_number.gif")

        # Process GIF file using Tesseract OCR
        img_text = pytesseract.image_to_string(Image.open("phone_number.gif"), config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789+ -c threshold=100')
        return img_text.strip()
    except Exception as e:
        phone_number = "Phone number not found."
        print(str(e))  # Log error message in case of an exception
    return phone_number

# Loop through pages
for pageNumber in range(1, totalPages + 1):
    url = f"https://rekvizitai.vz.lt/en/companies/odonthology_services/{pageNumber}/"
    driver.get(url)

    driver.maximize_window()
    if pageNumber == 21:
        print("captchayı giriniz")
        time.sleep(30)


    try:
        driver.find_element(By.ID, "cookiescript_close").click()
    except:
        pass

    links = driver.find_elements(By.XPATH, "//a[@class='company-title d-block']")
    # Write links to file
    with open(link_file_path, "a", encoding="utf-8") as file:
        for link in links:
            company_url = link.get_attribute("href")
            file.write(f"{company_url}\n")
    time.sleep(1)

# Read link file and extract company info for each link
with open(link_file_path, "r", encoding="utf-8") as link_file:
    for url in link_file:
        url = url.strip()
        driver.get(url)

        name = driver.find_element(By.CSS_SELECTOR, "h1.title").text.strip()

        address_element = driver.find_element(By.CSS_SELECTOR, "tr[itemprop='address'] .value")
        address = address_element.text.strip() if address_element else "Address information not found."

        phone_number = extract_phone_number(driver)

        website_element = driver.find_element(By.CSS_SELECTOR, "a[href^='http']")
        website = website_element.get_attribute("href") if website_element else "Website information not found."

        registration_code_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='Registration code']/following-sibling::td[@class='value']")
        registration_code = registration_code_element.text.strip() if registration_code_element else "Kayit Kodu Bulunamadi"
        print(f"registration_code: {registration_code}")

        manager_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='Manager']/following-sibling::td[@class='value']")
        manager_name = manager_element.text.strip() if manager_element else "Manager Bulunamadi"

        company_age_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='Company age']/following-sibling::td[@class='value']")
        company_age = company_age_element.text.strip() if company_age_element else "Company Age Bulunamadi"
        print(f"Company Age: {company_age}")
        
        try:
            share_capital_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='Share capital']/following-sibling::td[@class='value']")
            share_capital = share_capital_element.text.strip()
            print(f"Share Capital: {share_capital}")
        except Exception as e:
            share_capital = "Share Capital Bulunamadı"
            print(f"Hata: {str(e)} - Share Capital: {share_capital}")

        
        try:
            state_social_insurance_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='State social insurance contributions amount']/following-sibling::td[@class='value']")
            state_social_insurance = state_social_insurance_element.text.strip()
            print(f"State Social Insurance Contributions Amount: {state_social_insurance}")
        except Exception as e:
            state_social_insurance = "State Social Insurance Contributions Amount Bulunamadı"
            print(f"Hata: {str(e)} - State Social Insurance Contributions Amount: {state_social_insurance}")




        employees_element = driver.find_element(By.XPATH, "//td[@class='name' and text()='Employees']/following-sibling::td[@class='value']")
        employees = employees_element.text.strip() if employees_element else "Employees Bulunamadi"
        print(f"Employees: {employees}")
        
        img_element = driver.find_element(By.CSS_SELECTOR, "tr td.value img")
        img_src = img_element.get_attribute("src") if img_element else None

        if img_src:
            # Handle image download as before
            response = requests.get(img_src)
            if response.status_code == 200:
                img_data = response.content
                with open(f"company_image_{pageNumber}.jpg", "wb") as img_file:
                    img_file.write(img_data)
            else:
                print(f"Failed to retrieve image. Status code: {response.status_code}")
        else:
            print("Image source not found.")
            
        company_info = {
            "name": name,
            "address": address,
            "phone": phone_number,
            "website": website,
            "img": img_src,
            "registration_code": registration_code,
            "manager": manager_name,
            "company_age": company_age,
            "share_capital": share_capital,
            "state_social_insurance": state_social_insurance,
            "employees": employees
        }

        # Write company info to file
        with open(info_file_path, "a", encoding="utf-8") as file:
            file.write(f"Company Name: {company_info['name']}\n")
            file.write(f"Company Address: {company_info['address']}\n")
            file.write(f"Company Phone: {company_info['phone']}\n")
            file.write(f"Company Website: {company_info['website']}\n")
            file.write(f"Company Image: {img_src}\n")
            file.write(f"Registration Code: {company_info['registration_code']}\n")
            file.write(f"Manager: {company_info['manager']}\n")
            file.write(f"Company Age: {company_info['company_age']}\n")
            file.write(f"Share Capital: {company_info['share_capital']}\n")
            file.write(f"State Social Insurance Contributions Amount: {company_info['state_social_insurance']}\n")
            file.write(f"Employees: {company_info['employees']}\n")
            file.write("\n")
        time.sleep(1)

# Close the WebDriver
driver.quit()

