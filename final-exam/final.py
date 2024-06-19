import RPi.GPIO as GPIO
from time import sleep
import time
import random
import board
import neopixel
from gpiozero import Button, PWMOutputDevice
import paho.mqtt.client as mqtt

# MQTT 설정
MQTT_HOST = "mqtt-dashboard.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = f"mobile/10/sensing"  # MY_ID에 적절한 식별자를 넣어주세요

# MQTT 클라이언트 생성
mqtt_client = mqtt.Client()

# 연결되었을 때 호출될 콜백 함수
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 브로커에 연결되었습니다.")
    else:
        print(f"MQTT 브로커 연결에 실패하였습니다. 코드: {rc}")

# MQTT 클라이언트에 콜백 함수 등록
mqtt_client.on_connect = on_connect

# MQTT 브로커에 연결
mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

# GPIO 설정
pixel_pin = board.D10
button_pin = 24
buzzer_pin = 12

# LED 스트립 설정   
NUM_PIXELS = 4
pixels = neopixel.NeoPixel(pixel_pin, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

# 버튼과 부저 설정
button = Button(button_pin, pull_up=False)
buzzer = PWMOutputDevice(buzzer_pin, frequency=100, initial_value=0.0)

def buzz(duration):
    buzzer.value = 0.5
    sleep(duration)
    buzzer.value = 0.0

def set_led_color(color):
    pixels.fill(color)
    pixels.show()

def clear_led():
    pixels.fill((0, 0, 0))
    pixels.show()

def send_mqtt_message(topic, payload):
    mqtt_client.publish(topic, payload)
    print(f"MQTT 메시지 전송 - 주제: {topic}, 메시지: {payload}")

def reaction_test():
    print("준비...")
    set_led_color((0, 0, 255))  # 준비 신호: 파란색
    sleep(random.uniform(2, 5))  # 2초에서 5초 사이 랜덤 대기
    set_led_color((255, 0, 0))  # 시작 신호: 빨간색
    start_time = time.time()

    button.wait_for_press()
    reaction_time = time.time() - start_time
    clear_led()

    reaction_time_str = f"{reaction_time:.3f}초"
    print(f"반응 시간: {reaction_time_str}")

    if reaction_time < 0.2:
        buzz(0.1)  # 빠른 반응 - 짧은 부저 소리
    else:
        buzz(0.5)  # 느린 반응 - 긴 부저 소리

    # MQTT로 반응 시간 전송
    send_mqtt_message(MQTT_TOPIC, reaction_time_str)

try:
    print("버튼을 눌러 게임을 시작하세요...")
    button.wait_for_press()
    print("게임을 시작합니다...")
    reaction_test()
    
except KeyboardInterrupt:
    print("게임 종료")
finally:
    clear_led()
    GPIO.cleanup()
