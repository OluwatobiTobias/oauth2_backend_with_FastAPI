
def start():
    import uvicorn
    uvicorn.run("auth_app.main:app", host="0.0.0.0", port=3030, reload=True)

if __name__ == "__main__":
    start()