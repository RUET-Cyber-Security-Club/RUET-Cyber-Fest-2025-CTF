// fest.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Simple banner
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

void secret_function(void) {
    FILE *f = fopen("flag.txt", "r");
    if (!f) {
        puts("Could not open flag.txt");
        return;
    }

    char buf[256];
    size_t n = fread(buf, 1, sizeof(buf)-1, f);  
    buf[n] = '\0';

    printf(" FLAG: %s\n", buf);
    fclose(f);
}

void treasure_hunt() {
    puts("Treasure Hunt Instructions:");
    puts(" - Find physical clue at the registration desk.");
    puts(" - Decode the cipher on the poster.");
    puts(" - Bring decoded keyword to an organizer for a bonus artifact.\n");
}

void seminar() {
    puts("Seminar Info:");
    puts(" - 11:00: Secure Coding Basics");
    puts(" - 13:00: Binary Exploitation 101");
    puts(" - 15:00: Reverse Engineering Lab\n");
}

void quiz() {
    puts("Quick Quiz (no points, just for fun):");
    puts(" Q: What does ASLR stand for?\n");
    char answer[64];
    printf("Your answer: ");
    fgets(answer, sizeof(answer), stdin);
    if (strstr(answer, "address space layout randomization") ||
        strstr(answer, "Address Space Layout Randomization")) {
        puts("Correct! (But this won't help you get the flag).\n");
    } else {
        puts("Nice try. Research it—it matters for exploits!\n");
    }
}

void get_username() {
    char username[32];
    char tmp[256];

    puts("=== Play CTF ===");
    puts("Enter your CTF username:");

    if (!fgets(tmp, sizeof(tmp), stdin)) {
        puts("Input error.");
        return;
    }
    tmp[strcspn(tmp, "\n")] = '\0';

    strcpy(username, tmp);

    printf("Welcome, %s! Prepare to pwn.\n", username);
    puts("Ok then go and play CTF\n");
}

int main() {
    banner();

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    while (1) {
        puts("Menu:");
        puts(" 1. Play Treasure Hunt");
        puts(" 2. Play CTF");
        puts(" 3. Going to seminar");
        puts(" 4. Give quiz");
        puts(" 5. Exit");
        printf("Select option: ");

        char line[8];
        if (!fgets(line, sizeof(line), stdin)) {
            puts("Input error. Exiting.");
            return 1;
        }

        int choice = atoi(line);
        puts("");

        switch (choice) {
            case 1: treasure_hunt(); break;
            case 2: get_username(); break;   
            case 3: seminar(); break;
            case 4: quiz(); break;
            case 5: puts("Goodbye!"); return 0;
            default: puts("Invalid choice. Try again.\n");
        }
    }

    return 0;
}
