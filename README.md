# remote-sqlitedict
Package allows to set up a remotely accessed SQLite backed Python dictionary for a convenient data persistence in serverless environment

### Usage

##### Server

    pip install remote-sqlitedict
    python -m remote_sqlitedict
    
This will open server at a default port of 18753, and will save data in the current working directory.

To change port or data directory use:

    python -m remote_sqlitedict 1234 --directory /sqlite-data/

Also you can use Docker with docker-compose:
    
    docker-compose up -d
 
##### Client

To use client just import **get_sqlitedict** function, and call it:

    from remote_sqlitedict import get_sqlitedict
    db = get_sqlitedict('localhost', 18753, 'test_database')
    
    # use exactly as you would use sqlitedict
    db['some_object'] = {'field': 'value'}
    db.commit()