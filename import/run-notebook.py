import sys, json

# Get the notebook file path
if len(sys.argv) != 2:
    print("Usage: python run-notebook.py <notebook_path>")
    sys.exit(1)
else:
    nb_path = sys.argv[1]


nb_file = open(nb_path, 'r')
nb_file_content = nb_file.read()
nb_file.close()

nb = json.loads(nb_file_content)

for i, cell in enumerate(nb['cells']):

    if cell['cell_type'] == 'markdown':
        for line in cell['source']:
            print(line.strip())

    if cell['cell_type'] == 'code' and 'source' in cell:
        try:
            exec(''.join(cell['source']))
        except BaseException as error:
            print('')
            print(f'Error while running cell number {i}. Code is')
            for j, line in enumerate(cell['source']):
                print(str(j + 1).rjust(3) + ": " + line, end='')
            print('\n')
            raise error