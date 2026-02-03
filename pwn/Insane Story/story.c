
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

void banner(void) {
    puts("██████╗  ██████╗███████╗ ██████╗");
    puts("██╔══██╗██╔════╝██╔════╝██╔════╝");
    puts("██████╔╝██║     ███████╗██║     ");
    puts("██╔══██╗██║     ╚════██║██║     ");
    puts("██║  ██║╚██████╗███████║╚██████╗");
    puts("╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝");
    puts("");
    puts("");
}

void story(void) {
 
    const size_t READ_SZ = 1024;
    char *buf = malloc(READ_SZ + 1); 
    if (!buf) {
        puts("Allocation failure.");
        return;
    }

    printf("Tell me a story: ");
    fflush(stdout);

    ssize_t n = read(STDIN_FILENO, buf, READ_SZ);
    if (n <= 0) {
        puts("\nNo input.");
        free(buf);
        return;
    }

    if (n > 0 && buf[n-1] == '\n') {
        buf[n-1] = '\0';
        --n;
    } else {
        buf[n] = '\0';
    }

    if ((size_t)n > 1000) {
        FILE *f = fopen("flag.txt", "r");
        if (f) {
            char flagline[1024];
            if (fgets(flagline, sizeof(flagline), f)) {
                printf("FLAG: %s\n", flagline);
            } else {
                puts("Flag file empty.");
            }
            fclose(f);
        } else {
            puts("Flag file not found.");
        }
    } 
    else if((size_t)n > 400){
        puts("Hmm, not bad, but still i am not impresed.");
    }
    else {
        puts("Ahh! You are too boring. Don't waste my time!");
    }

    free(buf);
}

int main(void) {
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    banner();
    story();
    return 0;
}
