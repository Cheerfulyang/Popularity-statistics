#include <stdio.h>

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "DynamicCountFilter.h"
#include "util.c"



typedef struct poplist{
	int key;
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
	ml->hash[k->key]++;
	if(ml->curSize > ml->maxSize){
		ml->hash[ml->end->key]--;	
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

int queryhash(mylist *ml, int num){
	return ml->hash[num];
}


void main(){
	clock_t start, finish, end;
	int length = 10000;
	mylist *my_list = (mylist *)malloc(sizeof(mylist));
	my_list->maxSize = length;
	my_list->hash = (int *)malloc(sizeof(int)*10000);
//	m_list->hash = {0};
	int my_array[100000] = {0};
	int i,j = 0;
	int m= 0;
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
	printf("i=%d\n", i);
	finish = clock();

	printf("insert clock = %lu\n", finish - start);
	i = 0;
	int t,q = 0;
	int hashres;
	while(my_array[i]){
                //printf("%d times =  %d\n", my_array[i],query(my_list, 3));
		t = my_array[i];
		while(t){
			q = t%10;
			t = t/10;
			hashres = hashres*68569 + q;
			q = 3751* 689;
			
		}
                queryhash(my_list, my_array[i]); 
                i++;
        }
	printf("i = %d\n", i);
	int Hash_Num = 1;
	unsigned char * element = "number";
	unsigned *hashAddress = (unsigned *)malloc(sizeof(unsigned) * Hash_Num);
	if (!GenerateHashAddress(element, 6, 8, Hash_Num, hashAddress))
	{
		free(hashAddress);
		printf("error");
	}
	printf("hash = %d\n", *hashAddress);
	//printf("%d times =  %d\n", my_array[i],query(my_list, 3)); 
	end = clock();
	printf("query clock = %lu\n", end - finish);
	free(hashAddress);
	
}
