##python -m chainlit run app.py --host 0.0.0.0 --port 8000

python -m pip install --upgrade pip
pip install -r requirements.txt

PORT=${PORT:-8000}
                                                               
python -m chainlit run app.py --host 0.0.0.0 --port $PORT

