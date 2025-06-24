# solution-bot-sbx
python -m venv venv

.\venv\Scripts\activate

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

pip install -r .\requirements.txt

chainlit run app.py
