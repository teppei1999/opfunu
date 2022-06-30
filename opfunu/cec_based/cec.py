#!/usr/bin/env python
# Created by "Thieu" at 06:43, 30/06/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

from abc import ABC
import numpy as np
from opfunu.benchmark import Benchmark
import pkg_resources
from pandas import read_csv


class CecBenchmark(Benchmark, ABC):
    """
    Defines an abstract class for optimization benchmark problem.

    All subclasses should implement the ``evaluate`` method for a particular optimization problem.

    Attributes
    ----------
    bounds : list
        The lower/upper bounds of the problem. This a 2D-matrix of [lower, upper] array that contain the lower and upper bounds.
        By default, each problem has its own bounds. But user can try to put different bounds to test the problem.
    ndim : int
        The dimensionality of the problem. It is calculated from bounds
    lb : np.ndarray
        The lower bounds for the problem
    ub : np.ndarray
        The upper bounds for the problem
    f_global : float
        The global optimum of the evaluated function.
    x_global : np.ndarray
        A list of vectors that provide the locations of the global minimum.
        Note that some problems have multiple global minima, not all of which may be listed.
    n_fe : int
        The number of function evaluations that the object has been asked to calculate.
    dim_changeable : bool
        Whether we can change the benchmark function `x` variable length (i.e., the dimensionality of the problem)
    """

    name = "Benchmark name"
    latex_formula = r'f(\mathbf{x})'
    latex_formula_dimension = r'd \in \mathbb{N}_{+}^{*}'
    latex_formula_bounds = r'x_i \in [-2\pi, 2\pi], \forall i \in \llbracket 1, d\rrbracket'
    latex_formula_global_optimum = r'f(0, ..., 0)=-1, \text{ for}, m=5, \beta=15'
    continuous = True
    linear = False
    convex = True
    unimodal = False
    separable = False

    differentiable = True
    scalable = True
    randomized_term = False
    parametric = True
    shifted = True

    modality = True  # Number of ambiguous peaks, unknown # peaks

    # n_basins = 1
    # n_valleys = 1

    def __init__(self):
        super().__init__()
        self._bounds = None
        self._ndim = None
        self.dim_changeable = True
        self.dim_default = 30
        self.dim_max = 100
        self.f_global = None
        self.x_global = None
        self.n_fe = 0
        self.f_shift = None
        self.f_bias = None
        self.support_path = None

    def make_support_data_path(self, data_name):
        self.support_path = pkg_resources.resource_filename("opfunu", f"cec_based/{data_name}")

    def check_shift_data(self, f_shift):
        if type(f_shift) is str:
            return self.load_shift_data(f_shift)
        else:
            if type(f_shift) in [list, tuple, np.ndarray]:
                return np.squeeze(f_shift)
            else:
                raise ValueError(f"The shift data should be a list/tuple or np.array!")

    def load_shift_data(self, f_shift_file):
        data = read_csv(f"{self.support_path}/{f_shift_file}", delimiter='\s+', index_col=False, header=None)
        return data.values.reshape((-1))

    def load_matrix_data(self, data_file=None):
        data = read_csv(self.support_path + data_file, delimiter='\s+', index_col=False, header=None)
        return data.values

    def check_solution(self, x, dim_max=None, dim_support=None):
        """
        Raise the error if the problem size is not equal to the solution length

        Parameters
        ----------
        x : np.ndarray
            The solution
        dim_max : The maximum number of variables that the function is supported
        dim_support : List of the supported dimensions
        """
        if not self.dim_changeable and (len(x) != self._ndim):
            raise ValueError(f"The length of solution should has {self._ndim} variables!")
        if (dim_max is not None) and (len(x) > dim_max):
            raise ValueError(f"This function is not supported ndim > {dim_max}!")
        if (dim_support is not None) and (len(x) not in dim_support):
            raise ValueError(f"This function is only supported ndim in {dim_support}!")

    def check_ndim_and_bounds(self, ndim=None, dim_max=None, bounds=None, default_bounds=None):
        """
        Check the bounds when initializing the object.

        Parameters
        ----------
        ndim : int
            The number of dimensions (variables)
        dim_max : int
            The maximum number of dimensions (variables) that the problem is supported
        bounds : list, tuple, np.ndarray
            List of lower bound and upper bound, should use default None value
        default_bounds : np.ndarray
            List of initial lower bound and upper bound values
        """
        if ndim is None:
            self._bounds = default_bounds if bounds is None else np.array(bounds).T
            self._ndim = self._bounds.shape[0]
            if dim_max is not None and self._ndim > dim_max:
                raise ValueError(f"{self.__class__.__name__} problem supports maximum {dim_max} variables!")
        else:
            if bounds is None:
                if self.dim_changeable:
                    if type(ndim) is int and ndim > 1:
                        if dim_max is None or ndim <= dim_max:
                            self._ndim = int(ndim)
                            self._bounds = np.array([default_bounds[0] for _ in range(self._ndim)])
                        else:
                            raise ValueError(f"{self.__class__.__name__} problem supports maximum {dim_max} variables!")
                    else:
                        raise ValueError('ndim must be an integer and > 1!')
                else:
                    self._ndim = self.dim_default
                    self._bounds = default_bounds
                    print(f"{self.__class__.__name__} is fixed problem with {self.dim_default} variables!")
            else:
                if self.dim_changeable:
                    self._bounds = np.array(bounds).T
                    self._ndim = self._bounds.shape[0]
                    if self._ndim > dim_max:
                        raise ValueError(f"{self.__class__.__name__} problem supports maximum {dim_max} variables!")
                    else:
                        print(f"{self.__class__.__name__} problem is set with {self._ndim} variables!")
                else:
                    self._bounds = np.array(bounds).T
                    if self._bounds.shape[0] == self.dim_default:
                        self._ndim = self.dim_default
                    else:
                        raise ValueError(f"{self.__class__.__name__} is fixed problem with {self._ndim} variables. Please setup the correct bounds!")
