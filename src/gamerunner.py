#!/usr/bin/env python2
from server.server import MMServer
from subprocess import Popen
import config.handle_constants
import argparse
import game
import sys
import os
import pickle
import vis.visualizer
import time


FNULL = open(os.devnull, 'w')
constants = config.handle_constants.retrieveConstants("serverDefaults")
vis_constants = config.handle_constants.retrieveConstants("visualizerDefaults")

parameters = None
client_list = list()


def launch_clients():
    if parameters.client:
        numberOfClients = len(parameters.client)
        for client in parameters.client:
            launch_client(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'test-clients/', client))
    else:
        numberOfClients = 0
    for x in xrange(numberOfClients, parameters.teams):
        launch_client(os.path.join(os.getcwd(), parameters.defaultClient))


def launch_client(client):
        c = Client_program(client)
        c.run()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launches the server with p clients which "
        + "connect to it.")
    parser.add_argument(
        "-u", "--port",
        help="Specifies the port on which the server should run. " +
        "Defaults to {0}".format(constants["port"]),
        default=constants["port"],
        type=int)
    parser.add_argument(
        "-w", "--debug-view",
        help="Runs the debug view to help you find your problem!",
        const=True,
        default=False,
        action="store_const",
    )
    parser.add_argument(
        "-m", "--map",
        help="Specifies the map file on which the game should run. " +
        "Defaults to {0}".format(constants["map"]),
        default=constants["map"])
    parser.add_argument(
        "-o", "--mapOverlay",
        help="Specifies the overlay map file on which the game should be shown. " +
        "Defaults to {0}".format(vis_constants["map_overlay"]),
        default=vis_constants["map_overlay"])
    parser.add_argument(
        "-l", "--log",
        help="Specifies a log file where the game log will be written. " +
        "For example, ./gamerunner.py --log BUTT.out, Defaults to {0}".
        format(constants["log"]),
        default=constants["log"])
    parser.add_argument(
        "-t", "--teams",
        help="Specifies the number of teams. Defaults to {0}."
        .format(constants["players"]),
        default=constants["players"],
        type=int)
    parser.add_argument(
        "-c", "--client",
        help="Signifies this client to be run. " +
        "As an example ./gamerunner.py -p 3 -c myClient -c test_clients/python " +
        "The gamerunner will run a number of test clients (which can be " +
        "specified with -d) equal to players - specified clients",
        action="append")

    parser.add_argument(
        "-d", "--defaultClient",
        help="The default client to launch when no specific clients " +
        "are given. Defaults to {0}".format(constants["defaultClient"]),
        default=os.path.join(*constants["defaultClient"].split("/")))
    parser.add_argument(
        "-v", "--verbose",
        help="When present prints player one's standard output.",
        const=None,
        default=FNULL,
        action="store_const")
    parser.add_argument(
        "-vv", "--veryVerbose",
        help="When present prints all players standard output.",
        const=None,
        default=FNULL,
        action="store_const")

    parser.add_argument(
        "-s", "--show",
        help="Set this to make the game be visualized in a window." +
        "Fun to watch and helpful for debuging!",
        const=True,
        default=False,
        action="store_const")
    parser.add_argument(
        "-C", "--cached-map",
        help="Speeds up the launch time of the server by using a cached map. " +
        "If you are having any sort of problem try launching without this!",
        const=True,
        default=False,
        action="store_const")
    
    args = parser.parse_args()
    if args.teams < 2:
        sys.stdout.write(parser.format_usage())
        print "{0}: error: Cannot run with less than two players".format(
            parser.prog)
        exit(1)
    if args.client and len(args.client) > args.teams:
        sys.stdout.write(parser.format_usage())
        print "{0}: error: More clients specified than players".format(
            parser.prog)
        exit(1)
    return args


## A simple logger that writes things to a file and, if enabled, to the
## visualizer
class FileLogger(object):
    def __init__(self, fileName):
        self.file = fileName
        self.vis = False

    ## The function that logs will be sent to
    # @param stuff
    #   The stuff to be printed
    def print_stuff(self, stuff):
        with open(self.file, 'a') as f:
            f.write(stuff + '\n')
        if self.vis:
            self.vis.turn(stuff)
            

def main():
    global parameters
    parameters = parse_args()
    sys.stdout.write("Creating server with {0} players, ".format(
        parameters.teams))
    print "and {0} as the map\n".format(parameters.map)
    print "Running server on port {0}\n".format(parameters.port)
    print "Writing log to {0}".format(parameters.log)
    map_cache_str = "map.cache"
    with open(parameters.log, 'w'):
        pass
    fileLog = FileLogger(parameters.log)
    if os.path.isfile(map_cache_str) and parameters.cached_map:
        with open(map_cache_str, 'r') as f:
            rooms = pickle.load(f)
        my_game = game.Game(parameters.map, rooms)
        with open(map_cache_str, 'r') as f:
            rooms = pickle.load(f)
    else:
        my_game = game.Game(parameters.map)
        rooms_str = pickle.dumps(my_game.rooms)
        with open(map_cache_str, 'w') as f:
            f.write(rooms_str)
        rooms = pickle.loads(rooms_str)
    if parameters.show:
        fileLog.vis = vis.visualizer.Visualizer(rooms, parameters.mapOverlay, debug=parameters.debug_view)
    serv = MMServer(parameters.teams,
                    my_game,
                    logger=fileLog)
    serv.run(parameters.port, launch_clients)


class Client_program(object):
    """
    This object holds and manages the prosses for the
    connecting teams
    """
    first = True

    def __init__(self, client_path):
        """
        path of the client to run
        """
        self.client_path = client_path

    def run(self):
        """
        """
        try:
            self.bot = Popen(os.path.join(self.client_path, "run.sh"),
                             stdout=self.chose_output(), cwd=self.client_path)
        except OSError as e:
            msg = "the player {} failed to start with error {}".format(
                self.client_path, e)
            print msg
            raise ClientFailedToRun(msg)

    def kill(self):
        if not self.bot.poll():
            try:
                self.bot.kill()
            except OSError:
                pass

    def stop(self):
        """
        """
        self.bot.terminate()

    @classmethod
    def chose_output(cls):
        output = parameters.veryVerbose
        if cls.first and parameters.veryVerbose == FNULL:
            output = parameters.verbose

        cls.first = False
        return output

class ClientFailedToRun(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


if __name__ == "__main__":
    main()
