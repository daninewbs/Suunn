#class for making rtc easier to use

from pcf8523 import PCF8523
import time


class RealClock(PCF8523):
    """uses PCF8523 class to create some simple getter setter methods"""
    def __init__(self, i2c ):
        
        super().__init__(i2c)
        self.current_time = time.localtime(self.datetime)
        
    
    #added getter methods
    def get_current_year(self):
        return self.current_time[0]
    
    def get_current_month(self):
        return self.current_time[1]
    
    def get_current_day(self):
        day = self.current_time[2]
        if day == 0:  
            return "Sun"
        if day == 1:  
            return "Mon"
        if day == 2:  
            return "Tue"
        if day == 3:  
            return "Wed"
        if day == 4:  
            return "Thur"
        if day == 5:  
            return "Fri"
        if day == 6:  
            return "Sat"
   
    
    def get_current_hour(self):
        """return current hour in the day"""
        return self.current_time[3]
  
    def get_current_min(self):
        """return current min in the day"""
        return self.current_time[4]

    
    
   