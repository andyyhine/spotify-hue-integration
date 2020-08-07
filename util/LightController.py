from phue import Bridge
from rgbxy import Converter

class LightController:

    def __init__(self, bridgeAddress):
        self.bridge = Bridge(bridgeAddress)
        self.lights = self.bridge.get_light_objects('name')
        self.converter = Converter()

    def setLight(self, light, r, g, b):
        try:
            xy = self.converter.rgb_to_xy(r, g, b)
        except ZeroDivisionError:
            xy = [1/3, 1/3]
        finally:  
            self.lights[light].xy = xy
        
    
