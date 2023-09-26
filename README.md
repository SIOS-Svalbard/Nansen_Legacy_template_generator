# Nansen_Legacy_template_generator

The Nansen Legacy template generator is designed based on experiences gained during the Nansen Legacy project (Arven etter Nansen - AeN). This template generator will be used to create spreadsheet templates that include columns based on both the NetCDF Climate and Forecast (CF) Metadata Conventions and Darwin Core.

CF Conventions: https://cfconventions.org/
Darwin Core: https://dwc.tdwg.org/

A separate sheet in the same file includes space to fill in metadata based on the Attribute Convention for Data Discovery (ACDD).

ACDD: https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery_1-3

The ACDD conventions recommendations used in this template generator are in line with the recommendations for CF-NetCDF files that contribute to SIOS, as documented here:
https://adc.met.no/node/4

## Setup and Installation

This application was developed with Python version 3.8.10.

```
git clone <repo-url>

pip install -r requirements.txt
```

The field definitions are not updated automatically, but can be updated using the GUI (Admin - get latest terms).

Either run
```sh
make update-config
```

or when the source is not available but the Flask server is running
```sh
curl -X POST http://localhost:5000/update
```

The application can be run using WSGI (flaskapp.wsgi) and has been developed using apache2.

Cite this application as:
Luke Marsden, & Olaf Schneider. (2023). SIOS-Svalbard/Nansen_Legacy_template_generator: Nansen Legacy template generator (v1.01). Zenodo. https://doi.org/10.5281/zenodo.8362212
