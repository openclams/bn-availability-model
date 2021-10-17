// Disable deprecation warning from numpy
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <stdio.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <time.h>
#include <pthread.h>


typedef struct Graph Graph;
typedef struct Node Node;
typedef struct Stack Stack;
typedef npy_intp dom_size;

typedef struct {
    int tid;
    Graph *graph;
    long n_samples;
    long* frequencies;
} ThreadArgs;

struct Graph{
    Node *nodes;
    Py_ssize_t n_nodes;
    Node **sorted_nodes;
    Py_ssize_t n_sorted_nodes;
};

struct Node{
    Py_ssize_t index;
    Graph *graph;
    PyObject *name;
    PyObject *cpd;
    dom_size cardinality;
    Node **parents;
    Py_ssize_t n_parents;
    Node **children; // Array
    Py_ssize_t n_children;
};

pthread_mutex_t lock;

void freeGraph(Graph *graph){

      if(graph->sorted_nodes){
        free(graph->sorted_nodes);
      }

      for(Py_ssize_t i = 0; i< graph->n_nodes; i++){

            Py_DECREF(graph->nodes[i].cpd);

            Py_DECREF(graph->nodes[i].name);

      }

      free(graph->nodes);

      free(graph);
}

struct Stack {
    int top;
    Py_ssize_t capacity;
    Node **array;
};

void freeStack(Stack *stack){
    free(stack->array);
    free(stack);
}


struct Stack* createStack(Py_ssize_t capacity){
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


void linkAdjacentNodes(PyObject *bn_obj, Graph *graph, int b_parents){

        Node  *nodes;

        PyObject    *bn_nodes,
                    *bn_node,
                    *bn_iterator,
                    *bn_get_parents,
                    *bn_get_children,
                    *bn_get_method;


        Py_ssize_t  n = 0,
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
                                // PyObject_Print(nodes[g].name, stdout, 0);
                                //PyObject_Print(nodes[i].children[j].name, stdout, 0);
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

Graph * buildGraph(PyObject *bn_obj){

    Graph *graph;

    PyObject    *bn_nodes,
                *bn_node,
                *bn_get_cpds,
                *bn_cpd,
                *bn_iterator,
                *bn_cardinality;

    Py_ssize_t  n = 0,
                i = 0;



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

         graph->nodes[i].cpd = bn_cpd;

         graph->nodes[i].cardinality = *((int *)PyArray_GETPTR1((PyArrayObject *)bn_cardinality, 0));

         graph->nodes[i].parents = NULL;

         graph->nodes[i].children = NULL;

         i++;

         Py_DECREF(bn_cardinality);

         Py_DECREF(bn_node);
    }

    Py_DECREF(bn_iterator);
    Py_DECREF(bn_nodes);

    linkAdjacentNodes(bn_obj, graph, 1);
    linkAdjacentNodes(bn_obj, graph, 0);

    Py_DECREF(bn_get_cpds);
    Py_DECREF(bn_obj);

    return graph;
}

double nparams(Graph *graph){

    PyObject *bn_cardinality_array;

    Py_ssize_t i;
    Py_ssize_t n = graph->n_sorted_nodes;

    double total = 0.0;

    for(i = 0; i < n; i++){

        bn_cardinality_array = PyObject_GetAttrString(graph->sorted_nodes[i]->cpd, "cardinality");

        PyObject *res = PyArray_Prod((PyArrayObject *)bn_cardinality_array, NPY_MAXDIMS, PyArray_DESCR((PyArrayObject *)bn_cardinality_array)->type_num, NULL);

        total += PyFloat_AsDouble(res);

        Py_DECREF(bn_cardinality_array);
        Py_DECREF(res);
    }

    return total;
}


void display(Graph *graph, int show){

       for(Py_ssize_t i = 0; i< graph->n_sorted_nodes; i++){

            if(show){
                PyObject_Print(graph->nodes[i].name, stdout, 0);
            }else{
                PyObject_Print(graph->sorted_nodes[i]->name, stdout, 0);
            }
//            PyObject_Print(PyLong_FromLong(graph->nodes[i].n_children), stdout, 0);
//
//            for(Py_ssize_t j = 0; j< graph->nodes[i].n_children; j++){
//
//                PyObject_Print(graph->nodes[i].children[j]->name, stdout, 0);
//
//            }
            //PyObject_Print(PyUnicode_FromString(" "), stdout, 0);
       }

}

long observation(Node *node, dom_size *evidence){
    PyObject *bn_value_array;
    double choice = (double) rand()/RAND_MAX;

    //printf("g\n");
  PyGILState_STATE gstate;
  gstate = PyGILState_Ensure();
  // printf("h\n");
////
  // bn_value_array = PyObject_GetAttrString(node->cpd, "values");
//
  // Py_DECREF(bn_value_array);
////
////printf("j\n");
  PyGILState_Release(gstate);

    return 0;

    npy_intp *indexes = malloc((node->n_parents + 1) * sizeof(npy_intp));

    double sum = 0;

    for(npy_intp i = 0; i < node->cardinality; i++){

        indexes[0] = i;

        for(long j = 0; j < node->n_parents; j++){

            indexes[j+1] = evidence[node->parents[j]->index];

        }


        sum += *((double*)PyArray_GetPtr((PyArrayObject *)bn_value_array, indexes));


        if(choice <= sum){

            free(indexes);

            Py_DECREF(bn_value_array);

            return i;

        }
    }

    return 0;
}

long sample(Graph *graph, dom_size *evidence){

     Node *node;

     for(Py_ssize_t i = 0; i < graph->n_sorted_nodes; i++){

        node = graph->sorted_nodes[i];

        evidence[node->index] = observation(node, evidence);

     }
      //  printf("%ls\n",PyUnicode_AsUnicode(node->name));
     return evidence[node->index];
}



void* compute_samples(void *args)
{
    ThreadArgs *param = (ThreadArgs *) args;

    //printf("%i\n",param->tid);
    fflush(stdout);
    long *frequencies = param->frequencies;

    long n_samples = param->n_samples;

    Graph *graph = param->graph;

    dom_size *evidence = (dom_size *)malloc(graph->n_sorted_nodes * sizeof(dom_size));

    for(Py_ssize_t i = 0; i< graph->n_sorted_nodes; i++){

        evidence[i] = 0;

    }

    for(long i = 0; i< n_samples; i++){

        long ev = sample(graph, evidence);
        //printf("[%i]\n ",param->tid);
         //fflush(stdout);
        //pthread_mutex_lock(&lock);

        frequencies[ev] += 1;

        //pthread_mutex_unlock(&lock);
   }

    printf("%i end\n ",param->tid);
    fflush(stdout);

    free(evidence);

   // pthread_exit(NULL);
    return NULL;
}


static PyObject* cpdist(PyObject* self, PyObject *args) {

   PyEval_InitThreads();

    int num_cores = 6;

    int error;

    time_t t;

    srand((unsigned) time(&t));

    PyObject *node_name;
    PyObject *bn_obj;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "OO", &bn_obj,&node_name)){
        return NULL;
        }


 //

//PyThreadState *_save;
//
//_save = PyEval_SaveThread();

   Graph *graph = buildGraph(bn_obj);

   graph->n_sorted_nodes = graph->n_nodes;

   graph->sorted_nodes = (Node **)malloc(graph->n_sorted_nodes * sizeof(Node*));

   Stack *stack = topologicalSort(graph);

   for(Py_ssize_t i = 0; i< graph->n_sorted_nodes; i++){

        Node *temp_node = pop(stack);

        graph->sorted_nodes[i] = temp_node;
   }

   long n_samples = (long)((5000.0 * log10(nparams(graph)))/num_cores);

   dom_size cardinality = graph->sorted_nodes[graph->n_sorted_nodes - 1]->cardinality;

   long *frequencies = malloc(cardinality * sizeof(long));

   for(dom_size i = 0; i< cardinality; i++){
        frequencies[i] = 0;
   }

   for(Py_ssize_t c = 0; c < graph->n_sorted_nodes; c++){
         if(PyUnicode_Compare(graph->sorted_nodes[c]->name,node_name) == 0){
            graph->n_sorted_nodes = c+1;
            break;
         }
   }

    if (pthread_mutex_init(&lock, NULL) != 0) {
        printf("\n mutex init has failed\n");
        return Py_None;
    }

    pthread_t *worker = malloc(num_cores * sizeof(pthread_t));

    ThreadArgs *param = malloc(num_cores * sizeof(ThreadArgs));
 Py_BEGIN_ALLOW_THREADS
     for(int i = 0; i < num_cores; i++) {

        param[i].n_samples = n_samples;
        param[i].frequencies = frequencies;
        param[i].graph = graph;
        param[i].tid = i;

        error = pthread_create(worker + i,
                               NULL,
                               &compute_samples,
                               param + i);

        if (error != 0)
            printf("\nThread can't be created :[%s]",
                   strerror(error));
    }

    for(int i = 0; i < num_cores; i++) {
        printf("fin %i\n",i);
        fflush(stdout);
        pthread_join(worker[i], NULL);

    }
Py_END_ALLOW_THREADS
//PyEval_RestoreThread(_save);

   // pthread_mutex_destroy(&lock);

   result = PyList_New(cardinality+1);

   for(dom_size i = 0; i< cardinality; i++){

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

//int
//main(int argc, char *argv[])
//{
//    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
//    if (program == NULL) {
//        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
//        exit(1);
//    }
//
//    /* Add a built-in module, before Py_Initialize */
//    if (PyImport_AppendInittab("bnlearn", PyInit_bnlearn) == -1) {
//        fprintf(stderr, "Error: could not extend in-built modules table\n");
//        exit(1);
//    }
//    //import_array();
//
//
//    /* Pass argv[0] to the Python interpreter */
//    Py_SetProgramName(program);
//
//    /* Initialize the Python interpreter.  Required.
//       If this step fails, it will be a fatal error. */
//    Py_Initialize();
//    import_array();
//
//    /* Optionally import the module; alternatively,
//       import can be deferred until the embedded script
//       imports it. */
//    PyObject *pmodule = PyImport_ImportModule("bnlearn");
//    if (!pmodule) {
//        PyErr_Print();
//        fprintf(stderr, "Error: could not import module 'spam'\n");
//    }
//
//    PyMem_RawFree(program);
//    return 0;
//}
