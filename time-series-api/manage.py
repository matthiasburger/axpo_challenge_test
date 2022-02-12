from application import create_app

try:
    app = create_app()
except Exception as e:
    print(e)
    raise