#include "parse.h"

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>

static int read_message(int fd, char *buf, size_t cap)
{
    ssize_t got = recv(fd, buf, cap - 1, 0);

    if (got <= 0) {
        return -1;
    }
    buf[got] = '\0';
    return (int)got;
}

static int dispatch_route(char *path, char *body)
{
    if (strncmp(path, "/upload", 7) == 0) {
        return parse_headers(body);
    }
    return 0;
}

int handle_request(int fd)
{
    char buf[4096];

    if (read_message(fd, buf, sizeof(buf)) < 0) {
        return -1;
    }
    return dispatch_route(buf, buf);
}
