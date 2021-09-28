#include <Python.h>
#include <stdio.h>
#include <numpy/arrayobject.h>

typedef struct Graph Graph;
typedef struct Node Node;

struct Graph{
    Node *nodes;
    Py_ssize_t n_nodes;
    Node *sorted_nodes;
    Py_ssize_t n_sorted_nodes;
};

struct Node{
    Graph *graph;
    PyObject *name;
    PyObject *cpd;
    long cardinality;
    long evidence;
    Node *parents;
    Py_ssize_t n_parents;
    Node *children; // Array
    Py_ssize_t n_children;
};



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

        bn_get_method = b_parents ? bn_get_parents : bn_get_children;


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

            if(b_parents){
                 nodes[i].n_parents =  num_nodes ;
            }else{
                 nodes[i].n_children =  num_nodes ;
            }

            if(num_nodes){

                if(b_parents){
                     nodes[i].parents = (Node *)malloc(num_nodes * sizeof(Node));
                }else{
                    nodes[i].children = (Node *)malloc(num_nodes * sizeof(Node));
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
                                 nodes[i].parents[j] = nodes[g];
                            }else{
                                nodes[i].children[j] = nodes[g];
                            }

                     }
                  }

                  Py_DECREF(bn_node);
               }
               Py_DECREF(bn_iterator);

            }
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

         graph->nodes[i].graph = graph;

         graph->nodes[i].name = bn_node;
         Py_INCREF(bn_node);

         graph->nodes[i].cpd = bn_cpd;

         graph->nodes[i].cardinality = 2;//*((long *)PyArray_GETPTR1(bn_cardinality,0));

         graph->nodes[i].evidence = -1;

         graph->nodes[i].parents = NULL;

         graph->nodes[i].children = NULL;

         i++;

         Py_DECREF(bn_node);
    }

    Py_DECREF(bn_iterator);

    linkAdjacentNodes(bn_obj, graph, 1);
    linkAdjacentNodes(bn_obj, graph, 0);

    Py_DECREF(bn_get_cpds);
    Py_DECREF(bn_obj);

    return graph;
}


static PyObject* bnlearn_cpdist(PyObject* self, PyObject *args) {

    const char *node = 0;
    PyObject *bn_obj;

    if (!PyArg_ParseTuple(args, "Os", &bn_obj,&node))
        return NULL;

   Graph *graph = buildGraph(bn_obj);

   PyObject_Print(graph->nodes[10].name, stdout, 0);
   PyObject_Print(graph->nodes[10].parents[0].name, stdout, 0);
   PyObject_Print(graph->nodes[10].children[0].name, stdout, 0);

   return Py_None;
}


static PyMethodDef bnlearn_funcs[] = {
   {"cpdist", (PyCFunction)bnlearn_cpdist,
      METH_VARARGS, ""},
      {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef bnlearn_module = {
    PyModuleDef_HEAD_INIT,
    "bnlearn",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    bnlearn_funcs
};

PyMODINIT_FUNC
PyInit_bnlearn(void)
{
    if(PyArray_API == NULL)
    {
        import_array();
    }
    return PyModule_Create(&bnlearn_module);
}

int
main(int argc, char *argv[])
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        exit(1);
    }

    /* Add a built-in module, before Py_Initialize */
    if (PyImport_AppendInittab("bnlearn", PyInit_bnlearn) == -1) {
        fprintf(stderr, "Error: could not extend in-built modules table\n");
        exit(1);
    }
    //import_array();


    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(program);

    /* Initialize the Python interpreter.  Required.
       If this step fails, it will be a fatal error. */
    Py_Initialize();



    /* Optionally import the module; alternatively,
       import can be deferred until the embedded script
       imports it. */
    PyObject *pmodule = PyImport_ImportModule("bnlearn");
    if (!pmodule) {
        PyErr_Print();
        fprintf(stderr, "Error: could not import module 'spam'\n");
    }

    PyMem_RawFree(program);
    return 0;
}
