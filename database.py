from sqlalchemy import create_engine, text

class dbConnect:
    db_connection_string = "mysql+pymysql://ymxyk9vwlplokqz9epql:pscale_pw_yTBmlW78dzZDPiag3SXdEtAIXlf3r1j3c1dHlLsFjg2@aws.connect.psdb.cloud/csit321?charset=utf8mb4"

    engine = create_engine(
        db_connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": "/etc/ssl/cert.pem",
            }
        }
    )