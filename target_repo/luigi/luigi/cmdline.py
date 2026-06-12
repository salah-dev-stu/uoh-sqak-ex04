import os
import argparse
import logging
import sys

import luigi.server
import luigi.process
import luigi.configuration
import luigi.interface


def luigi_run(argv=sys.argv[1:]):
    luigi.interface.run(argv, use_dynamic_argparse=True)


def luigid(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Central luigi server")
    parser.add_argument("--background", help="Run in background mode", action="store_true")
    parser.add_argument("--pidfile", help="Write pidfile")
    parser.add_argument("--logdir", help="log directory")
    parser.add_argument("--state-path", help="Pickled state file")
    parser.add_argument("--address", help="Listening interface")
    parser.add_argument("--port", default=8082, help="Listening port")

    opts = parser.parse_args(argv)

    if opts.state_path:
        config = luigi.configuration.get_config()
        config.set("scheduler", "state-path", opts.state_path)

    if opts.background:
        # daemonize sets up logging to spooled log files
        logging.getLogger().setLevel(logging.INFO)
        luigi.process.daemonize(
            luigi.server.run,
            api_port=opts.port,
            address=opts.address,
            pidfile=opts.pidfile,
            logdir=opts.logdir,
        )
    else:
        if opts.logdir:
            logging.basicConfig(
                level=logging.INFO,
                format=luigi.process.get_log_format(),
                filename=os.path.join(opts.logdir, "luigi-server.log"),
            )
        else:
            logging.basicConfig(level=logging.INFO, format=luigi.process.get_log_format())
        luigi.server.run(api_port=opts.port, address=opts.address)
