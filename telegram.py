from pywinauto import Application
from pywinauto import mouse
from pywinauto.keyboard import send_keys
from img_detection import *
import time
from random_word import RandomWords
import pyperclip
import psutil
from loguru import logger
from devtools import *


class TelegramApp:
    x, y = 100, 100
    width, height = 800, 600

    def __init__(self, exe_path, wait_network_loading=True, time_to_wait=60):
        self.app = Application().start(exe_path)
        self.app.wait_cpu_usage_lower(threshold=5)

        self.main_window = self.app.top_window()

        self.main_window.move_window(x=self.x, y=self.y, width=self.width, height=self.height, repaint=True)

        if wait_network_loading:
            if not wait_while_img_dissapear(self.main_window, 'templates\\telegram\\network_loading.png', 0.25, time_to_wait*4, 0.95):
                raise Exception(f'Telegram not loaded in {time_to_wait} sec')
            logger.info('Telegram loaded successfully!')


    def get_window_center_coords(self, window):
        rect = window.rectangle()
        x = rect.left
        y = rect.top
        width = rect.width()
        height = rect.height()

        x_center = int(x + width / 2)
        y_center = int(y + height / 2)

        return x_center, y_center

    
    def scroll_to_click(self, dist, window, template_path, delay, tries_count, threshold, click=True):
        x, y = self.get_window_center_coords(self.main_window)

        window.set_focus()

        time.sleep(0.2)
        mouse.move(coords=(x, y))
        time.sleep(0.2)

        for i in range(dist):
            if i % 5 == 0:
                if click:
                    if click_on_img(window, template_path, delay, tries_count, threshold):
                        return True
                else:
                    if get_img_coords(window, template_path, delay, tries_count, threshold):
                        return True
            send_keys('{DOWN}')
            time.sleep(0.01)
        return False


    def key_cycle(self, window, key, count, delay):
        window.set_focus()
        for i in range(count):
            send_keys(key)
            time.sleep(delay)


    def turn_on_webview_inspecting(self):
        click_on_img(self.main_window, 'templates\\telegram\\burger_menu.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\settings.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\advanced.png', 0.5, 5, 0.9)

        self.scroll_to_click(60, self.main_window, 'templates\\telegram\\exp_settings.png', 0, 1, 0.9)

        if self.scroll_to_click(50, self.main_window, 'templates\\telegram\\inspection.png', 0, 1, 0.9, click=False):
            if click_on_img(self.main_window, 'templates\\telegram\\inspection_off.png', 0.5, 5, 0.9):
                logger.info('Webview inspecction ON!')
            elif get_img_coords(self.main_window, 'templates\\telegram\\inspection_on.png', 0.5, 5, 0.9):
                logger.info('Webview inspecction already ON!')
            else:
                logger.info('Inspection not found!')

        self.key_cycle(self.main_window, '{ESC}', 4, 0.05)


    def enter_new_text(self, nickname, delay=0.2):
        time.sleep(delay)
        send_keys("^a")
        time.sleep(delay)
        send_keys("{BACKSPACE}")
        time.sleep(delay)
        send_keys(nickname)


    def set_nickname(self, nickname, delay=0.2, change_if_already_set=False):
        click_on_img(self.main_window, 'templates\\telegram\\burger_menu.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\settings.png', 0.5, 5, 0.7)
        click_on_img(self.main_window, 'templates\\telegram\\my_account.png', 0.5, 5, 0.9)
        click_on_img(self.main_window, 'templates\\telegram\\change_username.png', 0.5, 5, 0.9)

        if not change_if_already_set and not get_img_coords(self.main_window, 'templates\\telegram\\empty_username.png', 0.5, 5, 0.9):
            logger.info('Username already setted!')
            self.key_cycle(self.main_window, '{ESC}', 4, 0.05)
            return True

        self.enter_new_text(nickname, delay)
        time.sleep(delay * 3)

        if get_img_coords(self.main_window, 'templates\\telegram\\username_available.png', 0.5, 10, 0.9):
            if click_on_img(self.main_window, 'templates\\telegram\\save.png', 0.5, 5, 0.8):
                logger.info('Username successfully setted!')
                self.key_cycle(self.main_window, '{ESC}', 4, 0.05)
                return True
        
        raise Exception('Username do not setted!')
    

    def launch_app(self, launch_path, allow_msg_path, ok_path, link, app_name='App', timeout=30):
        old_windows = list(self.app.windows())

        for i in range(int(timeout / (timeout/10))):
            self.write_to_saved_messages(link)  #1sec
            if click_on_img(self.main_window, launch_path, 0.2, 45, 0.9):
                break

        for i in range(timeout):
            if get_img_coords(self.main_window, allow_msg_path, 0.3, 3, 0.9): #0.9sec
                click_on_img(self.main_window, ok_path, 0.3, 10, 0.9)

            new_windows = list(self.app.windows())
            if len(new_windows) > len(old_windows):
                unique_windows = [w for w in new_windows if w not in old_windows]
                app_window = unique_windows[0]
                if app_window:
                    logger.info(f'{app_name} window successfully launched!')
                    return app_window

        raise Exception(f'{app_name} window do not launched.')
    

    def open_dev_tools(self, app, focus_control_path, app_name='App', wait=30):
        if app is None:
            raise Exception(f'{app_name} window not found!')

        if not click_on_img(app, focus_control_path, 0.2, wait*5, 0.9):
            raise Exception('Focus control not found!')
        time.sleep(0.3)
        send_keys("{F12}")
        time.sleep(0.2)
        devtools = DevTools()
        return devtools
    

    def write_to_saved_messages(self, message, delay=0.2):
        time.sleep(delay)
        send_keys("^0")
        pyperclip.copy(message)
        time.sleep(delay)
        send_keys("^v")
        time.sleep(delay)
        send_keys("{ENTER}")


    def quit_telegram(self):
        self.main_window.set_focus()
        time.sleep(0.1)
        self.main_window.set_focus()
        time.sleep(0.3)
        send_keys('^q')
        logger.info("Telegram closed with ^q.")


    @staticmethod
    def get_random_word_with_length( min_length, max_length):
        r = RandomWords()
        while True:
            word = r.get_random_word()
            if min_length <= len(word) <= max_length:
                return word


    @staticmethod
    def get_nickname():
        word1 = TelegramApp.get_random_word_with_length(3,5)
        word2 = TelegramApp.get_random_word_with_length(3,5)
        nickname = f"{word1}{word2}"
        return nickname

    
    @staticmethod
    def stop_telegram_processes():
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if 'Telegram' in process.info['name']:
                    p = psutil.Process(process.info['pid'])
                    p.terminate()
                    p.wait()
                    logger.warning(f"Telegram process - PID {process.info['pid']} was stopped.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    
    @staticmethod
    def is_proxifier_running():
        for process in psutil.process_iter(['name']):
            if process.info['name'] == 'Proxifier.exe':
                return True
        return False
    

    @staticmethod
    def get_account_number_from_path(path):
        try:
            formatted_str = path[path.index('all_telegrams')+14:].strip()
            end_str = formatted_str[:formatted_str.index("\\")]
            return int(end_str)
        except:
            return None
        

    @staticmethod
    def get_control_data(window):
        children = window.children()
        print()
        for control in children:
            control_text = control.window_text()
            control_rect = control.rectangle()
            control_width = control_rect.width()
            control_height = control_rect.height()
            control_class = control.class_name()
            print(f"Текст контролу: {control_text}")
            print(f"Ім'я класу контролу: {control_class}")
            print(f"Розміри контролу: {control_width}x{control_height}")
            print()


    @staticmethod
    def print_window_info(window):
        window_title = window.window_text()
        window_class = window.class_name()
        window_rect = window.rectangle()
        window_position = (window_rect.left, window_rect.top)
        window_size = (window_rect.width(), window_rect.height())

        print(f"Заголовок вікна: {window_title}")
        print(f"Клас вікна: {window_class}")
        print(f"Позиція вікна: {window_position}")
        print(f"Розмір вікна: {window_size}")
