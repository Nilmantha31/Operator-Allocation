class Config:
    HOST = '127.0.0.1'  
    PORT = 5000          
    DEBUG = True         

class ProductionConfig(Config):
    DEBUG = False
    HOST = '192.168.0.137'
    PORT = 5000

class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '192.168.40.129'
    PORT = 5000