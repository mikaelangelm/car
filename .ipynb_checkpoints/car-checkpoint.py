# from IPython.display import clear_output ; clear_output()
import time as time_lib
 
# import logging #https://pythonhosted.org/RPIO/rpio_py.html#log-output
# log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
# logging.basicConfig(format=log_format, level=logging.DEBUG) 
import RPi.GPIO as io

import asyncio

from aiohttp import web
routes = web.RouteTableDef()
    
class Car:
    def __init__(self, in_1=27, in_2=17, in_3=23, in_4=24):
        self.motor = None
        self.rule = None
        self.motor_1 = in_3  # in motor 
        self.motor_2 = in_4 # in motor 
        self.rule_1 = in_1  # in rule
        self.rule_2 = in_2  # in rule
        self.direct = 0 # для машины [0:9] excl.5, как numpad ; для движков [0,1,2] где 0 - не двигается
        self.debug = True
        if self.debug and type(self) is Car: print('init Car')
        # все что ниже - относится только к мотору/рулю, но может управляться из машины 
        self.pwm = None
        self.freq = 75 # частота ШИМа ; подобрано опытным путем
        self.dur  = 1   # длите льность до максимального разгона/поворта колес
        self.time_sleep = 0.1 # шаг обновления ШИМа (сек)
        self.duty_cycle = 0 # DONE текущее состояние мотора/руля # self.dur / self.time_sleep # шаг увеличения ШИМа (отн.ед.) # 
        self.duty_start, self.duty_finish = 15, 100 # подобрано опытным путем      
        self.time_interval = 0.3 # частота опроса setInterval в tesla_joystick.html
        io.setmode(io.BCM)
    
    def __iter__(self):
        pass
    
    def __del__(self, print=True):
        message_list = []
        io.cleanup()
        motor.pwm.stop()
        del self.motor      
        if self.debug:             
            message_list.append('del Motor')
        del self.rule
        if self.debug:
            message_list.append('del Rule')
            message_list.append('del Car')
        io.cleanup()
        message_list.append('io cleaned up')
        if print:
            for message in message_list: print(message)
        return message_list
        
    def __call__(self, motor, rule, debug=True):
        self.loop = None
        self.motor = motor
        self.motor.car = self
        self.rule = rule
        self.rule.car = self
        self.debug = debug
        if self.debug: print('call Car')
    def __setattr__(self, attr, val):
        self.__dict__[attr] = val
        if type(self) is Car and attr in ('debug', 'time_sleep'):
            if getattr(self, 'motor', None) != None: setattr(self.motor, attr, val) 
            if getattr(self, 'rule', None)  != None: setattr(self.rule,  attr, val)
            
    def print_all_tasks():
        for task in asyncio.all_tasks():
            print(task._coro.__name__)
            
    def cancel_prev_task(self, task_name='move_motor'):
        for task in asyncio.all_tasks():
            if task._coro.__name__ == task_name:
                _=task.cancel()
                break
                if request.app['car'].debug: print_all_tasks()
                
    def move(self, direct_x: float=0, direct_y: float=0):
        if self.loop == None:
            self.loop = asyncio.get_running_loop()
            
        if (direct_y >= 15 or direct_y <=-15):
            self.cancel_prev_task('move_motor')
            self.loop.create_task(self.motor.move_motor((1 if direct_y >= 15 else -1), abs(direct_y)))
        if (direct_x >= 15 or direct_x <=-15):
            self.cancel_prev_task('move_rule')
            self.loop.create_task(self.rule.move_rule((1 if direct_x >= 15 else -1)))
            
    def func(self, t: float=0, y_min: int=0, force=7) -> int:
        t *= force
        '''функция плавного затухания сигнала (y) ближе к началу/концу (t) https://www.wolframalpha.com/input/?i=t%5E2'''
        y = int((t/(1+abs(t)))* 100)    
        return min(y, 100) if y >= y_min else y_min
    
    
class Motor(Car):
    def __init__(self):
        super().__init__()
        if self.debug: print('init Motor: pin', self.motor_1, self.motor_2)
        io.setup(self.motor_1, io.OUT)
        self.pwm1 = io.PWM(self.motor_1, self.freq) # назад
        io.setup(self.motor_2, io.OUT)
        self.pwm2 = io.PWM(self.motor_2, self.freq) # вперед
        self.pwm = self.pwm2

    async def move_motor(self, direct: int=0, duty_cycle: int=100, time=0.1, time_sleep: int=0, flag='flag'):
#         return await self.move_motor0(direct, time)
        if time_sleep > 0:
            if self.debug: print('time_sleep', time_sleep)
            await asyncio.sleep(time_sleep) # TODO del if not necessary
            await self.move_motor(direct, duty_cycle, time)
            return None
        duty_cycle = min(duty_cycle, 100)
        ''' direct: [-1,0,1] 0 - откл., -1 - назад, 1 - вперед'''
        if self.debug: print('move Motor', 'pin', self.motor_2 if direct==1 else self.motor_1, 'time', time, 'duty_cycle', self.duty_cycle, '->', duty_cycle)
        #   0) если направление изменилось:
        # - 1) снижаем скорость до 0
        # - 2) меняем self.pwm (если это 0 - останавливаем и все)
        # - 3) увеличиваем до duty_cycle и выполняем time       
        if direct != self.direct:
            if self.debug: print('0) direct', self.direct, '->', direct)
            # - снижаем скорость до 0
            t = 0
            while 1 - self.func(t) > self.duty_cycle: # чтобы подогнать t под соответствующую мощность
                t += 0.05
            while self.duty_cycle > 0:
                await asyncio.sleep(self.time_sleep)
                if self.debug: print('1)',self.duty_cycle, '->', self.duty_cycle - self.func(t), 't', round(t, 2))
                self.duty_cycle -= self.func(t)                
                self.pwm.ChangeDutyCycle(self.duty_cycle)                               
                t += self.time_sleep
            self.pwm.stop()
            self.direct = 0
            self.duty_cycle = 0
#             if self.debug: print('self.direct 0, self.duty_cycle 0, self.pwm.stop()')
            # - меняем self.pwm (если direct 0 - останавливаем и все)
            if direct==0: return None
#             if self.debug: print('2) устанавливаем self.pwm:', 'direct', direct)
            self.direct = direct
            self.pwm = self.pwm2 if direct==1 else self.pwm1
        # - увеличиваем до duty_cycle и выполняем time
        t = 0
        t_pass = 0
        while self.func(t) < self.duty_cycle: # чтобы подогнать t под соответствующую мощность
            t += 0.05
        if self.debug: print('3.0)', self.duty_cycle, '->', max(duty_cycle, 0), 't', round(t_pass, 2), round(t, 2))
        self.duty_cycle = max(duty_cycle, 0)
        self.pwm.start(self.duty_cycle)
        while self.duty_cycle < duty_cycle and t_pass < time:
            await asyncio.sleep(self.time_sleep)          
            if self.debug: print('3.1)', self.duty_cycle, '->', max(self.duty_cycle, self.func(t, self.duty_start)), 't', round(t_pass, 2), round(t, 2))
            self.duty_cycle = max(self.duty_cycle, self.func(t, self.duty_start))
            self.pwm.ChangeDutyCycle(self.duty_cycle)           
            t += self.time_sleep
            t_pass += self.time_sleep
            
        await asyncio.sleep(self.time_interval*1.6) # с запасом
        if self.debug: print('self.direct 0, self.duty_cycle 0, self.pwm.stop()')
        self.pwm.stop()
        self.direct = 0
        self.duty_cycle = 0
        
        
class Rule(Car):
    def __init__(self):
        super().__init__()
        if self.debug: print('init Rule: pin', self.rule_1, self.rule_2)
        io.setup(self.rule_1, io.OUT)
        self.pwm1 = io.PWM(self.rule_1, self.freq) # назад
        io.setup(self.rule_2, io.OUT)
        self.pwm2 = io.PWM(self.rule_2, self.freq) # вперед
        self.pwm = self.pwm2
    async def move_rule(self, direct: int=0, duty_cycle: int=75, time=0.1, time_sleep: int=0, flag='flag'):
        ''' direct: [-1,0,1] -1 - лево, 0 - откл., 1 - право'''
        if self.debug: print('move Rule', 'pin', self.rule_1 if direct==1 else self.rule_2, 'time', time, 'freq', self.freq, 'duty_cycle', self.duty_cycle, '->', duty_cycle, flag)
        if self.direct != direct:
            self.pwm.stop()
        
        self.pwm = self.pwm2 if direct==1 else self.pwm1
        self.direct = direct
        self.pwm.start(100) # duty_cycle
        await asyncio.sleep(self.time_sleep*1.4)
        self.pwm.stop()
        
car, motor, rule = Car(), Motor(), Rule()
car(motor, rule) # соединим вместе машину, мотор, руль

@routes.get('/')
def tesla_web_response(request):  
    with open('/home/pi/Desktop/Py/tesla_web_client/tesla.html', 'r') as tesla_html_file:
        return web.Response(text=tesla_html_file.read(), content_type='text/html')
@routes.get('/tesla_joystick')
def tesla_joystick(request):
    '''https://www.programmersforum.ru/showthread.php?t=244839'''
    with open('/home/pi/Desktop/Py/tesla_web_client/tesla_joystick.html', 'r') as tesla_html_file:
        return web.Response(text=tesla_html_file.read(), content_type='text/html')
        

@routes.get('/{move}')
async def tesla_move(request):   
    method = request.match_info.get('move')
    return_text = 'done'
    params = dict(request.rel_url.query) # https://stackoverflow.com/questions/47851096/query-parameters-of-the-get-url-using-aiohttp-from-python3-5
    for key in params: params[key] = float(params[key])
    
    def print_all_tasks():
        for task in asyncio.all_tasks():
            print(task._coro.__name__)
    def cancel_prev_task(task_name='move_motor'):
        for task in asyncio.all_tasks():
            if task._coro.__name__ == task_name:
                _=task.cancel()
                break
                if request.app['car'].debug: print_all_tasks()
                
    
    if request.app['loop'] == None:
        request.app['loop'] = asyncio.get_running_loop()
        request.app['car'].loop = request.app['loop']
    
    if method=='move_motor':
        cancel_prev_task(method)
        request.app['loop'].create_task(request.app['car'].motor.move_motor(**params))
    elif method=='move_rule':
        cancel_prev_task(method)
        request.app['loop'].create_task(request.app['car'].rule.move_rule(**params))
    elif method=='move': # TODO manage from Car.move()
        request.app['car'].move(params['direct_x'], params['direct_y'])
    elif method=='car':
        return_text = str(request.app['car'].__dict__)
    elif method=='del_car':
        return_text = str(request.app['car'].__del__())
    return web.Response(text=return_text)


# https://docs.aiohttp.org/en/stable/web_quickstart.html
app = web.Application()
app.add_routes(routes)
app.router.add_static('/static/', path='tesla_web_client/static', name='static')
# car.debug = False
# car.rule.debug = False
car.time_sleep = 0.300 # min(car.time_sleep, 0.5*0.1) # 0.1 - частота опроса setInterval в tesla_joystick.html
app['car'] = car
app['loop'] = None
try:
    web.run_app(app, port=8080) # , host="localhost", port=8080) #
except KeyboardInterrupt:
    del car
