Howto
=====

#) run "python manage.py load_currencies" to get all currencies from webservice. The script will call update_rates
   to download the rates prior to saving the currencies in database.
#) If they are already currencies used in the database they are updated, otherwise they are created with
   the attribute 'used' set to false.

To update the pickle rates file run ::python manage.py update_rates

To set which currencies to use:
python manage.py set_currencies_used CHF EUR

To reset all currencies to False:
python manage.py set_currencies_used --all_false