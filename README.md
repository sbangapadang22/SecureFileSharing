## Secure File Sharing Web Application
### Files are never sent to the server. Utilizes AES-256-GCM to encrypt files uploaded by users. Encrypted using a randomly generated key with high entropy.

### 4/6/2024 dev notes (deploying to heroku):
1. some errors when deploying, cant access app (update backend to handle heroku)
2. code still usable with localhost:800 for now

### dev notes (still in development, using Flask):

1. open terminal 1 and nav to dev_httpserver and run python -m http.server
2. open terminal 2 stay in project dir, run python backend.py
3. nav to http://localhost:8000/ on chrome, to test functionality
4. add stuf