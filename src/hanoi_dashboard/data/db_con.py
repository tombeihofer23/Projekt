from pathlib import Path
from typing import Optional

import yaml
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm.session import Session, sessionmaker


class DbCon:
    """Datenbank-Connection Klasse."""

    def __init__(
        self,
        db_name: Optional[str] | None = None,
        user: Optional[str] | None = None,
        config_path: Path = Path(__file__).parent / "config/config.yaml",
    ) -> None:
        """Konstruktor der Datenbank Klasse"""

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
        """Session-Objekt wird geladen."""

        return self.session
