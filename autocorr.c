/* Python module to calculate the autocorrelation function of a field*/

#include <Python.h>
#include "numpy/arrayobject.h"
#include <omp.h>

//Compute the absolute distance between two points
double distance(const int * a, const int * b, const npy_intp dims)
{
    double total=0;
    for(int i=0; i< dims; i++){
        total+=pow(*(a+i)-*(b+i),2);
    }
    return sqrt(total);
}


//Compute the absolute distance between two points
double distance2(const int * a, const int * b)
{
    const int dif1 = (*(a)-*(b));
    const int dif2 = (*(a+1)-*(b+1));
    return sqrt(dif1*dif1+dif2*dif2);
}
/*Find the autocorrelation function from a sparse list of discrete tracer points.
   The field is assumed to be 1 at these points and zero elsewhere
   list - list of points to autocorrelate. A tuple length n (n=2) of 1xP arrays:
   the output of an np.where on an n-d field
   nbins - number of bins in output autocorrelation function
   size - size of the original field (assumed square), so field has dimensions (size,size..) n times
   norm - If true, normalise by the number of possible cells in each bin
*/
PyObject * _autocorr_list(PyObject *self, PyObject *args)
{
    PyArrayObject *plist;
    int nbins, size,norm=1;
    if(!PyArg_ParseTuple(args, "O!iii",&PyArray_Type, &plist, &nbins, &size, &norm) )
        return NULL;
    /*In practice assume this is 2*/
    npy_intp dims = PyArray_DIM(plist,0);
    npy_intp points = PyArray_DIM(plist,1);
    npy_intp npnbins = nbins;
    //Bin autocorrelation, must cover sqrt(dims)*size
    //so each bin has size sqrt(dims)*size /nbins
    const int nproc = omp_get_max_threads();
    int autocorr_C[nproc][nbins];
    memset(autocorr_C,0,nproc*nbins*sizeof(int));
    //Avg. density of the field: rho-bar
    const double avg = points/(1.*size*size);
    #pragma omp parallel
    {
        const int tid = omp_get_thread_num();
        #pragma omp for
        for(int b=0; b<points; b++){
            for(int a=0; a<points; a++){
                double rr = distance2(PyArray_GETPTR2(plist,0,a), PyArray_GETPTR2(plist,0,b));
                //Which bin to add this one to?
                int cbin = floor(rr * nbins / (size*sqrt(dims)));
                autocorr_C[tid][cbin]+=1;
            }
        }
    }
    PyArrayObject *autocorr = (PyArrayObject *) PyArray_SimpleNew(1,&npnbins,NPY_DOUBLE);
    PyArray_FILLWBYTE(autocorr, 0);
    for(int tid=0; tid < nproc; tid++){
        for(int nn=0; nn< nbins; nn++){
            *(double *)PyArray_GETPTR1(autocorr,nn)+=autocorr_C[tid][nn];
        }
    }
    /*Normalise field*/
    for(int nn=0; nn< nbins; nn++)
        *(double *)PyArray_GETPTR1(autocorr,nn) = *(double *)PyArray_GETPTR1(autocorr,nn)/avg/avg-1;

    if(norm){
        double count[nbins];
        for(int nn=0; nn< nbins; nn++){
            //Count number of square bins in a circle of radius sqrt(dims)*size
            //This is 4 * (quarter circle)
            // = 4 * sum(y < r) \sqrt(r^2-y^2)
            //Maximal radius in this bin
            double rr = (1+nn)*sqrt(dims)*size/(1.*nbins);
            //Vector of y values
            count[nn]=0;
            for(int yy=0; yy<floor(rr);yy++){
                //Vector of integrands along x axis
                count[nn] += 4*ceil(sqrt(rr*rr - yy*yy));
            }
        }
        //Take off the modes in previous bin to get an annulus
        for(int nn=nbins-1; nn > 0; nn--)
            count[nn] -= count[nn-1];
        for(int nn=0; nn< nbins; nn++)
            *(double *)PyArray_GETPTR1(autocorr,nn)/=count[nn];
    }
    return Py_BuildValue("O", autocorr);
}

static PyMethodDef __autocorr[] = {
  {"_autocorr_list", _autocorr_list, METH_VARARGS,
   "Calculate the autocorrelation function"
   "    Arguments: plist, nbins, size, norm"
   "    "},
  {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC
init_autocorr_priv(void)
{
  Py_InitModule("_autocorr_priv", __autocorr);
  import_array();
}
