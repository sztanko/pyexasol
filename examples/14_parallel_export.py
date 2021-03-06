"""
Example 14
Parallel export into multiple independent processes
"""

import pyexasol as E
import _config as config

import multiprocessing
import pyexasol.callback as cb

import pprint
printer = pprint.PrettyPrinter(indent=4, width=140)


class ExportProc(multiprocessing.Process):
    def __init__(self, shard_id):
        self.shard_id = shard_id
        self.read_pipe, self.write_pipe = multiprocessing.Pipe(False)

        super().__init__()

    def start(self):
        super().start()
        self.write_pipe.close()

    def get_proxy(self):
        return self.read_pipe.recv()

    def run(self):
        self.read_pipe.close()

        http = E.http_transport(config.dsn, E.HTTP_EXPORT)
        self.write_pipe.send(http.get_proxy())
        self.write_pipe.close()

        pd = http.export_to_callback(cb.export_to_pandas, None)
        print(f'{self.shard_id}:{len(pd)}')


pool_size = 5
pool = list()
proxy_list = list()

C = E.connect(dsn=config.dsn, user=config.user, password=config.password, schema=config.schema)

for i in range(pool_size):
    proc = ExportProc(i)
    proc.start()

    proxy_list.append(proc.get_proxy())
    pool.append(proc)

printer.pprint(pool)
printer.pprint(proxy_list)

C.export_parallel(proxy_list, "SELECT * FROM payments", export_params={'with_column_names': True})

stmt = C.last_statement()
print(f'EXPORTED {stmt.rowcount()} rows in {stmt.execution_time}s')

for i in range(pool_size):
    pool[i].join()
