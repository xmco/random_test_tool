import os
import sys
import pkgutil
import importlib
import logging


def load_tests(path=os.path.dirname(__file__), prefix='statistical_tests.statistical_tests'):
    """
    Importe tous les statistical_tests statistiques.
    """

    for importer, name, ispkg in pkgutil.walk_packages([path]):
        try:
            pkg_name = f'{prefix}.{name}'
            if pkg_name not in sys.modules:
                importlib.import_module(pkg_name)
                logging.debug(f"Module {name} chargé")
            else:
                logging.debug(f"Module {name} déjà chargé")

            if ispkg:
                load_tests(os.path.join(path, name), pkg_name)

        except ImportError as error:
            logging.exception(error)