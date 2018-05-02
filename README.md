# README #

# Usage
Run sender:
```
python sender.py --accountID <accountID>
```

Kill all senders:
```
ps -e --format "pid cmd" | grep sender.py | awk '{print $1}' | xargs kill
```

Get results table:
```
python manage.py results
python manage.py processing_status
python manage.py add_alpha --comment "comment" --author "you" -- '<alpha>'
python manage.py add_random_websim --n 300

python manage.py add_gen_alpha --gen generators.tree_generator --n 1

python manage.py top --top top_gen
python manage.py top --top top
```

Run production mode:
change prod variable in session.py
'''

### Locks
http://stackoverflow.com/questions/6507475/job-queue-as-sql-table-with-multiple-consumers-postgresql — second answer — true

# Alpha-generator
## Params:
```
sending.delay,
sending.decay,
sending.opneut,
sending.backdays,
sending.univid,
sending.optrunc
```
