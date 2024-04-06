## Secure File Sharing Web Application
### Files are never sent to the server. Utilizes AES-256-GCM to encrypt files uploaded by users. Encrypted using a randomly generated key with high entropy.

### dev notes (still in development, using Flask):

1. open terminal 1 and nav to dev_httpserver and run python -m http.server
2. open terminal 2 stay in project dir, run python backend.py
3. nav to http://localhost:8000/ on chrome, to test functionality
4. add stuff

# todo:
1. create records to view / edit status, views for self-destruct, etc.
2. experiment w/ frontend (get off bootstrap)
3. deploy online
4. test
