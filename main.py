import asyncio
import Car, Cam #, Man

car, motor, rule = Car.Car(), Car.Motor(), Car.Rule()#, camera = Cam.cam() #, man.man()
car(motor, rule)#, camera) #, manipulator) # соединим вместе машину, мотор, руль, камеру, манипулятор

self_drive = True

# === AUTOMATIC DRIVE
if self_drive:            
    car.loop = asyncio.new_event_loop()
    car.loop.run_until_complete(car.loop.create_task(car.move(0, 100, time=1)))
    
# === MANUAL DRIVE ===    
else: 
    from aiohttp import web 
    web_handler = Car.WebHandler(app=web.Application(), routes=web.RouteTableDef())
           
    @web_handler.routes.get('/')
    def main_client(request):  
        return web_handler.main_client(request)
    
    @web_handler.routes.get('/tesla_joystick')
    def joystick(request):
        return web_handler.joystick(request)
    
    @web_handler.routes.get('/{move}')
    async def move(request):
        web_handler.move(request)
    
    # https://docs.aiohttp.org/en/stable/web_quickstart.html
    web_handler.app.add_routes(web_handler.routes)

    car.time_sleep = 0.300 # min(car.time_sleep, 0.5*0.1) # 0.1 - частота опроса setInterval в tesla_joystick.html
    web_handler.app['car'] = car
    web_handler.app['loop'] = None
    
    try:
        web.run_app(web_handler.app, port=8080) # , host="localhost", port=8080) #
    except KeyboardInterrupt:
        pass
    
car.__del__()
