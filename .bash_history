source myenv/bin/activate
pip install psycopg2
python --version
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev
sudo service postgresql start
pg_config
pip install psycopg2
sudo -u postgres psql
touch test.py
nano test.py
python test.py
nano test.py
nano schema.sql
# Loop to create databases and apply schema
for i in {01..06}; do
    createdb -U postgres compra_2019_$i;     psql -U postgres -d compra_2019_$i -f schema.sql; 
    createdb -U postgres venda_2019_$i;     psql -U postgres -d venda_2019_$i -f schema.sql; done
sudo -i -u postgres
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   