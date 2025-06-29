"""DB-Connection Klasse für Datenbankverbindung."""

from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm.session import Session, sessionmaker


class DbCon:
    """
    Stellt eine Verbindung zu einer Datenbank her, basierend auf einer YAML-Konfigurationsdatei.
    Diese Klasse ermöglicht das Erstellen von SQLAlchemy-Sessions sowie das Löschen aller Daten
    aus einer Tabelle.

    :param db_name: Name der Datenbank
    :type db_name: Optional[str]
    :param user: Datenbank-Benutzername
    :type user: Optional[str]
    :param config_path: Pfad zur YAML-Konfigurationsdatei mit Zugangsdaten.
    :type config_path: pathlib.Path
    """

    def __init__(
        self,
        db_name: Optional[str] | None = None,
        user: Optional[str] | None = None,
        config_path: Path = Path(__file__).parent / "config/config.yaml",
    ) -> None:
        # config-Datei lesen
        with config_path.open("r") as f:
            config: dict = yaml.safe_load(f)

        if not db_name:
            db_name: str = config["name"]

        if not user:
            user: str = config["user"]

        # generierung der Datenbank URL
        self.db_url: URL = URL.create(
            drivername="postgresql",
            username=user,
            password=config["password"],
            host=config["host"],
            database=db_name,
            port=config["port"],
        )

        # Verbindung mit der Datenbank
        self.engine: Engine = create_engine(url=self.db_url)

        self.session: Session = sessionmaker(self.engine)

    def get_session(self) -> sessionmaker:
        """
        Gibt ein SQLAlchemy-Sessionmaker-Objekt zurück, das für Transaktionen
        mit der Datenbank verwendet werden kann.
        Muss mit zwei Klammern aufgerufen werden: get_session()()

        :return: Sessionmaker-Objekt zur Erstellung von SQLAlchemy-Sessions.
        :rtype: sqlalchemy.orm.sessionmaker
        """

        return self.session

    def delete_all_data_from_table(self, table) -> None:
        """
        Löscht alle Einträge aus der angegebenen Tabelle und bestätigt die Transaktion.

        :param table: SQLAlchemy-Modellklasse, aus der die Daten gelöscht werden sollen.
        :type table: sqlalchemy.ext.declarative.DeclarativeMeta
        """

        with self.get_session()() as session:
            try:
                num_rows_deleted: int = session.query(table).delete()
                session.commit()
                logger.debug(
                    "Deleted {} rows from  table '{}'",
                    num_rows_deleted,
                    table.__tablename__,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                session.rollback()
                logger.error(e)
