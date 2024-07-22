from pywinauto import Application
import re
from loguru import logger
import json
from pywinauto import Desktop, Application
import time

class DevTools:
    base_params_path = [                    #path to RootWebArea
        {'class_name': "BrowserRootView"},
        {'class_name': "NonClientView"},
        {'class_name': "BrowserFrameViewWin"},
        {'class_name': "BrowserView"},
        {'class_name': "SidebarContentsSplitView", 'found_index': 0},
        {'class_name': "SidebarContentsSplitView", 'found_index': 0},
        {'class_name': "View"},
        {'auto_id': "RootWebArea"},
    ]

    storage_subpath = [
        {'class_name': 'widget vbox tabbed-pane-shadow', 'found_index': 0},
        {'auto_id': 'panel-resources'},
        {'class_name': 'widget vbox panel resources'},
        {'class_name': 'tree-outline'},
        {'class_name': 'children expanded', 'title':	'Storage'},
    ]

    table_path = [
        {"class_name": "widget vbox tabbed-pane-shadow", "found_index": 0},
        {'class_name': "widget vbox flex-auto view-container overflow-auto overflow-hidden"},
        {'class_name': "widget vbox panel resources"},
        {'class_name': "data-grid striped-data-grid"},
        {'class_name': "data-grid no-selection striped-data-grid"}, #non-selected var
        {'class_name': "data"},
    ]

    def __init__(self) -> None:
        if DevTools.is_process_running('DevTools', 10):
            self.app = Application(backend="uia").connect(title_re="DevTools")
        else:
            raise Exception("DevTools Application do not found")

        self.main_window = self.app.top_window()
        if not self.main_window:
           raise Exception("DevTools Window do not found")
        
        self.RootWebArea_control = DevTools.get_control_by_path(self.main_window, self.base_params_path)
        if not self.RootWebArea_control:
           raise Exception("DevTools RootWebArea_control do not found")
        
        logger.info("DevTools launched successfully!")
        

    @staticmethod
    def is_process_running(process_name, timeout=1):
        for i in range(int(timeout*5)):
            windows = Desktop(backend="uia").windows(title_re=process_name)
            if len(windows) > 0:
                return True
            time.sleep(0.2)
        return False


    @staticmethod
    def get_control_by_path(main_control, params_path, skip_count=5):
        current_control = main_control
        for current_params in params_path:
            prev_control = current_control
            current_control = current_control.child_window(**current_params)
            if not current_control.exists():
                skip_count -= 1
                if skip_count > 0:
                    current_control = prev_control
                    continue
                raise Exception(f'Control with params: {current_params} not found.')
        return current_control
    
    
    @staticmethod
    def found_child_by_name(controls, name_to_find, deep=1):
        matched_controls = []
        for control in controls:
            if name_to_find in control.window_text():
                return control
            if deep > 0:
                childrens = control.children()
                result = DevTools.found_child_by_name(childrens, name_to_find, deep - 1)
                if result:
                    matched_controls.append(result)
        if matched_controls:
            return matched_controls
        return None

    def get_tgWebAppData_control(self):

        table_control = DevTools.get_control_by_path(self.RootWebArea_control, self.table_path)
        tgWebAppData_control = DevTools.found_child_by_name(table_control.children(), 'tgWebAppData')[0]
        return tgWebAppData_control


    def get__tgWebAppData(self):
        tgWebAppData_control = self.get_tgWebAppData_control()
        tgWebAppData_dict = json.loads(tgWebAppData_control.window_text())
        return tgWebAppData_dict['tgWebAppData']
    
    
    def get_localdata_control(self):
        table_control = DevTools.get_control_by_path(self.RootWebArea_control, self.table_path)
        tgWebAppData_control = DevTools.found_child_by_name(table_control.children(), 'distinct_id')[0]
        return tgWebAppData_control

    def get_localdata(self):
        localdata_control = self.get_localdata_control()
        full_text = localdata_control.element_info.name
        res = self.extract_ids_from_text(full_text)
        return res
    

    def extract_ids_from_text(self, text):
            distinct_id_pattern = r'"distinct_id"\s*:\s*"([^"]+)"'
            device_id_pattern = r'\$device_id"\s*:\s*"([^"]+)"'

            distinct_id_match = re.search(distinct_id_pattern, text)
            device_id_match = re.search(device_id_pattern, text)

            result = {
            'distinct_id': distinct_id_match.group(1) if distinct_id_match else None,
            'device_id': device_id_match.group(1) if device_id_match else None,
            'user_id': distinct_id_match.group(1) if distinct_id_match else None,
            }
            return result


    def get_Application_btn_control(self):
        path = [
            {'class_name': 'widget tabbed-pane-shadow tool-actions-side-view tab-layout-activity-bar hbox'},
            {'class_name': 'tabbed-pane-header-tabs'},
            {'auto_id': 'tab-resources'},
        ]

        application_control = DevTools.get_control_by_path(self.RootWebArea_control, path)
        return application_control
    

    def get_storage_control(self, control_name):
            storage_control = DevTools.get_control_by_path(self.RootWebArea_control, self.storage_subpath)
            session_storage_control = DevTools.found_child_by_name([storage_control], control_name)[0]
            return session_storage_control


    def get_storage_item_data_by_name(self, data_name):
        storage_control = DevTools.get_control_by_path(self.RootWebArea_control, self.storage_subpath)
        session_storage_subcontrol = DevTools.found_child_by_name(storage_control.children(), data_name)
        return session_storage_subcontrol
    

    def prepare_and_get_tgWebAppData(self):
        app_btn_control = self.get_Application_btn_control()
        app_btn_control.click_input()

        session_storage_control = self.get_storage_control('Session storage')
        session_storage_control.double_click_input()
        matched_controls = control = self.get_storage_item_data_by_name('https://telegram.blum.codes')
        if len(matched_controls) > 1:
            res_control = matched_controls[1]
        else: 
            res_control = matched_controls[0]
        res_control.click_input()

        webAppData = self.get__tgWebAppData()
        return webAppData
    

    def prepare_and_get_localdata(self):
        session_storage_control = self.get_storage_control('Local storage')
        session_storage_control.double_click_input()
        matched_controls = control = self.get_storage_item_data_by_name('https://telegram.blum.codes')
        res_control = matched_controls[0]
        res_control.click_input()

        localdata = self.get_localdata()
        return localdata



    def print_all_controls_info(self, parent_control):
        children = parent_control.children()
        for child in children:
            title = child.window_text()
            class_name = child.friendly_class_name()
            rectangle = child.rectangle()
            
            print(f"Заголовок: {title}")
            print(f"Клас: {class_name}")
            print(f"Розташування: {rectangle}")
            print("-" * 40)

