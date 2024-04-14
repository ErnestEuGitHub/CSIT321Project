from sqlalchemy import create_engine, text

class dbConnect:
    db_connection_string = "mysql+pymysql://9ifgazidbdynts8z5mhn:pscale_pw_M2Z17oTDOSuKopVqTLhLvZc1JPVeFnDkWRdFspL83eb@aws.connect.psdb.cloud/csit321?charset=utf8mb4"

    engine = create_engine(
        db_connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": "/etc/ssl/cert.pem",
            }
        }
    )