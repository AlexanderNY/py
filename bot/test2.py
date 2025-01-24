def click_coords(coords_array, driver, xpath_to_grab_dict):
    for coords in range(0, len(array)):
        action = ActionBuilder(driver)
        action.pointer_action.move_to_location([coords][0], [coords][1])
        action.pointer_action.click()
        action.perform()
        driver.switch_to.window(driver.window_handles[coords + 1])
        current_url = driver.current_url
        result_page_content_array = {}
        if 'page_url' in xpath_to_grab_dict:
            result_page_content_array['page_url'] = driver.current_url

        if 'page_title' in xpath_to_grab_dict:
            result_page_content_array['page_title'] = driver.find_element("xpath",
                                                                          "/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/h1")

        if 'page_author' in xpath_to_grab_dict:
            result_page_content_array['page_author'] = driver.find_element("xpath",
                                                                           "/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[1]/ul[1]/ul[1]/li[3]/a[1]")

        if 'page_date' in xpath_to_grab_dict:
            result_page_content_array['page_date'] = driver.find_element("xpath",
                                                                         "/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[1]/ul[1]/ul[1]/li[1]")

        if 'page_date' in xpath_to_grab_dict:
            result_page_content_array['page_date'] = driver.find_element("xpath",
                                                                         "/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[1]/ul[1]/ul[1]/li[1]")

        if 'page_text' in xpath_to_grab_dict:
            result_page_content_array['page_text'] = driver.find_element("xpath",
                                                                         "/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/div[1]")

        if 'page_images' in xpath_to_grab_dict:
            result_page_content_array['page_images'] = ""

        if 'page_comments' in xpath_to_grab_dict:
            result_page_content_array['page_comments'] = driver.find_element("xpath",
                                                                             "/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[2]/div[2]")

        if 'page_likes' in xpath_to_grab_dict:
            result_page_content_array['page_likes'] = driver.find_element("xpath",
                                                                          "/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/ul[3]")

        if 'page_views' in xpath_to_grab_dict:
            result_page_content_array['page_views'] = driver.find_element("xpath",
                                                                          "/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/div[2]/span[1]")

        driver.switch_to.window(driver.window_handles[0])

        print(result_page_content_array)

    # это смартлаб хитмэпы (раз в час)


driver = get_chromedriver(use_proxy=False,
                          user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
driver.get('https://smart-lab.ru/q/map/')
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located(("xpath", "/html/body/div/main/div[6]"))
)

set_viewport_size(driver, 1366, 768)

# display the viewport size
print(driver.execute_script("return [window.innerWidth, window.innerHeight];"))

comm_1 = driver.find_element("xpath", "/html/body/div/main/div[6]")
comm_1_x = comm_1.location['x']
comm_1_y = comm_1.location['y']
# -683 влево это до упора, 384 вверх тое до упора, примерная сетка
# всего 30 клеток
# первые две ширина 200 220 220 170 170 165 165
# второй ряд ширина 180
# 1 
#

#
driver.execute_script("window.scrollBy(" + str(comm_1_x) + "," + str(comm_1_y) + ")")

coordinates_array = [[200, 250], [200, 470], [450, 100], [350, 300], [350, 450], [650, 100], [775, 100], [900, 100],
                     [1100, 100], [1250, 100]]
xpath_to_grab_dict = {'page_title': '/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/h1', 'page_author': '/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[1]/ul[1]/ul[1]/li[3]/a[1]', 'page_date':'/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[1]/ul[1]/ul[1]/li[1]', 'page_text': '/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/div[1]', 'page_comments': '/html[1]/body[1]/div[2]/div[4]/div[3]/div[2]/div[2]/div[2]', 'page_likes': '/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/ul[3]', 'page_views': '/html/body/div[2]/div[4]/div[3]/div[2]/div[1]/div[2]/span[1]'}


click_coords(coords_array, driver, xpath_to_grab_dict)
