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
from datetime import datetime


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


def is_item_packable():
    """
    This function ensures that item is packable.
    :return: True or False depending on the state of item order
    """
    try:
        WebDriverWait(dr, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//td[contains(text(),'There is no packable items.')]")))
        return False
    except:
        try:
            WebDriverWait(dr, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//div[contains(text(),'There is no packable items.')]")))
            return False
        except:
            return True


def traverse_orders_page():
    """
    This function paginates the orders pages and extracts the order number of all the items
    :return: 1. (list/array) The order numbers of all the items present on the "orders" page(s)
    2. (list/array) The customer names of all the items present on the "orders" page(s)
    """
    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "icon-pagination")))

    NUM_PAGES = int(dr.find_element_by_class_name("icon-pagination").text.split()[-2])
    order_number_array = []
    customer_name_array = []

    # Extracting order numbers of all the items
    for page_num in range(1, NUM_PAGES + 1):
        dr.find_elements_by_xpath("//ul[contains(@class,'vx-pagination icon-pagination')]//li")[page_num].click()
        sleep(5)
        try:
            assert str(page_num) == dr.find_element_by_xpath(
                "//ul[contains(@class,'vx-pagination icon-pagination')]//li[""@class='active']").text
        except AssertionError:
            print("Page traversal failed. Exiting the code")
            exit()

        order_number_array += [el.text.split()[0] for el in
                               dr.find_elements_by_xpath("//div[@class='table-responsive']//tr")[1:]]
        customer_name_array += [" ".join(el.text.split()[2:-3]) for el in
                                dr.find_elements_by_xpath("//div[@class='table-responsive']//tr")[1:]]

    return order_number_array, customer_name_array


def pack_items(order_number_array, customer_name_array):
    """
    This function Creates packages for all the order numbers of the items
    :param (list/array) order_number_array: The array which hold all the order numbers
    :return: 1. (list/array) The order numbers of items that were packaged successfully
    """
    orders_packed = []
    customer_name_packed = []
    for index, order_number in enumerate(order_number_array):
        dr.get(f"https://seller.hepsiglobal.com/order/{order_number}")
        # ensures that item is packable to prevent the code from breaking
        if not is_item_packable():
            continue

        # create package
        WebDriverWait(dr, 5).until(
            (lambda dr: len(dr.find_elements_by_xpath("//label[@class='custom-control-label']")) == 2))
        dr.find_elements_by_xpath("//label[@class='custom-control-label']")[0].click()

        dr.find_elements_by_class_name("btn.btn-success")[0].click()

        # Confirming the package
        WebDriverWait(dr, 4).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='swal2-actions']//button")))
        dr.find_element_by_xpath("//div[@class='swal2-actions']//button").click()

        # Ensuring that package was created successfully
        WebDriverWait(dr, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//h2[@class='swal2-title' and contains(text(), 'Success')]")))

        orders_packed.append(order_number)
        customer_name_packed.append(customer_name_array[index])

    return orders_packed, customer_name_packed


def filter_package(order_number):
    """
    This function performs the act of filtering the packages based on the order number, and returns the unique package
    identifier allotted to the packaged order
    :param order_number: Item's order number (which have been packaged previously)
    :return: (string) The package number (item's unique package identifier number)
    """
    WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Filter')]")))
    dr.find_element_by_xpath("//span[contains(text(),'Filter')]").click()

    WebDriverWait(dr, 10).until(EC.element_to_be_clickable((By.ID, "order_id")))
    dr.find_element_by_id("order_id").send_keys(Keys.CONTROL+"a")
    dr.find_element_by_id("order_id").send_keys(order_number)

    WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(),'Filter')]")))
    dr.find_element_by_xpath("//button[contains(text(),'Filter')]").click()

    el = WebDriverWait(dr, 10).until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(text(), {order_number})]")))
    package_number = el.get_attribute('href').split('/')[-1]
    return package_number


def extract_all_package_numbers(orders_packed):
    """
    This function does nothing but extracts the package number one by once for all the packed order numbers
    :param orders_packed: (array/list) Order numbers which were previously packed
    :return: (list) The package numbers of the respective order numbers
    """
    package_number_array = []
    for order_number in orders_packed:
        package_number = filter_package(order_number)
        package_number_array.append(package_number)
    return package_number_array


def visit_package_page(package_number):
    """
    This function takes in the item's package number as input and returns the item's various specs such as
    performa_link, tracking_link, image_link, item_name in order
    :param package_number: (str) The package number of the item
    :return: performa_link, tracking_link, image_link, item_name, barcode
    """

    dr.get(f"https://seller.hepsiglobal.com/package/{package_number}")

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


def process_packages(package_number_array, customer_name_packed):
    """
    This is the most important function. It processes the package number and download their pdf and images into
    the respective folders.
    :param package_number_array: (List/array) package numbers
    :param customer_name_packed: (List/array) customer names
    :return: None
    """
    for index, package_number in enumerate(package_number_array):
        (performa_link, tracking_link,
         image_link, item_name, barcode) = visit_package_page(package_number)
        customer_name = customer_name_packed[index]

        performa_name = PERFORMA_FOLDER + customer_name + " " + item_name + ".pdf"
        download_stuff(performa_link, performa_name)

        tracking_name = TRACKING_FOLDER + customer_name + " " + barcode + ".pdf"
        download_stuff(tracking_link, tracking_name)

        image_name = IMAGES_FOLDER + customer_name + ".jpg"
        download_stuff(image_link, image_name)


if __name__ == "__main__":
    create_folders()

    dr = start_chrome_instance()
    dr.get(WEBSITE)

    if not log_in_first():
        log_in()
        input("automatic log in failed. please click the 'log in' button yourself manually. Press enter when done: ")
    if not verify_log_in():
        print("Log in failed still. Exiting")
        exit()
    print("Log in successful.")

    dr.get("https://seller.hepsiglobal.com/orders")
    _ = os.system("cls")
    _ = os.system("cls")
    _ = input("\nPlease press enter here when you are done filtering the items: ")
    _ = os.system("cls")
    _ = os.system("cls")

    print("\nPlease wait. Iterating over orders now.....\n")
    order_number_array, customer_name_array = traverse_orders_page()
    print("\nPackaging the total number of", len(order_number_array), "detected orders.\n")

    orders_packed, customer_name_packed = pack_items(order_number_array, customer_name_array)

    if len(orders_packed) == 0:
        input("\nAll selected Items have been packaged already. Please exit the code. \n")
        exit()

    print("\nPackaged successfully a total number of", len(orders_packed), " orders.\n")

    dr.get("https://seller.hepsiglobal.com/packages/")
    package_number_array = extract_all_package_numbers(orders_packed)
    print("\nExtraction of Package Numbers complete.\n")

    print("\nNow downloading the PDF files and Images for the Items.....\n")
    process_packages(package_number_array, customer_name_packed)
    print("\nThe files have been stored successfully. You may close the program and Chrome Browser now.\n")
