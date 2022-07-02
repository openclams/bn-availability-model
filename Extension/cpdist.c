// Disable deprecation warning from numpy
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <stdio.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include <string.h>

typedef struct Graph Graph;
typedef struct Node Node;
typedef struct Stack Stack;


typedef struct {
    int tid;
    Graph *graph;
    int n_samples;
    int *frequencies;
} ThreadArgs;

struct Graph{
    Node *nodes;
    int n_nodes;
    Node **sorted_nodes;
    int n_sorted_nodes;
};

struct Node{
    int index;
    Graph *graph;
    PyObject *name;
    double *cpd;
    int n_cpd;
    int cardinality;
    Node **parents;
    int n_parents;
    Node **children; // Array
    int n_children;
    //long *indexes;
};

pthread_mutex_t lock;

void freeGraph(Graph *graph){

      if(graph->sorted_nodes){
        free(graph->sorted_nodes);
      }

      for(int i = 0; i< graph->n_nodes; i++){

            free(graph->nodes[i].parents);

            free(graph->nodes[i].children);

            //free(graph->nodes[i].cpd)

            //free(graph->nodes[i].indexes);
            if(graph->nodes[i].name){
                Py_DECREF(graph->nodes[i].name);
            }
      }

      free(graph->nodes);

      free(graph);
}

Graph * copyGraph(Graph *graph){
    Graph *graph_copy = malloc(sizeof(Graph));

    memcpy(graph_copy,graph,sizeof(Graph));

    graph_copy->nodes = malloc(graph->n_nodes * sizeof(Node));

    memcpy(graph_copy->nodes,graph->nodes,graph->n_nodes * sizeof(Node));

    for(int i = 0; i< graph->n_nodes; i++){
        graph_copy->nodes[i].graph = graph_copy;

        graph_copy->nodes[i].name = NULL;

        memcpy(graph_copy->nodes[i].cpd,graph->nodes[i].cpd,graph->nodes[i].n_cpd*sizeof(double));

        graph_copy->nodes[i].parents = malloc(graph->nodes[i].n_parents * sizeof(Node*));
        for(int a = 0; a< graph->nodes[i].n_parents; a++){
            graph_copy->nodes[i].parents[a] = &graph_copy->nodes[graph->nodes[i].parents[a]->index];
        }

        graph_copy->nodes[i].children = malloc(graph->nodes[i].n_children * sizeof(Node*));
        for(int b = 0; b< graph->nodes[i].n_children; b++){
           graph_copy->nodes[i].children[b] = &graph_copy->nodes[graph->nodes[i].children[b]->index];
        }
    }

     for(int i = 0; i< graph->n_nodes; i++){
            graph_copy->sorted_nodes[i] = &graph_copy->nodes[graph->sorted_nodes[i]->index];
     }

     return graph_copy;
}

struct Stack {
    int top;
    int capacity;
    Node **array;
};

void freeStack(Stack *stack){
    free(stack->array);
    free(stack);
}


struct Stack* createStack(int capacity){
    Stack* stack = (Stack *)malloc(sizeof(Stack));
    stack->capacity = capacity;
    stack->top = -1;
    stack->array = (Node **)malloc(stack->capacity * sizeof(void *));
    return stack;
}

// Stack is full when top is equal to the last index
int isFull(Stack* stack){
    return stack->top == stack->capacity - 1;
}

// Stack is empty when top is equal to -1
int isEmpty(Stack* stack){
    return stack->top == -1;
}

void push( Stack* stack, Node *item){
    if (isFull(stack))
        return;
    stack->top++;
    stack->array[stack->top] = item;
}

Node* pop( Stack* stack){
    return stack->array[stack->top--];
}


int isIn(Stack* stack, Node *item){
    if(isEmpty(stack))
        return 0;
    for(int i = 0; i <= stack->top; i++){
        if(PyUnicode_Compare(stack->array[i]->name,item->name) == 0)
            return 1;
    }
    return 0;
}

void topologicalSortRec(Node *node, Stack* visited,  Stack* stack){
    push(visited, node);

    for (int i = 0; i < node->n_children; i++){

       if (!isIn(visited, node->children[i])){

            topologicalSortRec(node->children[i], visited, stack);
        }
    }

    push(stack, node);
}

Stack *topologicalSort(Graph *graph){

    Stack *stack = createStack(graph->n_nodes);

    Stack* visited = createStack(graph->n_nodes);

    for (int i = 0; i < graph->n_nodes; i++){

        if (!isIn(visited, &graph->nodes[i])){

            topologicalSortRec(&graph->nodes[i], visited, stack);

        }
    }

    freeStack(visited);

    return stack;
}



int printError(char * text){

      if (PyErr_Occurred()) {

        PyObject_Print(PyUnicode_FromString(text), stdout, 0);

        PyErr_PrintEx(0);

        PyErr_Clear();

        return 1;
      }
      return 0;
}


void linkAdjacentNodes(PyObject *bn_obj, Graph *graph, int b_parents, int num_cores){

        Node  *nodes;

        PyObject    *bn_nodes,
                    *bn_node,
                    *bn_iterator,
                    *bn_get_parents,
                    *bn_get_children,
                    *bn_get_method;


        int         n = 0,
                    i = 0,
                    j = 0,
                    g = 0,
                    num_nodes = 0;


        bn_get_parents = PyUnicode_FromString("get_parents");

        bn_get_children = PyUnicode_FromString("get_children");

       if(b_parents){
          bn_get_method =  bn_get_parents;
       }else{
          bn_get_method =  bn_get_children;
       }

        n = graph->n_nodes;

        nodes = graph->nodes;

        for(i = 0; i < n; i++){

            bn_nodes =  PyObject_CallMethodOneArg(bn_obj,
                                    bn_get_method,
                                    nodes[i].name);

            if(!bn_nodes || printError("nodes_list")){
                PyObject_Print(bn_nodes, stdout, 0);
            }

            bn_iterator = PyObject_GetIter(bn_nodes);

            num_nodes = 0;

            while((bn_node = PyIter_Next(bn_iterator))){
                num_nodes++;
                Py_DECREF(bn_node);
            }
            Py_DECREF(bn_iterator);
            Py_DECREF(bn_nodes);

            if(b_parents){
                 nodes[i].n_parents =  num_nodes ;
            }else{
                 nodes[i].n_children =  num_nodes ;
            }

            if(num_nodes){

                if(b_parents){
                     nodes[i].parents = (Node **)malloc(num_nodes * sizeof(void*));

                     //nodes[i].indexes = malloc((num_nodes + 1) * sizeof(long) * num_cores);

                }else{
                     nodes[i].children = (Node **)malloc(num_nodes * sizeof(void*));
                }

                bn_nodes =  PyObject_CallMethodOneArg(bn_obj,
                                bn_get_method,
                                nodes[i].name);

                bn_iterator = PyObject_GetIter(bn_nodes);

                j = 0;

                while((bn_node = PyIter_Next(bn_iterator))){

                    for(g = 0; g< n; g++){

                   // If 0 then equal!
                       if(PyUnicode_Compare(nodes[g].name,bn_node) == 0){

                            if(b_parents){
                                nodes[i].parents[j]  = &nodes[g];
                            }else{
                                nodes[i].children[j]  = &nodes[g];

                            }
                        }

                    }
                  j++;
                  Py_DECREF(bn_node);
               }
               Py_DECREF(bn_iterator);

            }

            Py_DECREF(bn_nodes);
        }

        Py_DECREF(bn_get_parents);
        Py_DECREF(bn_get_children);
}

Graph * buildGraph(PyObject *bn_obj,int num_cores){

    Graph *graph;

    PyObject    *bn_nodes,
                *bn_node,
                *bn_get_cpds,
                *bn_cpd,
                *bn_iterator,
                *bn_cardinality;

    int  n = 0;
    int  i = 0;

    bn_get_cpds = PyUnicode_FromString("get_cpds");

    graph = (Graph *)malloc(sizeof(Graph));

    Py_INCREF(bn_obj);

    bn_nodes = PyObject_CallMethod(bn_obj,"nodes", NULL);

    n = PyObject_Length(bn_nodes);

    graph->n_nodes = n;

    graph->nodes = (Node *)malloc(n * sizeof(Node));

    if(!graph->nodes){

        PyObject_Print(PyLong_FromLong(-1), stdout, 0);

        return NULL;
    }

    bn_iterator = PyObject_GetIter(bn_nodes);

    while((bn_node = PyIter_Next(bn_iterator))){

         bn_cpd =  PyObject_CallMethodOneArg(bn_obj,bn_get_cpds,bn_node);

         PyObject *bn_cpd_values = PyObject_GetAttrString(bn_cpd, "values");

         if(!bn_cpd || printError("get_cpds")){
            PyObject_Print(bn_cpd, stdout, 0);
         }

         bn_cardinality = PyObject_GetAttrString(bn_cpd, "cardinality");

         if(!bn_cardinality || printError("cardinality")){
            PyObject_Print(bn_cardinality, stdout, 0);
         }

         graph->nodes[i].index = i;

         graph->nodes[i].graph = graph;

         graph->nodes[i].name = bn_node;
         Py_INCREF(bn_node);

         // Copy CPD for performance reasons when multiple processes are called
         graph->nodes[i].n_cpd = PyArray_SIZE((PyArrayObject *) bn_cpd_values);

         //graph->nodes[i].cpd = malloc( graph->nodes[i].n_cpd *sizeof(double));

         //double *src_cpd
         graph->nodes[i].cpd =  (double *) PyArray_DATA((PyArrayObject *) bn_cpd_values);

         //memcpy(graph->nodes[i].cpd,src_cpd,graph->nodes[i].n_cpd*sizeof(double));

         graph->nodes[i].cardinality = *((int *)PyArray_GETPTR1((PyArrayObject *)bn_cardinality, 0));

         graph->nodes[i].parents = NULL;

         graph->nodes[i].children = NULL;

         i++;

         Py_DECREF(bn_cardinality);

         Py_DECREF(bn_node);
    }

    Py_DECREF(bn_iterator);
    Py_DECREF(bn_nodes);

    linkAdjacentNodes(bn_obj, graph, 1, num_cores);
    linkAdjacentNodes(bn_obj, graph, 0, num_cores);

    Py_DECREF(bn_get_cpds);
    Py_DECREF(bn_obj);

    return graph;
}

double nparams(Graph *graph){

    int i;
    int n = graph->n_sorted_nodes;

    double total = 1.0;

    for(i = 0; i < n; i++){

        total = graph->sorted_nodes[i]->cardinality;


        for(int j = 0; i < graph->sorted_nodes[i]->n_parents; j++){

            total *= graph->sorted_nodes[i]->parents[j]->cardinality;

        }
    }

    return total;
}


double get_value(Node *node, int* indexes){
    int position = 0;

    if(node->n_parents == 0){
        position = indexes[0];
    }else if(node->n_parents == 1){
        position =   node->parents[0]->cardinality*indexes[0]
                   + indexes[1];
    }else if(node->n_parents == 2){
        position =   node->parents[1]->cardinality *  node->parents[0]->cardinality * indexes[0]
                   + node->parents[1]->cardinality *  indexes[1]
                   + indexes[2];
    }else{
        int prod = 1;
        for(int i = 0; i <= node->n_parents; i++){

           prod = 1;

            for(int j = i; j < node->n_parents; j++){

                prod = prod * node->parents[j]->cardinality;

            }

            position += prod * indexes[i];
        }
    }
    return node->cpd[position];
}


int observation(Node *node, int *evidence, int tid){

    double choice = (double) rand()/RAND_MAX;

    int indexes[40]; //= node->indexes + (tid * (node->n_parents+1));

    double sum = 0;

    for(int i = 0; i < node->cardinality; i++){

        indexes[0] = i;

        for(long j = 0; j < node->n_parents; j++){

           indexes[j+1] = evidence[node->parents[j]->index];

        }

        double value = get_value(node, indexes);

        sum += value;

        if(choice <= sum){
            return i;
       }
  }

    return 0;
}

long sample(Graph *graph, int *evidence, int tid){

     Node *node;

     for(int i = 0; i < graph->n_sorted_nodes; i++){

        node = graph->sorted_nodes[i];

        evidence[node->index] = observation(node, evidence, tid);

     }

     return evidence[node->index];
}


void* compute_samples(void *args)
{
    ThreadArgs *param = (ThreadArgs *) args;

    int tid = param->tid;

    int *frequencies = param->frequencies;

    long n_samples = param->n_samples;

    Graph *graph = param->graph;

    int cardinality = graph->sorted_nodes[graph->n_sorted_nodes - 1]->cardinality;

    for(int i = 0; i< cardinality; i++){
        frequencies[i] = 0;
    }

    int *evidence = (int *)malloc(graph->n_nodes * sizeof(int));

    for(int i = 0; i < graph->n_sorted_nodes; i++){

        evidence[i] = 0;

    }

    for(long i = 0; i< n_samples; i++){

       int ev = sample(graph, evidence, tid);

       frequencies[ev] += 1;

   }

    free(evidence);

    //free(graph);

    return NULL;
}


//void show(Node *node){
//    int clac = 1;
//
//    printf("%ls: \n\t\t",PyUnicode_AsUnicode(node->name));
//
//    for(int j = 0; j < node->n_parents; j++){
//       clac *= node->parents[j]->cardinality;
//
//       printf("%ls\t",PyUnicode_AsUnicode(node->parents[j]->name));
//    }
//    printf("\n\t\t");
//
//    for(int c = 0; c < clac * node->cardinality; c++){
//        printf("%f ",node->cpd[c]);
//        if (c % clac == clac-1){
//            printf("|\n\t\t");
//        }
//    }
////    printf("\n");
//}

static PyObject* cpdist(PyObject* self, PyObject *args) {

    int num_cores;

    int error;

    time_t t;

    srand((unsigned) time(&t));

    PyObject *node_name;
    PyObject *bn_obj;
    PyObject *result;
    PyObject *cores;

    if (!PyArg_ParseTuple(args, "OOO", &bn_obj,&node_name,&cores)){
        return NULL;
        }

    num_cores = PyLong_AsLong(cores);

   Graph *graph = buildGraph(bn_obj,num_cores);

   graph->n_sorted_nodes = graph->n_nodes;

   graph->sorted_nodes = (Node **)malloc(graph->n_sorted_nodes * sizeof(Node*));

   Stack *stack = topologicalSort(graph);

   for(int i = 0; i< graph->n_sorted_nodes; i++){

        Node *temp_node = pop(stack);

        graph->sorted_nodes[i] = temp_node;

        //show(temp_node);
   }

   long n_samples = (long)((10000.0 * log10(nparams(graph))));

   int cardinality = graph->sorted_nodes[graph->n_sorted_nodes - 1]->cardinality;

   int *frequencies = malloc(cardinality * sizeof(int));
    for(int i = 0; i< cardinality; i++){
        frequencies[i] = 0;
    }


   for(int c = 0; c < graph->n_sorted_nodes; c++){
         if(PyUnicode_Compare(graph->sorted_nodes[c]->name,node_name) == 0){
            graph->n_sorted_nodes = c+1;
            break;
         }
   }

    pthread_t *worker = malloc(num_cores * sizeof(pthread_t));

    ThreadArgs *param = malloc(num_cores * sizeof(ThreadArgs));

     Py_BEGIN_ALLOW_THREADS

     for(long i = 1; i < num_cores; i++) {

        param[i].n_samples = n_samples/num_cores;
        param[i].frequencies = malloc(cardinality * sizeof(int));

        param[i].graph = graph;
        param[i].tid = i;

        error = pthread_create(worker + i,
                               NULL,
                               &compute_samples,
                               &param[i]);

        if (error != 0)
            printf("\nThread can't be created :[%s]",
                   strerror(error));
    }

    param[0].n_samples = n_samples/num_cores;
    param[0].frequencies = malloc(cardinality * sizeof(int));

    param[0].graph = graph;
    param[0].tid = 0;
    compute_samples(&param[0]);

    for(int i = 1; i < num_cores; i++) {
        pthread_join(worker[i], NULL);
    }

    for(long i = 0; i < num_cores; i++) {
       for(int j = 0; j< cardinality; j++){
            frequencies[j] += param[i].frequencies[j];
       }
    }

     for(long i = 0; i < num_cores; i++) {
       free(param[i].frequencies);
    }

    Py_END_ALLOW_THREADS

    free(param);

   result = PyList_New(cardinality+1);

   for(int i = 0; i< cardinality; i++){

        PyList_SetItem(result, i, PyLong_FromLong(frequencies[i]));

   }

   PyList_SetItem(result, cardinality, PyLong_FromLong(n_samples));

   freeGraph(graph);

   freeStack(stack);

   free(frequencies);

   return result;
}


static PyMethodDef funcs[] = {
   {"cpdist", (PyCFunction)cpdist,
      METH_VARARGS, ""},
      {NULL, NULL, 0, NULL}        /* Sentinel */
};

/**
 * Define the module. Its name will be 'cpdist'
 */
static struct PyModuleDef cpdist_module = {
    PyModuleDef_HEAD_INIT,
    "cpdist",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables.
                 This module is stateless, subsequent calls are new.
                 */
    funcs
};

/**
 * Create module, interpreter searches for this function first.
 */
PyMODINIT_FUNC PyInit_cpdist(void)
{
    PyObject *module = PyModule_Create(&cpdist_module);

    import_array();

    return module;
}