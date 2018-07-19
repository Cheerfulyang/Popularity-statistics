#include <stdio.h>

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "DynamicCountFilter.h"
#include "util.c"

#define HASHLEN 1024


typedef struct poplist{
	unsigned char *key;
	struct poplist *next;
	struct poplist *pre;
}poplist;

typedef struct mylist{
	int maxSize;
	int curSize;
	int *hash;
	poplist *head;
	poplist *end;
}mylist;

unsigned generatehash(unsigned char *element){
	unsigned *hashAddress = (unsigned *)malloc(sizeof(unsigned));
        int Hash_Num = 1;
        if (!GenerateHashAddress(element, 3, HASHLEN, Hash_Num, hashAddress))
        {
                free(hashAddress);
                printf("error");
		return 0;
        }
//        printf("hash = %d\n", *hashAddress);
	return *hashAddress;
}

int remove_end(mylist *ml, poplist *k){
        if(ml->curSize == 0){
                return 0;
        }
        ml->end = k->pre;
        ml->end->next = NULL;
	ml->curSize--;
        return 1;
}


int insert_head(mylist *ml, poplist *k){
	int res = 0;
	ml->curSize++;
	unsigned hashAddress = generatehash(k->key);	
	ml->hash[hashAddress]++;
	if(ml->curSize > ml->maxSize){
		unsigned hashAddress = generatehash(ml->end->key);
		ml->hash[hashAddress]--;	
		res = remove_end(ml, ml->end);
	}
	if(ml->head == NULL && ml->end == NULL){
		ml->head = ml->end = k;
	}
	else{
		ml->head->pre = k;
		k->next = ml->head;
		k->pre = NULL;
		ml->head = k; 
		return res;
	}
}
/*
int query(mylist *ml, int num){
	poplist *k = ml->head;
	int count, j = 0;
	while(k){
		j++;
		if(k->key == num){
			count++;
		}
		k = k->next;
	}
	//printf("j = %d\n", j);
	return count;
}
*/

int queryhash(mylist *ml, unsigned char *str){
	unsigned hashAddress = generatehash(str);
	return ml->hash[hashAddress];
}


void main(){
	clock_t start, finish, end;
	int length = 10000;
	mylist *my_list = (mylist *)malloc(sizeof(mylist));
	my_list->maxSize = length;
	my_list->hash = (int *)malloc(sizeof(int)*10000);
	int my_array[100000] = {0};
	int i,j = 0;
	int m= 0;
	

        unsigned char **a;
        a = (unsigned char **)malloc(sizeof(unsigned char*)*10000);
        for(i = 0; i < 10000; i++){
                *(a+i) = (unsigned char *)malloc(sizeof(unsigned char)*3);
                for(j = 0; j<3; j++){
                        *((*(a+i))+j) = 'a'+rand()%10 ;
                }
        }

        unsigned len = 3;


	
	start = clock();

	i = 0;
	while(a[i]){
		poplist *k = (poplist *)malloc(sizeof(poplist));
		k->key = a[i];
        	insert_head(my_list, k);
		i++;
	}
/*

	for(j = 0; j<10000; j++){
		my_list->hash[j] = 0;
		m = rand()%10000 + 1;
		my_array[j] = m;
	//	printf("%d\n", my_array[j]);
	}	
	start = clock();
	while(my_array[i]){
		poplist *k = (poplist *)malloc(sizeof(poplist));
		k->key = my_array[i];
        	insert_head(my_list, k);
		//printf("%d times =  %d\n", my_array[i],query(my_list, 3)); 
		//printf("%d times =  %d\n", my_array[i],query(my_list, 100)); 
		i++;
	}

*/

	printf("i=%d\n", i);

	finish = clock();
	printf("insert clock = %lu\n", finish - start);
	i = 0;
	int t,q = 0;
	int hashres;
	
	while(a[i]){
                //printf("%d times =  %d\n", my_array[i],query(my_list, 3));
		
                queryhash(my_list, a[i]); 
                i++;
        }
	printf("i = %d\n", i);

	
	//printf("%d times =  %d\n", my_array[i],query(my_list, 3)); 
	end = clock();
	printf("size = %lu\n", sizeof(my_list->hash[0]));
	
	long int k;
	for(i = 0; i<HASHLEN ; i++){
		k+= sizeof(my_list->hash[i]);
	}
	printf("size = %lu\n", k);


	printf("query clock = %lu\n", end - finish);
	
}
