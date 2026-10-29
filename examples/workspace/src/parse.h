#ifndef PARSE_H
#define PARSE_H

int parse_headers(char *body);
int copy_field(char *dst, const char *src, int len);

#endif
