import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://admin:n1mda@localhost/factcheckergh"
SECRET_KEY = 'F34TF$($e34D';
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://example.db'


# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "whatda4k?"

# Secret key for signing cookies
SECRET_KEY = "secret"

