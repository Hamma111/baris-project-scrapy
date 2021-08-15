from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import requests
import os
from datetime import datetime, timedelta

# CHANGE THIS VARIABLE TO ADJUST DAYS.
# VALUE OF 3 WOULD MEAN THE DATA FOR PACKAGES OF TODAY AND 2 DAYS BEFORE WILL BE DOWNLOADED
# VALUE OF 2 WOULD MEAN DATA OF ONLY TODAY AND YESTERDAY.
NUM_DAYS = 3

# setting global variables. These may be changed when needed manually when needed
USERNAME = 'barissonmezee@gmail.com'
PASSWORD = 'FRST847!SRC'
WEBSITE = "https://seller.hepsiglobal.com/"
PERFORMA_FOLDER = os.getcwd() + '\\' + "Downloads" + os.path.sep
TRACKING_FOLDER = os.getcwd() + '\\' + "Downloads" + os.path.sep
IMAGES_FOLDER = os.getcwd() + '\\' + "Downloads" + os.path.sep


def create_folders():
    """
    Creates the necessary folders for the download of PDFs and Images.
    :return: None
    """
    try:
        os.mkdir(PERFORMA_FOLDER)
    except FileExistsError:
        pass
    try:
        os.mkdir(TRACKING_FOLDER)
    except FileExistsError:
        pass
    try:
        os.mkdir(IMAGES_FOLDER)
    except FileExistsError:
        pass


def start_chrome_instance():
    """
    This function starts the instance of a chrome browser
    :return: The chrome instance.
    """
    # initiating an instance of Google Chrome
    options = Options()
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    dr = webdriver.Chrome(options=options)

    return dr


def log_in_first():
    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email']")))
    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

    dr.find_element_by_xpath("//input[@placeholder='Email']").send_keys(USERNAME)
    dr.find_element_by_xpath("//input[@placeholder='Password']").send_keys(PASSWORD)
    dr.find_element_by_xpath("//button[@type='submit']").click()
    dr.get("https://seller.hepsiglobal.com/orders")

    # To verify the log in
    try:
        dr.get("https://seller.hepsiglobal.com/orders")
        WebDriverWait(dr, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='menu-item menu-title']")))
        return True
    except TimeoutException:
        return False


def log_in():
    """
    This function enters the username (email) and the password into the input fields and
    logs in to the website.
    :return: None
    """
    # Filling and submitting the LogIn form
    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Email']")))
    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Password']")))

    dr.find_element_by_xpath("//input[@placeholder='Email']").send_keys(USERNAME)
    dr.find_element_by_xpath("//input[@placeholder='Password']").send_keys(PASSWORD)
    # dr.find_element_by_xpath("//button[@type='submit']").click()

    # To verify the log in
    # try:
    #     dr.get("https://seller.hepsiglobal.com/orders")
    #     WebDriverWait(dr, 10).until(
    #         EC.visibility_of_element_located((By.XPATH, "//span[@class='menu-item menu-title']")))
    # except TimeoutException:
    #     print('Log in to the website not successful.')


def verify_log_in():
    # To verify the log in
    try:
        dr.get("https://seller.hepsiglobal.com/orders")
        WebDriverWait(dr, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@class='menu-item menu-title']")))
        return True
    except TimeoutException:
        print('Log in to the website not successful.')
        return False


def date_verifier():
    package_date = WebDriverWait(dr, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//label[contains( text(), ' Created at:' )]/following-sibling::label"))).text
    package_date = datetime.strptime(package_date.split()[0], "%m/%d/%Y")
    if package_date + timedelta(days=NUM_DAYS) >= datetime.today():
        return True
    else:
        return False


def get_customer_name(order_number):
    """
    returns customer name
    :param order_number: Item's order number (which have been packaged previously)
    :return: (string) The order number (item's unique package identifier number)
    """
    dr.get("https://seller.hepsiglobal.com/orders")
    WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Filter')]")))
    dr.find_element_by_xpath("//span[contains(text(),'Filter')]").click()

    WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.ID, "id")))
    dr.find_element_by_id("id").send_keys(Keys.CONTROL+"a")
    dr.find_element_by_id("id").send_keys(order_number)

    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'Filter')]")))
    dr.find_element_by_xpath("//button[contains(text(),'Filter')]").click()

    _ = WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, f"//td[contains(text(), {order_number})]")))
    customer_name = dr.find_element_by_xpath("//table//tbody//td//a").text
    return customer_name



def return_download_info():
    """
    This function takes in the item's package number as input and returns the item's various specs such as
    performa_link, tracking_link, image_link, item_name in order
    :return: performa_link, tracking_link, image_link, item_name, barcode
    """

    # performa pdf link
    performa_element = WebDriverWait(dr, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//a[contains(text() , ' Get Proforma PDF')]")))
    performa_link = performa_element.get_attribute("href")

    # Click the banner to reveal information of tracking pdf link
    WebDriverWait(dr, 10).until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@data-accordion-component='AccordionItem']"))).click()
    tracking_element = WebDriverWait(dr, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//a[contains(text() , ' Get Tracking PDF')]")))
    tracking_link = tracking_element.get_attribute("href")

    # image
    image_element = WebDriverWait(dr, 10).until(EC.visibility_of_element_located(
        (By.XPATH, "//img[@class='table-image']")))
    image_link = image_element.get_attribute('src')

    # item name
    WebDriverWait(dr, 5).until(EC.visibility_of_element_located(
        (By.XPATH, "//div[@class='table-responsive']")))
    item_name = " ".join(dr.find_elements_by_xpath("//div[@class='table-responsive']//tr")[-1].text.split()[2:-3])

    # barcode
    barcode = WebDriverWait(dr, 2).until(
        EC.visibility_of_element_located((By.ID, "tracking_barcode"))).get_attribute("value")

    return performa_link, tracking_link, image_link, item_name, barcode


def download_stuff(url, name_directory):
    """
    This function simply takes in the URL, retrieves the response from URL and saves it according to the name parameter
    :param url: (str) The URL for the PDF or Image
    :param name_directory: (str) The directory + name for the PDF file or Image
    :return:
    """
    site = requests.get(url)
    with open(name_directory, "wb") as file_writer:
        file_writer.write(site.content)


def visit_listed_page():
    dr.get("https://seller.hepsiglobal.com/packages/")
    while True:
        sleep(5)
        package_urls = list(dict.fromkeys([x.get_attribute('href') for x in dr.find_elements_by_xpath("//tbody//td//a")]))
        for package_url in package_urls:
            response = visit_individual_page(package_url)
            if not response:
                return

        sleep(5)
        dr.find_element_by_xpath("//li[@class='next']").click()


def visit_individual_page(package_url):
    print(package_url)
    dr.execute_script(f'''window.open("","_blank");''')
    dr.switch_to.window(dr.window_handles[1])

    dr.get(package_url)

    if not date_verifier():
        return False

    order_number = WebDriverWait(dr, 1).until(EC.visibility_of_element_located(
        (By.XPATH, "//label[contains( text(), ' Order ID:' )]/following-sibling::label"))).text
    customer_name = get_customer_name(order_number)

    dr.get(package_url)

    (performa_link, tracking_link,
     image_link, item_name, barcode) = return_download_info()

    performa_name = PERFORMA_FOLDER + customer_name + " " + item_name + ".pdf"
    download_stuff(performa_link, performa_name)

    tracking_name = TRACKING_FOLDER + customer_name + " " + barcode + ".pdf"
    download_stuff(tracking_link, tracking_name)

    image_name = IMAGES_FOLDER + customer_name + ".jpg"
    download_stuff(image_link, image_name)

    dr.close()
    sleep(2)
    dr.switch_to.window(dr.window_handles[0])
    return True


if __name__ == "__main__":
    create_folders()

    dr = start_chrome_instance()
    dr.get(WEBSITE)

    _ = os.system("cls")
    _ = os.system("cls")

    if not log_in_first():
        log_in()
        input("automatic log in failed. please click the 'log in' button yourself manually. Press enter when done: ")
    if not verify_log_in():
        print("Log in failed still. Exiting")
        exit()
    print("Log in successful.")
    _ = os.system("cls")
    _ = os.system("cls")
    dr.get("https://seller.hepsiglobal.com/packages/")

    date_selected = (datetime.today() - timedelta(days=NUM_DAYS)).strftime("%d-%m_%Y")

    print("\nTraverring packages up till", date_selected, "\n")
    visit_listed_page()
    dr.quit()
    input("\nThe files have been stored successfully. You may close the program and Chrome Browser now.\n")
