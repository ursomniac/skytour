python manage.py create_dso_finder_charts --dso_list 2891
python manage.py create_wide_narrow_charts --dso_list 2891
python manage.py add_to_imaging_checklist -p 3 2891
python manage.py create_dso_pdf --dso_list 2891
python manage.py create_atlas_plate -f 47 48
python manage.py scrape_metadata --source leda --model D --dso_list 2891 --verbose
python manage.py scrape_metadata --source simbad --model D --dso_list 2891 --verbose
python manage.py scrape_metadata --source leda --model F --dso_list 1727 --verbose
python manage.py scrape_metadata --source simbad --model F --dso_list 1727 --verbose
