from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time, json
import argparse
import logging
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--username_amazon', type=str, required=True)
    parser.add_argument('--password_amazon', type=str, required=True)
    parser.add_argument('--email_ereaderiq', type=str, required=True)
    args = parser.parse_args()

    username_amazon = args.username_amazon
    password_amazon = args.password_amazon
    email_ereaderiq = args.email_ereaderiq

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(60)

    logging.info("get books from amazon, start...")
    books = get_book_from_amazon(driver, username_amazon, password_amazon)
    logging.info("books:%s", len(books))
    with open('./books.json', 'w') as outfile:
        json.dump(books, outfile, indent=2)

    logging.info("add books from to ereaderiq, start...")
    add_book_to_ereaderiq(driver, books, email_ereaderiq)

    driver.quit()

def get_book_from_amazon(driver, username_amazon, password_amazon):
    driver.get('https://www.amazon.com/')
    menu_account = driver.find_element_by_xpath('//*[@id="nav-link-accountList"]/span[1]')
    menu_account.click()

    field_email = driver.find_element_by_xpath('//*[@id="ap_email"]')
    field_email.send_keys(username_amazon)
    time.sleep(3)
    button_continue = driver.find_element_by_xpath('//*[@id="continue"]')
    button_continue.click()
    time.sleep(3)
    field_password = driver.find_element_by_xpath('//*[@id="ap_password"]')
    field_password.send_keys(password_amazon)
    time.sleep(3)
    button_signin = driver.find_element_by_xpath('//*[@id="signInSubmit"]')
    button_signin.click()
    time.sleep(5)
    logging.info(f"logging-in to amazon")

    menu_account = driver.find_element_by_xpath('//*[@id="nav-link-accountList"]/span[1]')
    action = ActionChains(driver)
    action.move_to_element(menu_account).perform()
    item_wishlist = driver.find_element_by_xpath('//*[@id="nav-flyout-wl-items"]/div/a/span')
    item_wishlist.click()
    time.sleep(5)
    logging.info(f"keep scrolling for books to appear...")
    for _ in range(10):
        driver.execute_script("window.scrollBy(0,300)")
        time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    logging.info(f"get books from wishlist")
    items_book = driver.find_elements_by_xpath("//*[@id[starts-with(., 'itemName_')]]")
    books = []
    for item_book in items_book:
        books.append({
                        "text": item_book.text,
                        "uri": item_book.get_attribute("href")
                     })

    return books


def add_book_to_ereaderiq(driver, books, email_ereaderiq):
    # go ereaderiq
    logging.info("logging-in to ereaderiq")
    driver.get('https://www.ereaderiq.com/')
    button_signin = driver.find_element_by_xpath('//*[@id="header_upper_nav"]/li[1]/a')
    button_signin.click()
    time.sleep(3)
    email_field = driver.find_element_by_xpath('//*[@id="header"]//form//input[@name="email"]')
    email_field.send_keys(email_ereaderiq)
    button_login = driver.find_element_by_xpath('//*[@id="header"]/div[5]/div[2]/div/div[2]/div[1]/div/div[1]/form[1]/ul/li[3]/input')
    button_login.click()
    time.sleep(3)
    logging.info("opening the book tracking page...")
    driver.get('https://www.ereaderiq.com/track/drops/asin/')
    time.sleep(3)
    driver.execute_script("window.scrollBy(0,300)")
    logging.info("closing ads if appears...")
    try:
        ad_close = driver.find_element_by_xpath('//span[@class="mmt-sticky-close"]')
        ad_close.click()
    except Exception as ex:
        logging.error("ad element err", exc_info=True)

    time.sleep(3)

    logging.info("adding books to watchlist")
    for i, book in enumerate(books):
        logging.info("***** %s/%s:%s *****", i+1, len(books), book['text'])
        book_uri = driver.find_element_by_xpath('//*[@id="content"]//input[@name="asin"]')
        driver.execute_script("arguments[0].scrollIntoView();", book_uri)
        driver.execute_script("window.scrollBy(0,-200)")
        book_uri.send_keys(book['uri'])
        drop_type = Select(driver.find_element_by_xpath('//*[@id="content"]//select[@name="sign"]'))
        drop_type.select_by_value('percent')
        drop_number = driver.find_element_by_xpath('//*[@id="content"]//input[@name="amt"]')
        drop_number.clear()
        drop_number.send_keys('20')
        radio_update_price = driver.find_element_by_xpath('//input[@id="if_tracked_update"]')
        radio_update_price.click()
        button_track_it = driver.find_element_by_xpath('//*[@id="content"]//input[@value="Track It"]')
        button_track_it.click()
        time.sleep(3)
        try:
            message = driver.find_element_by_xpath('//*[@id="content"]//li[@class="response shown success"]')
            logging.info("\tmessage:%s", message.text)
        except Exception as ex:
            logging.error("message element err", exc_info=True)


if __name__ == "__main__":
    main()