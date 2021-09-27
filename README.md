# amazon_to_ereaderiq
This script is for sync-ing amazon wishlist of kindle books to ereaderiq which is for tracking book price drops
- default price drop: 20%

## pre-requisite
* account for https://www.ereaderiq.com/
* account for amazon US

## usage
- install dependencies
```python
pip install requirements.txt
```

- run
```python
python sync_amazon_to_ereaderiq_by_ui.py \
    --username_amazon='' \
    --password_amazon='' \
    --email_ereaderiq=''
```