import argparse
import sys

class MyArgParser(argparse.ArgumentParser):

    def error(self, message):
        raise Exception(message)
        #self.print_help(sys.stderr)
        #self.exit(1, '%s: error: %s\n' % (self.prog, message))

