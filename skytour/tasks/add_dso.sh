python manage.py create_dso_finder_charts --dso_list 2994
python manage.py create_wide_narrow_charts --dso_list 2994
python manage.py create_dso_pdf --dso_list 2994
python manage.py create_atlas_plate -f 15 16 17
python manage.py scrape_metadata --source leda --model D --dso_list 2992 --verbose
python manage.py scrape_metadata --source simbad --model D --dso_list 2992 --verbose
python manage.py create_wide_narrow_charts --dso_list 49 1550 68 72 1745 69 330 50 51 64 65 807 2834 1734 1735 1736 1740 1741 1743 1744 2873
#python manage.py scrape_metadata --source leda --model F --dso_list 1727 --verbose
#python manage.py scrape_metadata --source simbad --model F --dso_list 1727 --verbose
