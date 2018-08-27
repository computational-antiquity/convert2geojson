Making a New Release
====================

 - create and upload a new github tag == version
 - version++ for 'version' and 'download url'

```python
 setup(
    # ...
    version='0.0.1',
    # ...
    download_url='https://github.com/computational-antiquity/convert2geojson/archive/0.0.1.tar.gz',
    )
```

 - run these commands:

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```
