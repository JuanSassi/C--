CC=gcc
NASM=nasm
CFLAGS=-g -Wall -m32
LDFLAGS=-m32

OBJ_C=c/interface.o
OBJ_ASM=asm/calculator.o
BIN=gini

all: $(BIN)

$(OBJ_ASM): asm/calculator.asm
	$(NASM) -f elf32 $< -o $@

$(OBJ_C): c/interface.c
	$(CC) $(CFLAGS) -c $< -o $@

$(BIN): $(OBJ_C) $(OBJ_ASM)
	$(CC) $(CFLAGS) $(OBJ_C) $(OBJ_ASM) -o $@ $(LDFLAGS)

# GDB puro con test especial
gdb-test: c/dep_gdb.o asm/calculator.o
	$(CC) $(CFLAGS) -o dep_test c/dep_gdb.o asm/calculator.o
	gdb -q ./dep_test

run:
	./$(BIN) 42.7

clean:
	rm -f c/*.o asm/*.o *.o $(BIN) dep_test