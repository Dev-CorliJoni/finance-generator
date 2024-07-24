# finance-generator

## Supported exchanges
- Bitpanda

## How to generate a report

Creation of a report with all the data taken into account
```
python main.py --imports ".\bitpanda.csv" --export ".\destination_folder"
```

Generate report with the all data between 1\1\2024 and 12\31\2024
```
python main.py --imports ".\bitpanda.csv" --export ".\destination_folder" --start_date "1\1\2024" --end_date "12\31\2024"
```
