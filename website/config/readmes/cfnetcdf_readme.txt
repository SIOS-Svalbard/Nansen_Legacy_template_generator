README:

Spreadsheet template to record metadata and data.

Please do not publish data in this format. This template should make it easier for you to create a CF-NetCDF file.
This will help make your data FAIR.

The column headers in the 'data' sheet should be mostly CF standard names, except for other fields you might have added and the 'bounds' fields.
Use these in the 'standard_name' variable attribute for each variable.
A list of CF standard names is available here:
https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html

The 'bounds' columns should be used where a data value spans a spatial or temporal range (a cell).
The bounds should be stored in a separate 2-dimensional variable that has no standard name.
Instead, the coordinate variable should include a 'bounds' variable attribute that refers
to the bounds variable.
There are examples in the CF conventions documentation.
https://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#_data_representative_of_cells

Use the attributes in the 'metadata' sheet as global attributes in your CF-NetCDF file.
They are terms from the ACDD conventions in most cases.
These are the recommendations of the Arctic Data Centre and SIOS, based on ACDD.
https://adc.met.no/node/4
https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3

The 'featureType' attribute is from the CF conventions:
http://cfconventions.org/Data/cf-conventions/cf-conventions-1.10/cf-conventions.html#_features_and_feature_types

You can create CF-NetCDF files using most programming languages. This includes Python, R, Matlab, C/C++, Java and Fortran.

If you don't like to code, you can use Rosetta. Rosetta helps you create a CF-NetCDF file using a web form.
http://tomcat.nersc.no/rosetta/

Some help (scripts linked in descriptions):

Create a CF-NetCDF file using Python for a depth profile
https://www.youtube.com/watch?v=QXnY17DMm5c
Create a CF-NetCDF file with multiple dimensions using Python
https://www.youtube.com/watch?v=gUZUdLdOt_4

Create a CF-NetCDF file using R for a depth profile
https://www.youtube.com/watch?v=ozhpQofa_g4

Check you NetCDF file against the CF conventions and the ACDD conventions
https://sios-svalbard.org/dataset_validation/form
or
https://compliance.ioos.us/index.html

Consider citing this template generator as:

Luke Marsden, & Olaf Schneider. (2023). SIOS-Svalbard/Nansen_Legacy_template_generator: Nansen Legacy template generator (v1.01). Zenodo. https://doi.org/10.5281/zenodo.8362212