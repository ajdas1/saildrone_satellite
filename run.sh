
python ./scripts/create_dir_structure.py
python ./scripts/register_dataset.py
python ./scripts/convert_saildrone_coordinates_to_shapefile.py
python ./scripts/convert_swath_outlines_to_shapefiles.py
python ./scripts/match_saildrone_satellite_swaths_pass1.py
python ./scripts/match_saildrone_satellite_swaths_pass2.py

python ./scripts/plot_saildrone_data_swath_coverage.py
