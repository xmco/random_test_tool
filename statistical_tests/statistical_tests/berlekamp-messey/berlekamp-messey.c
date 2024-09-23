#include <stdio.h>
#include <Python.h>

int berlekamp_messey(int *s, int n) {
    int b[n], c[n], t[n], d, j, N, L=0, m=-1;
    for(j=n; --j>0;)
        b[j]=c[j]=0;
    b[0]=c[0]=1;
    for(N=0; N<n; ++N) {                 // For N=0 step 1 while N<n
        d=s[N];                          // first term  of discrepancy
        for(j=L; j>0; --j)               // other terms of discrepancy
            d ^= c[j]&s[N-j];
        if (d!=0) {                      // non-zero discrepancy
            for(j=n; --j>=0;)            // copy c to t
                t[j]=c[j];
            for(j=n-N+m; --j>=0;)        // XOR b (reversed) into c
                c[N-m+j] ^= b[j];
            if(L+L<=N) {                 // if L<=N/2
                L=N+1-L;
                m=N;
                for(j=n; --j>=0;)        // copy t to b
                    b[j]=t[j];
            }
        }
    }
    return L;
}


static PyObject *method_berlekamp_messey(PyObject *self, PyObject *args) {

    PyObject *pyList;
    PyObject *pItem;
    int n, l;
    int *s;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "Oi", &pyList, &n)) {
        return NULL;
    }
    s = (int*)malloc(n*sizeof(int));

    for (int i=0; i<n; i++) {
       pItem = PyList_GetItem(pyList, i);
       s[i] = (int) PyLong_AsLong(pItem);
    }

    l = berlekamp_messey(s, n);

    return PyLong_FromLong(l);

}

static PyMethodDef BerlekampMesseyMethods[] = {
    {"berlekamp_messey", method_berlekamp_messey, METH_VARARGS, "Python interface for berlekamp_messey C library function"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef berlekamp_messey_module = {
    PyModuleDef_HEAD_INIT,
    "berlekamp_messey",
    "Python interface for the berlekamp_messey C library function",
    -1,
    BerlekampMesseyMethods
};


PyMODINIT_FUNC PyInit_berlekamp_messey(void) {
    return PyModule_Create(&berlekamp_messey_module);
}

