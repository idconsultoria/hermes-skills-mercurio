#!/usr/bin/env python3
"""7z-compatible CLI shim for KCC, using Python zipfile.
Place in PATH as '7z' so KCC finds it.

Usage:
    ./7z-shim.py a -mx0 -tzip output.zip file1 file2 ...
    ./7z-shim.py rn existing.zip old_name new_name
    
KCC calls:
    7z a -mx0 -tzip <tempfile> *
    7z rn <tempfile> !mimetype mimetype
"""

import os, sys
from zipfile import ZipFile, ZIP_STORED

def main():
    args = sys.argv[1:]
    if not args:
        return 0
    cmd = args[0]
    
    if cmd == 'a' and '-tzip' in args:
        # 7z a -mx0 -tzip <zipfile> <files...>
        zi = args.index('-tzip') + 1
        zipname = args[zi]
        files = [a for a in args[zi+1:] if not a.startswith('-')]
        mode = 'a' if os.path.exists(zipname) else 'w'
        
        with ZipFile(zipname, mode, ZIP_STORED) as zf:
            for f in files:
                if f == '*':
                    for root, dirs, fs in os.walk('.'):
                        for fn in fs:
                            fp = os.path.join(root, fn)
                            an = fp[2:] if fp.startswith('./') else fp
                            zf.write(fp, an)
                elif os.path.isfile(f):
                    zf.write(f, f)
        return 0
    
    elif cmd == 'rn':
        # 7z rn <zipfile> <old_name> <new_name>
        zipname, old, new = args[1], args[2], args[3]
        data = {}
        with ZipFile(zipname, 'r') as zf:
            for n in zf.namelist():
                data[n] = zf.read(n)
        bak = zipname + '.bak'
        os.rename(zipname, bak)
        try:
            with ZipFile(zipname, 'w', ZIP_STORED) as zf:
                for n, c in data.items():
                    zf.writestr(new if n == old else n, c)
        except:
            os.rename(bak, zipname)
            raise
        os.unlink(bak)
        return 0
    
    elif cmd in ('x', 'e'):
        zipname = args[1]
        dest = args[2] if len(args) > 2 else '.'
        with ZipFile(zipname, 'r') as zf:
            zf.extractall(dest)
        return 0
    
    elif cmd == 'l':
        zipname = args[1]
        with ZipFile(zipname, 'r') as zf:
            for n in zf.namelist():
                i = zf.getinfo(n)
                print(f"{'D' if n.endswith('/') else ' '} {i.file_size:>10}  {n}")
        return 0
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
