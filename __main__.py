from application import main

db, app = main()

if __name__ == "__main__":
    try:
        app.run(port=8000)
    except Exception as e:
        print(e)
        db.save()