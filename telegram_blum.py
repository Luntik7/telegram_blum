from telegram import TelegramApp
import time
from img_detection import *
from loguru import logger
from pywinauto.keyboard import send_keys
import json
from devtools import DevTools


class TelegramAppBlum(TelegramApp):
    def __init__(self, exe_path):
        super().__init__(exe_path)
        self.blum_window = None
        self.devtools = None


    def launch_blum(self, link, sleep_before_launch=3, tries_count=30):    
        self.blum_window = self.launch_app(
            'templates\\blum\\launch.png',
            'templates\\blum\\allow_msg.png',
            'templates\\blum\\OK.png',
            link,
            'Blum',
        )
    

    def manage_account_and_open_devtools(self):
        res = find_first_image([
            [self.blum_window, 'templates\\blum\\create_account.png', 0.5, 5, 0.9],
            [self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.9],
            [self.blum_window, 'templates\\blum\\currently_farming.png', 0.5, 5, 0.6],
            [self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6],
            [self.blum_window, 'templates\\blum\\continue.png', 0.5, 5, 0.6],
        ])
        if 'continue' in res:
            click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 5, 0.6)
            res = find_first_image([
                [self.blum_window, 'templates\\blum\\create_account.png', 0.5, 5, 0.9],
                [self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.9],
                [self.blum_window, 'templates\\blum\\currently_farming.png', 0.5, 5, 0.6],
                [self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6],
            ])
        if 'currently_farming' in res:
            logger.info('Account is currently farming!')
        elif 'start_farming' in res:
            logger.info('Account start farming!')
        elif 'claim' in res:
            logger.info('Account claim earnings!')
            click_on_img(self.blum_window, 'templates\\blum\\claim.png', 0.5, 5, 0.6)
            click_on_img(self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 10, 0.6)
        elif 'create_account' in res:
            logger.info('Account start to create!')
            self.create_account()
        else: 
            raise Exception("Account status not found!")

        if click_on_img(self.blum_window, 'templates\\blum\\logo.png', 0.5, 5, 0.7):
            time.sleep(0.3)
            send_keys("{F12}")
            time.sleep(1)
            self.devtools = DevTools()
        else:
            raise Exception('Blum logo not found!')


    def create_account(self):
        click_on_img(self.blum_window, 'templates\\blum\\create_account.png', 0.5, 10, 0.9)
        if get_img_coords(self.blum_window, 'templates\\blum\\blum_nickname_available.png', 0.5, 20, 0.8):
            click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 10, 0.9)
        time.sleep(13)
        click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 50, 0.9)
        click_on_img(self.blum_window, 'templates\\blum\\continue.png', 0.5, 20, 0.9)
        click_on_img(self.blum_window, 'templates\\blum\\start_farming.png', 0.5, 5, 0.6)

        logger.info('Account successfully created!')
        
        

    def collect_data(self, proxy=''):
        session_data = self.devtools.prepare_and_get_tgWebAppData()
        local_data = self.devtools.prepare_and_get_localdata()
        end_data = {
            'proxy': proxy,
            'Token':'',
            'distinct_id': local_data['distinct_id'],
            'device_id': local_data['device_id'],
            'user_id': local_data['user_id'],
            'tok': 'a663ec3881444e996e51121d5a98ce4d',
            'queid': session_data,
        }

        return end_data
    

    def append_to_json_file(self, file_path, new_dict):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        if not isinstance(data, list):
            data = []

        data.append(new_dict)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


    @staticmethod
    def test_devtools():
        devtools = DevTools()
        
        session_data = devtools.prepare_and_get_tgWebAppData()
        local_data = devtools.prepare_and_get_localdata()
        end_data = {
            'proxy':'---',
            'Token':'',
            'distinct_id': local_data['distinct_id'],
            'device_id': local_data['device_id'],
            'user_id': local_data['user_id'],
            'tok': 'a663ec3881444e996e51121d5a98ce4d',
            'queid': session_data,
        }

        for i,j in end_data.items():
            print(f"{i}: {j}")