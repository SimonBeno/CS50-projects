// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

unsigned int counter = 0;
bool nacitane = false;

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // TODO
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        printf("Usage: ./speller dictionaries/dictionaryname texts/textname.txt");
        return 1;
    }

    int check;

    while (true)
    {

        char word[LENGTH + 1]; //creates a temporary array to store a new word
        if (fscanf(file, "%s", word) == EOF)
        {
            nacitane = true;
            fclose(file);
            return true;
        }

        node *n = malloc(sizeof(node));
        //inserting a new node
        if (n == NULL)
        {
            return 1;
        }

        strcpy(n -> word, word);

        if (counter == 0)
        {
            table[hash(word)] = n;
            n -> next = NULL;
        }
        else
        {
            n -> next = table[hash(word)];
            table[hash(word)] = n;
        }

        counter++;


    }

    return false;
}


// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    return toupper(word[0]) - 'A';
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    if (nacitane == true)
        return counter;
    else
        return 0;
}

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO
    node *cursor = table[hash(word)];

    while (cursor != NULL)
    {
        if (strcasecmp(cursor -> word, word) == 0)
        {
            cursor = NULL;
            return true;
        }
        else
            cursor = cursor -> next;
    }
    return false;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor -> next;
            free(tmp);
        }
    }

    return true;
}
