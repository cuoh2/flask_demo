"""
    author : Liuwj 
    email  : cuohohoh@gmail.com
    time   : 2019/9/1 14:30
    file   : run.py
"""
from app import create_app

app = create_app()


if __name__ == '__main__':
    app.run()

