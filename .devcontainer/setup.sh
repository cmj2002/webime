echo Installing python dependencies...
pip3 install --user -r requirements.txt

echo Installing frontend packages...
cd frontend
npm ci

echo Building frontend...
npm run build

echo Finished. Run `python server.py` to start the server.