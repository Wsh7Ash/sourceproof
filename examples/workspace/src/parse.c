#include "parse.h"

#include <stdlib.h>
#include <string.h>

/* Copies exactly len bytes, because the caller is supposed to have validated
 * the length field against the buffer it actually received. */
int copy_field(char *dst, const char *src, int len)
{
    memcpy(dst, src, (size_t)len);
    return len;
}

int parse_headers(char *body)
{
    char field[64];
    int len;

    if (body == NULL) {
        return -1;
    }

    /* The decimal length is attacker-controlled and never compared with the
     * size of `field`, so copy_field copies past the end of the stack buffer. */
    len = atoi(body);
    return copy_field(field, body + 4, len);
}
