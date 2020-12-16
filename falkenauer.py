from pathlib import Path

documents_path = Path("Falkenauer/uniform")
instances_falkenauer = []
for document in documents_path.iterdir():
    with open(document) as f:
        content = f.readlines()
    instances_falkenauer.append([x.strip() for x in content])


    


