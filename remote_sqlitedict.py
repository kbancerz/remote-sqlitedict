import json
import os
import sys

import rpyc
from rpyc.core.protocol import PingError
from rpyc.utils.server import ThreadedServer
from sqlitedict import SqliteDict


# prevent JSON serialization issues by specifying and encoder
# see: https://github.com/tomerfiliba/rpyc/issues/393#issuecomment-662901702
def json_dumps(obj):
    return json.dumps(obj, indent=0)


DEF_PORT = 18753
PING_TIMEOUT = 1


class RemoteSQLiteDict(object):
    def __init__(self, host, port, db_name, autocommit):
        self._host = host
        self._port = port
        self._db_name = db_name
        self._autocommit = autocommit

        self._connection = None

    def __enter__(self):
        make_connection = False

        if self._connection is not None:
            try:
                self._connection.ping(timeout=PING_TIMEOUT)
            except (PingError, EOFError):
                make_connection = True
        else:
            make_connection = True

        if make_connection:
            self._connection = rpyc.connect(self._host, self._port, config={
                'allow_public_attrs': True,
                'allow_all_attrs': True,
            })

        return self._connection.root.proxy_sqlitedict(
            self._db_name, autocommit=self._autocommit)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()
        self._connection = None


def get_sqlitedict(host, port, db_name, autocommit=False):
    return RemoteSQLiteDict(host, port, db_name, autocommit=autocommit)


def start_server(port, db_root, single_db):
    # define new service with DB_ROOT set based on the parameter
    class SQLiteDictService(rpyc.Service):

        DB_ROOT = db_root

        def __init__(self):
            self._instance = None

        def exposed_proxy_sqlitedict(self, db_name, **kwargs):
            if single_db:
                db_path = os.path.join(self.DB_ROOT, '_root.sqlite')
            else:
                db_path = os.path.join(self.DB_ROOT, db_name + '.sqlite')

            self._instance = SqliteDict(
                db_path, tablename=db_name, encode=json_dumps,
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
        }
    ).start()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--single-db', '-s', action='store_true',
                        dest='single_db',
                        help='Save all data in a single database file')
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
    start_server(args.port, args.directory, args.single_db)
