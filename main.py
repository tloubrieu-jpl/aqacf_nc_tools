import parser
import os
import glob
from datetime import datetime, timedelta
import pytz
import netCDF4 as nc


def add_time_variable(dataset, d):
    dim_t = dataset.createDimension('time', size=1)
    # Create a variable `time` using the unlimited dimension:
    var_t = dataset.createVariable('time', 'int', dimensions=('time'), shuffle=False)
    var_t.units = 'seconds since 1970-01-01 00:00:00.0 +0:00'
    # Add some values to the variable:
    var_t[:] = [d.timestamp()]

    return dim_t

def copy_ncattrs(input_var, output_var):
    for attr in input_var.ncattrs():
        output_var.setncattr_string(attr, input_var.getncattr(attr))

def copy_dimension_and_variable(input, output, except_variables=[]):
    for dim in input.dimensions:
        output.createDimension(dim, size=input.dimensions[dim].size)

    for variable in input.variables:
        if variable not in except_variables:
            var = output.createVariable(variable,
                                  input.variables[variable].datatype,
                                  dimensions=input.variables[variable].dimensions)
            copy_ncattrs(input.variables[variable], var)
            output[variable][:] = input[variable][:]


def add_time_dimension_to_variable(input, output, variable, time_dimension):

    new_dimension = ['time']
    new_dimension.extend(input.variables[variable].dimensions)
    var = output.createVariable(variable, input.variables[variable].datatype, new_dimension)
    copy_ncattrs(input.variables[variable], var)
    var[:] = [input[variable][:]]


def add_time_in_file(file: str, date_pattern: str, out_dir: str, up_to=-1):
    file_name = os.path.basename(file)
    start_d = datetime.strptime(file_name[:up_to], date_pattern)
    #end_d = start_d.replace(year=start_d.year+1)
    #d = start_d + (end_d - start_d)/2
    d = start_d

    dataset_input = nc.Dataset(file, 'r', format="NETCDF4")
    dataset_output = nc.Dataset(os.path.join(out_dir, file_name), 'w', format='NETCDF4')
    dim_time = add_time_variable(dataset_output, d)
    copy_dimension_and_variable(dataset_input, dataset_output, except_variables=['GWRPM25'])
    add_time_dimension_to_variable(dataset_input, dataset_output, 'GWRPM25', dim_time)

    dataset_input.close()
    dataset_output.close()


def add_time_in_dir(in_dir, out_dir):
    file_pattern = os.path.join(in_dir, '*.nc')
    for file in glob.glob(file_pattern):
        add_time_in_file(file, 'V5GL01.HybridPM25.NorthAmerica.%Y%m-', out_dir, up_to=38)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    add_time_in_dir('/Users/loubrieu/Downloads/Monthly', '/Users/loubrieu/Documents/sdap/PM25_withtime_monthly')


