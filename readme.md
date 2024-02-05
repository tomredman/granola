# Granola

## Low-Overhead Distributed Transaction Coordination

### System designed by James Cowling for his PhD thesis at MIT
#### Thesis https://pmg.csail.mit.edu/papers/granola-thesis.pdf

## TODO
- [ ] Add a section on the Granola paper
- [ ] Add a section on the Granola implementation
- [ ] Add a section on the Granola evaluation
- [ ] Add a section on the Granola conclusion
- [ ] Add a section on the Granola future work

## Introduction
This is a naive implementation of the Granola system. The goal of this project is to understand the Granola system and to implement it in a simple way. The implementation is not meant to be used in production, but rather as a learning tool.

## Granola
Granola is a low-overhead distributed transaction coordination system. It is designed to be used in a distributed system where the overhead of a traditional two-phase commit protocol is too high. Granola is designed to be used in a system where the failure rate is low and the number of participants is high. Granola is designed to be used in a system where the participants are trusted and the system is not adversarial.

## Granola Paper
The Granola paper is a PhD thesis written by James Cowling at MIT. The paper is available at https://pmg.csail.mit.edu/papers/granola-thesis.pdf. The paper is a great resource for understanding the Granola system.

## Running the code
To run the code, you need to have Python 3 installed.

Start by running the transaction coordinator:
```
python transaction-coordinator.py
```

Then you can run the participants. You can run as many participants as you want. You can run the code by running the following command:
```
python granola.py --name repo1 --port 5001
python granola.py --name repo2 --port 5002
python granola.py --name repo3 --port 5003
```

And then you can run the client. You can run the code by running the following command:
```
python client.py --file test1.json
```

You can run multiple clients to see how the system behaves with concurrent connections:
```
python client.py --file test1.json
python client.py --file test1.json
python client.py --file test2.json
python client.py --file test3.json
python client.py --file test3.json
python client.py --file test3.json
```
