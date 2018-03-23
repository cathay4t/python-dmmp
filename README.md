python-dmmp
-----------
Python(2 & 3) API of multipath-tools in LGPL 3.0+ license.

## Install

```bash
python setup.py install
```

## Usage

Sample code, for detailed usage, check `help(dmmp)`:

```python
import dmmp

for mpath in dmmp.mpaths_get():
    print("Got mpath: wwid '%s', name '%s'" % (mpath.wwid, mpath.name))
    for pg in mpath.path_groups:
        print("\tGot path group: id '%d', priority '%d', status '%d(%s)', "
              "selector '%s'" %
              (pg.id, pg.priority, pg.status, pg.status_string, pg.selector))

        for p in pg.paths:
            print("\t\tGot path: blk_name '%s', status '%d(%s)'" %
                  (p.blk_name, p.status, p.status_string))
```

## Contact
 * IRC: Gris@freenode
 * Github issue: https://github.com/cathay4t/python-dmmp/issues
 * Github PR: https://github.com/cathay4t/python-dmmp/pulls
