#include <Python.h>


static PyObject* bnlearn_cpdist(PyObject* self, PyObject *args) {

    const char *node = 0;
    PyObject *bn_obj;

    if (!PyArg_ParseTuple(args, "Os", &bn_obj,&node))
        return NULL;

   //bn
   //node
   // evidence true
   // likelohood smapling

   return Py_BuildValue("s", node);
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
