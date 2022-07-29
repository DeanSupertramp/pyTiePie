import argparse
import sys

class MyArgParser(argparse.ArgumentParser):

    def error(self, message):
        raise Exception(message)