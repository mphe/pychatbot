#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from context import *
from functools import partial

running = True

def cmd_exit(msg, argv):
    global running
    running = False

def cmd_echo(msg, argv):
    msg.get_chat().send_message(" ".join(argv[1:]))

def cmd_fail(msg, argv):
    return 2/0

def cmd_admin(msg, argv):
    msg.get_chat().send_message("Super secret admin command")

def cmd_missing(msg, self, *args):
    if len(args) == 0:
        return util.command.COMMAND_ERR_NOTFOUND
    else:
        msg.get_chat().send_message("Custom missing command handler: " + self)

def on_sent(msg):
    logging.info(str(msg))

def on_receive(cmd_handler, msg):
    try:
        cmd_handler.execute(msg)
    except Exception as e:
        logging.error(str(e))


def main():
    logging.info("Creating API object")
    apiobj = api.create_api_object("test", stub=False, interactive=True)

    cmd = util.command.CommandHandler()
    cmd.register("exit", cmd_exit, argc=0)
    cmd.register("echo", cmd_echo)
    cmd.register("fail", cmd_fail, argc=0)
    cmd.register("admin", cmd_admin, argc=0, flags=util.command.CMDFLAG_ADMIN)
    cmd.register(util.command.COMMAND_MISSING, cmd_missing, argc=0,
                 flags=util.command.CMDFLAG_EXPAND)

    disp = util.event.APIEventDispatcher(apiobj)
    disp.register(api.APIEvents.MessageSent, on_sent)
    disp.register(api.APIEvents.Message, partial(on_receive, cmd))

    logging.info("Attaching...")
    apiobj.attach()

    while running:
        apiobj.iterate()

    logging.info("Detaching...")
    disp.clear()
    apiobj.detach()
    logging.info("Done")


if __name__ == "__main__":
    main()
