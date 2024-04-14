from sqlalchemy import create_engine, text

class dbConnect:
    db_connection_string = "mysql+pymysql://oslz0wcxffrpqea60rna:pscale_pw_q95yltu3ILbRH8ueq9TY8sZRtHsJd9cxLc40Wr8hD4n@aws.connect.psdb.cloud/csit321?charset=utf8mb4"

    engine = create_engine(
        db_connection_string,
        connect_args={
            "ssl": {
                "ssl_ca": "/etc/ssl/cert.pem",
            }
        }
    )