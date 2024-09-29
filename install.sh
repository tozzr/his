# mkdir hisss && cd hisss
python3 -m venv venv
source venv/bin/activate
pip install fastapi==0.111.0 jinja2==3.1.4
pip install passlib[bcrypt] python-jose