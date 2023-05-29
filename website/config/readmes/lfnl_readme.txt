README:

Spreadsheet template to record metadata and data.

Please do not publish data in this format. This template should make it easier for you to create a CF-NetCDF file or Darwin Core Archive.
This will help make your data FAIR.

This configuration has been designed to work with the 'Learnings from Nansen Legacy logging system'.
Some of the fields are required for use in this logging system.

Some of the column headers in the 'data' sheet are Darwin Core terms.
Use these as column headers in the CSV cores and extensions if creating a Darwin Core Archive.
A list of Darwin Core terms is available here:
https://dwc.tdwg.org/terms/

Some of the column headers in the 'data' sheet are CF standard names.
Use these in the 'standard_name' variable attribute for each variable if creating a CF-NetCDF file.
A list of CF standard names is available here:
https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html

Use the attributes in the 'metadata' sheet as global attributes in your CF-NetCDF file.
They are terms from the ACDD conventions in most cases.
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

You can create a Darwin Core Archive using GBIF's Integrated Publishing Toolkit (IPT).
In the link below there is a map of places where this is installed.
Contact a relevant one of these and ask if you can use their node.
They can provide you with login details.
It is also possible to configure a node at your own institution.
https://www.gbif.org/ipt
