#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-06-2026 19.53.20
#

#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 07-06-2026 19.53.20
#

import sys
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Optional

### - project modules
from pyLnLib import get_logger
logger = get_logger()


class PyProjectManager:
    """Classe per gestire la lettura e scrittura del file pyproject.toml"""

    def __init__(self, git_root: str):
        """
        Inizializza il manager per pyproject.toml

        Args:
            git_root: Percorso root del repository git
        """
        self.git_root = Path(git_root)
        self.pyproject_path = self.git_root / "pyproject.toml"
        self._data = None

    def read(self) -> Optional[dict]:
        """
        Legge il file pyproject.toml

        Returns:
            dict: Dati del file pyproject.toml, None se il file non esiste
        """
        if not self.pyproject_path.exists():
            logger.error(f"File 'pyproject.toml' NOT found in {self.git_root}")
            return None

        try:
            import tomllib
            with open(self.pyproject_path, "rb") as f:
                self._data = tomllib.load(f)
            return self._data
        except Exception as e:
            logger.error(f"Errore nella lettura di pyproject.toml: {e}")
            return None

    def write(self, f_execute: bool = True) -> bool:
        """
        Scrive i dati nel file pyproject.toml

        Args:
            f_execute: Se True esegue la scrittura, altrimenti dry-run

        Returns:
            bool: True se la scrittura è avvenuta con successo, False altrimenti
        """
        if self._data is None:
            logger.error("Nessun dato da scrivere. Eseguire prima read()")
            return False

        if not self.pyproject_path.parent.exists():
            logger.error(f"Directory {self.pyproject_path.parent} non esiste")
            return False

        if f_execute:
            try:
                import tomli_w
                with open(self.pyproject_path, "wb") as f:
                    tomli_w.dump(self._data, f)
                logger.info(f"pyproject.toml aggiornato con successo in {self.pyproject_path}")
                return True
            except Exception as e:
                logger.error(f"Errore nella scrittura di pyproject.toml: {e}")
                return False
        else:
            logger.info("DRY-RUN: pyproject.toml non modificato")
            return True

    def get_version(self) -> str:
        """
        Ottiene la versione corrente dal file pyproject.toml

        Returns:
            str: Versione corrente, "0.0.0" se non trovata
        """
        if self._data is None:
            self.read()

        if self._data is None:
            return "0.0.0"

        return self._data.get("project", {}).get("version", "0.0.0")

    def set_version(self, new_version: str, f_execute: bool = True) -> bool:
        """
        Imposta una nuova versione nel file pyproject.toml

        Args:
            new_version: Nuova versione da impostare
            f_execute: Se True esegue la scrittura, altrimenti dry-run

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        # Leggi i dati correnti se non sono già stati letti
        if self._data is None:
            if not self.read():
                logger.error("Impossibile leggere pyproject.toml")
                return False

        # Ottieni la versione corrente
        cur_version = self.get_version()

        # Assicurati che la struttura "project" esista
        if "project" not in self._data:  # type: ignore
            self._data["project"] = {}  # type: ignore

        # Imposta la nuova versione
        self._data["project"]["version"] = new_version

        # Log delle informazioni
        logger.info(f"Versione corrente: {cur_version}")
        logger.info(f"Nuova versione: {new_version}")

        # Scrivi il file se richiesto
        return self.write(f_execute)

    def update_version(self, new_version: str, f_execute: bool = True) -> bool:
        """
        Metodo alias per set_version per mantenere compatibilità con il codice esistente

        Args:
            new_version: Nuova versione da impostare
            f_execute: Se True esegue la scrittura, altrimenti dry-run

        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        return self.set_version(new_version, f_execute)

    @property
    def data(self) -> Optional[dict]:
        """Proprietà per accedere ai dati letti"""
        if self._data is None:
            self.read()
        return self._data

    @data.setter
    def data(self, value: dict):
        """Setta i dati manualmente"""
        self._data = value

    def exists(self) -> bool:
        """Verifica se il file pyproject.toml esiste"""
        return self.pyproject_path.exists()


# Funzioni di compatibilità per mantenere l'interfaccia esistente
def pyproject_read(git_root: str) -> Optional[dict]:
    """Funzione di compatibilità per pyproject_read esistente"""
    manager = PyProjectManager(git_root)
    return manager.read()

def pyproject_write(git_root: str, data: dict, f_execute: bool) -> None:
    """Funzione di compatibilità per pyproject_write esistente"""
    manager = PyProjectManager(git_root)
    manager.data = data
    manager.write(f_execute)

def pyproject_version(new_version: str, f_execute: bool, git_root: str):
    """Funzione di compatibilità per pyproject_version esistente"""
    manager = PyProjectManager(git_root)
    manager.set_version(new_version, f_execute)

def update_pyproject(new_version: str, f_execute: bool, git_root: str) -> bool:
    """Funzione di compatibilità per update_pyproject esistente"""
    manager = PyProjectManager(git_root)
    return manager.update_version(new_version, f_execute)


# Esempio di utilizzo
if __name__ == "__main__":
    # Utilizzo con la classe
    manager = PyProjectManager(".")
    print(f"Versione corrente: {manager.get_version()}")
    manager.set_version("1.0.0", f_execute=False)  # Dry-run

    # Utilizzo con le funzioni di compatibilità
    data = pyproject_read(".")
    if data:
        print(f"Dati letti: {data}")
        pyproject_version("2.0.0", f_execute=False, git_root=".")
        update_pyproject("3.0.0", f_execute=False, git_root=".")
