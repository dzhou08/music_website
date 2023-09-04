# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
import parse_music
import os
import shutil

app = FastAPI()
# Mount static files for CSS, JS, etc.
app.mount('/static', StaticFiles(directory='static'), name='static')

# recursively remove only file contents
def remove_file_contents(path):
    print(f'remove only file contents in {path}')
    for c in os.listdir(path):
        full_path = os.path.join(path, c)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            remove_file_contents(full_path)

@app.get('/')
def homepage():
    with open('templates/index.html', 'r') as file:
        content = file.read()
    return HTMLResponse(content)

@app.post('/upload')
async def process_data(
    spreadsheet_id: str = Form(...),
    band_type: str = Form(...),
    file: UploadFile = File(...)
):
    print('HI')
    print('Received data:')
    print(f'Spreadsheet URL: {spreadsheet_id}')
    print(band_type)
    print(f'File name: {file.filename}')

    # Save the uploaded file
    file_path = f'{file.filename}'
    upload_dir = os.path.join(os.getcwd(), "data")
    # Create the upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

        # get the destination path
    dest = os.path.join(upload_dir, file.filename)
    print(dest)

    # copy the file contents
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parse_music.process(spreadsheet_id, band_type, dest)

    #clean all files within folders
    remove_file_contents(upload_dir)

    # Return the processed data or perform any additional operations
    with open('templates/upload_success.html', 'r') as file:
        content = file.read()
    return HTMLResponse(content)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
