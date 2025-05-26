CFLAGS=-g -Wall

all: gini

gini: c/interface.c c/calculator.c
	$(CC) $(CFLAGS) $^ -o $@

run:
	./gini

gdb:
	gdb ./gini

clean:
	rm -f gini
