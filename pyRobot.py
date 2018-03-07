import RPi.GPIO as GPIO
import time
import socket
from threading import Thread
from queue import Queue
import pygame
import pygame.camera
import datetime
from pygame.locals import*

UDP_IP = "10.20.9.43"
UDP_PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


SERVO_UDP_PORT = 8081
sockServo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockServo.bind((UDP_IP, SERVO_UDP_PORT))

CAMERA_UDP_PORT = 13267
sockCamera = socket.socket()
sockCamera.bind((UDP_IP, CAMERA_UDP_PORT))
pygame.init()
pygame.camera.init()
pygame.font.init()
myfont = pygame.font.SysFont("monospace", 15)
cam = pygame.camera.Camera("/dev/video0",(240,180))

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)
GPIO.setup(37,GPIO.OUT)
GPIO.setup(32,GPIO.OUT)

TRIG = 23
ECHO = 24
##pulse_duration = 0
##distance = 0

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

p1 = GPIO.PWM(35, 50)
p2 = GPIO.PWM(37, 50)

GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

s1 = GPIO.PWM(38, 50)
s2 = GPIO.PWM(40, 50)


def straight():
    GPIO.output(7,True)
    GPIO.output(13,False)
    GPIO.output(11, False)
    GPIO.output(15, True)

def back():
    GPIO.output(7,False)
    GPIO.output(13,True)
    GPIO.output(11, True)
    GPIO.output(15, False)
    
def right():
    GPIO.output(7,True)
    GPIO.output(13,True)
    GPIO.output(11,False)
    GPIO.output(15, False)

def left():
    GPIO.output(7,False)
    GPIO.output(13,False) 
    GPIO.output(11, True)
    GPIO.output(15, True)
    
def right():
    GPIO.output(7,True)
    GPIO.output(13,True)
    GPIO.output(11, False)
    GPIO.output(15, False)

def distance(D):
    print("asd")
    while True:
        GPIO.output(TRIG, 1)
        time.sleep(0.1)
        GPIO.output(TRIG, 0)
        while GPIO.input(ECHO)== 0:
            pass
        pulse_start = time.time() 
        while GPIO.input(ECHO)== 1:
            pass
        pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start

        dist = pulse_duration * 17150
        
        mess='a'
        if not (D.empty()):
            mess = D.get()
        print ("Distance:", dist, "cm",mess[0])
        
        if (dist < 40):
            if mess[0] =='straight' :
                print("helal")
                #p1.ChangeDutyCycle(0)
                #p2.ChangeDutyCycle(0)

def Run(R):
    while True:
        data, addr = sock.recvfrom(1024)
        receivedValue = data.decode('utf-8')
        message = receivedValue.split()
        print(message)
        R.put(message)
        if (message[0] == 'straight'):
            straight()
            p1.ChangeDutyCycle(int(message[1]))
            p2.ChangeDutyCycle(int(message[1]))
        elif (message[0] == 'back'):
            back()
            p1.ChangeDutyCycle(int(message[1]))
            p2.ChangeDutyCycle(int(message[1]))
        elif (message[0] == 'left'):
            left()
            p1.ChangeDutyCycle(int(message[1]))
            p2.ChangeDutyCycle(int(message[1]))            
        elif (message[0] == 'right'):
            right()
            p1.ChangeDutyCycle(int(message[1]))
            p2.ChangeDutyCycle(int(message[1]))
        elif (message[0] == 'stop'):
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(0)
        elif (message[0] == 'led'):
            GPIO.output(32, 0)
        elif (message[0] == 'ledk'):
            GPIO.output(32, 1)
        else:
            if (message[0] != 'yukarı') & (message[0] != 'asa') & (message[0] != 'sag') & (message[0] != 'sol'):
                p1.ChangeDutyCycle(0)
                p2.ChangeDutyCycle(0)
            continue
def servo():
    s1.start(2.5)
    s2.start(2.5)
    s1.ChangeDutyCycle(0)
    s2.ChangeDutyCycle(0)
    sHorizontal = 2.5
    sVertical = 2.5
    degisim = 0.3
    while True:
        data1, addr = sockServo.recvfrom(1024)
        receivedValue1 = data1.decode('utf-8')
        message1 = receivedValue1.split()
        print(message1)

        if (message1[0] == 'yukarı'):
            if(sHorizontal < 7.5):
                sHorizontal = degisim + sHorizontal
                s1.ChangeDutyCycle(sHorizontal)
        elif (message1[0] == 'asa'):
            if(sHorizontal > 2.5):
                sHorizontal = sHorizontal - degisim
                s1.ChangeDutyCycle(sHorizontal)
        elif (message1[0] == 'sol'):
            if(sVertical < 7.5):
                sVertical = sVertical + degisim
                s2.ChangeDutyCycle(sVertical)
        elif (message1[0] == 'sag'):
            if(sVertical > 2.5):
                sVertical = sVertical - degisim
                s2.ChangeDutyCycle(sVertical)
        else:
            s1.ChangeDutyCycle(0)
            s2.ChangeDutyCycle(0)
        time.sleep(0.1)

def camera():
    while True:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label = myfont.render("%s " %date ,1,(255,255,0))
        cam.start()
        image =cam.get_image()
        image.blit(label, (0,0))
        pygame.image.save(image, "sending.jpg")
        time.sleep(1)
        sockCamera.listen(5)
        c, addr = sockCamera.accept()
        f = open('sending.jpg','rb')
        print('Sending...')
        l = f.read(1024)
        while (l):
            print('Sending...')
            c.send(l)
            l = f.read(1024)
        f.close()
        print("Done Sending")
        c.shutdown(socket.SHUT_WR)
        c.close()
        cam.stop()
    
    


            
q = Queue()
p1.start(0)
p2.start(0)        
t1 = Thread(target = distance, args = (q,))
t2 = Thread(target = Run, args = (q,))
t3 = Thread(target = servo)
t4 = Thread(target = camera )
t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()
GPIO.cleanup()
