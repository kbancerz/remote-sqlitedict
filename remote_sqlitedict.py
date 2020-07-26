import json
import os
import pickle
import sys

import rpyc
from rpyc.utils.server import ThreadedServer
from sqlitedict import SqliteDict


def pickle_dump(obj):
    return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(data):
    return pickle.loads(data)


# monkey-patch pickle in place of brine
rpyc.core.brine.dump = pickle_dump
rpyc.core.brine.load = pickle_load


DEF_PORT = 18753


def get_sqlitedict(host, port, db_name, autocommit=False):
    c = rpyc.connect(host, port, config={
            'allow_public_attrs': True,
            'allow_all_attrs': True,
            'allow_pickle': True,
        })
    return c.root.get_sqlitedict(db_name, autocommit=autocommit)


def start_server(port, db_root):
    # define new service with DB_ROOT set based on the parameter
    class SQLiteDictService(rpyc.Service):

        DB_ROOT = db_root

        def __init__(self):
            self._instance = None

        def exposed_get_sqlitedict(self, db_name, **kwargs):
            db_path = os.path.join(self.DB_ROOT, db_name + '.sqlite')
            self._instance = SqliteDict(
                db_path, tablename=db_name, encode=json.dumps,
                decode=json.loads, **kwargs)
            return self._instance

        def on_disconnect(self, conn):
            if self._instance is not None:
                self._instance.close()

    ThreadedServer(
        SQLiteDictService, port=port,
        protocol_config={
            'allow_public_attrs': True,
            'allow_all_attrs': True,
            'allow_pickle': True,
        }
    ).start()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', default=os.getcwd(),
                        help='Specify alternative directory '
                             '[default:current directory]')
    parser.add_argument('port', action='store',
                        default=DEF_PORT, type=int,
                        nargs='?',
                        help=f'Specify alternate port [default: {DEF_PORT}]')
    args = parser.parse_args()

    sys.stdout.write(f'Server starting on port {args.port}...')
    sys.stdout.flush()
    start_server(args.port, args.directory)
