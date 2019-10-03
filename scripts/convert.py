import json
import io
import os
import sys

def main():
    if len(sys.argv) < 2:
        print('sorry, need a file name')
        exit(1)
    file_name = sys.argv[1]

    path = os.path.basename(__file__)

    print('Current path', path)

    if not os.path.exists(file_name):
        print('Sorry, file does not exist')
        exit(1)

    print('Converting', file_name)

    with open(file_name) as file:
        schema = json.load(file)
        print(schema)

main()