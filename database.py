from sqlalchemy import create_engine, text
import os

from dotenv import load_dotenv
load_dotenv()


class dbConnect:
    db_connection_string = os.environ.get('MYSQL_ADDON_URI')

    engine = create_engine(
        db_connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": "/etc/ssl/cert.pem",
            }
        }
    )