#!/bin/bash
python ./fetch_primitives.py
python ./fetch_craftables.py
python ./patch_1_craftables.py
python ./patch_2_craftables.py
python ./patch_3_craftables.py
python ./patch_4_craftables.py
python ./patch_5_craftables.py
python ./fetch_crafting_ingredients.py
python ./create_ingredients.py
python ./create_hammerables.py