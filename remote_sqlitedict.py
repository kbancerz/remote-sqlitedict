import json
import os
import sys

import rpyc
from rpyc.utils.server import ThreadedServer
from sqlitedict import SqliteDict


# prevent JSON serialization issues by specifying and encoder
# see: https://github.com/tomerfiliba/rpyc/issues/393#issuecomment-662901702
def json_dumps(obj):
    return json.dumps(obj, indent=0)


DEF_PORT = 18753


def get_sqlitedict(host, port, db_name, autocommit=False):
    c = rpyc.connect(host, port, config={
            'allow_public_attrs': True,
            'allow_all_attrs': True,
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
