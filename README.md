Server that returns fibonacci sequence
================

##### To start service

Debugging run:
```
  make run
```

Daemon mode:
```
  make daemon
```

Running tests
```
  make test
```

Running pep8
```
  make pep8
```

Running tests + pep8 + start app in debugging mode:
```
  make
```

Server default port is: 8080.

You can also run it by twistd command like this
```
  make env
  source env/bin/activate
  twistd -n fibonacci --port=8080 --bind-address=0.0.0.0
```
You can bind any port you like if you do so.

To show help
```
  twistd fibonacci --help 
```
  
