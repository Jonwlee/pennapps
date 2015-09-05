#PennApps


1st time setup (install python first, then pip install virtualenv, virtualenvwrapper):
(http://mkelsey.com/2013/04/30/how-i-setup-virtualenv-and-virtualenvwrapper-on-my-mac/)
- mkvirtualenv pennapps
- workon pennapps if you don't see (pennapps) on your terminal user already
- pip install -r python/requirements.txt
- move your alchemyAPI api key (which should be in a file called api_key.txt) to python/alchemyAPI/api_key.txt
- `python python/server.txt` to start server at localhost:5000
- Turn off server with CtrlC
