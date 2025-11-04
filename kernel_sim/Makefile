CC=gcc
CFLAGS=-std=c11 -Wall -Wextra -O2 -I.
SRCS=main.c vfs_fd.c fs.c process.c shell.c
OBJS=$(SRCS:.c=.o)
TARGET=kernel_sim

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)


examples: examples/simple_user examples/vfs_user

examples/simple_user: examples/simple_user.c
	$(CC) $(CFLAGS) -o examples/simple_user examples/simple_user.c

examples/vfs_user: examples/vfs_user.c vfs_fd.o fs.o process.o
	$(CC) $(CFLAGS) -o examples/vfs_user examples/vfs_user.c vfs_fd.o fs.o process.o

clean:
	rm -f $(OBJS) $(TARGET)
