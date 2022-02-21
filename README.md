# car
indor navigated self-driving car with 2 cameras and manipulator based on python 3.7+ &amp; Raspberry Pi 3 B+ 

беспилотная машина с навигацией внутри помещения и манипулятором с 3 степенями свободы 

![car](https://github.com/mikaelangelm/car/blob/main/documents/car.jpg?raw=true)
![manipulator](https://github.com/mikaelangelm/car/blob/main/man.jpg?raw=true)
![cameras]()

## SOFTWARE:
* Raspberry pie OS (Debian 11 (bullseye))
* python 3.7+ (RPi, numpy, asyncio, aiohttp, cv2, PIL, picamera, tf.keras)
* jupiter lab, Thonny IDE

## HARDWARE
* Raspberry pie 3 B+ rev.2
* Портативный аккумулятор (5 V)
* Аккумулятор NiCd (1.2 V, 4 шт.)
* Драйвер мотора с модулем L298N (3 шт.)
* Модуль повышения напряжения
* Raspberry camera module OV5647 с ночным видинием (5 MP, 160°) 
* USB camera (2 MP)
* Сервопривод MG 996R (4 шт.)
- старая игрушечная беспроводная машинка JP Ranger
* коллекторный двигатель (3-6 V, мотор)
* катушка индуктивности (руль)
- Инфракрасный датчик расстояния (20 см, 2 шт.)
* Конструктор металлический
* Лапа металлическая под сервопривод MG 996R

## DONE:
1) Собрать машинку
2) Написать ПО для движения машки (car.py)
3) Написать веб-клиент для управления движением машины (tesla_joystick.html)

## TODO:
1) Написать ПО для датчиков приближения (car.py)
2) Собрать манипулятор и сервоприводы
3) Написать ПО для манипулятора (man.py)
4) Написать ПО для камер (cam.py)
5) Собрать данные и создать модель для indoor навигации (Raspberry camera)
6) Собрать данные и создать модель для манипуляции (USB-camera)
