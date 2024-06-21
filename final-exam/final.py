import RPi.GPIO as GPIO
from time import sleep
import time
import random
import board
import neopixel
from gpiozero import Button, PWMOutputDevice
import paho.mqtt.client as mqtt

MQTT_HOST = "mqtt-dashboard.com"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = f"mobile/10/sensing"  # MY_ID에 적절한 식별자를 넣어주세요

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 브로커에 연결되었습니다.")
    else:
        print(f"MQTT 브로커 연결에 실패하였습니다. 코드: {rc}")

mqtt_client.on_connect = on_connect

mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

pixel_pin = board.D10
button_pin = 24
buzzer_pin = 12

NUM_PIXELS = 4
pixels = neopixel.NeoPixel(pixel_pin, NUM_PIXELS, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

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
    set_led_color((0, 0, 255))  
    sleep(random.uniform(2, 5)) 
    set_led_color((255, 0, 0))  
    start_time = time.time()

    button.wait_for_press()
    reaction_time = time.time() - start_time
    clear_led()

    reaction_time_str = f"{reaction_time:.3f}초"
    print(f"반응 시간: {reaction_time_str}")

    if reaction_time < 0.2:
        buzz(0.1)  
    else:
        buzz(0.5)  

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