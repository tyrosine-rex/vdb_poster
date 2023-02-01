# vdb_poster


## Setup env

```bash
conda env create -f env/requirements.yml

conda activate vdb_poster_ravy_thomas

python -m ipykernel install --user --name vdb_poster_ravy_thomas
```


## Create database

```bash
python src/db/setup_database.py
```


## run streamlit app

Au premier lancement de streamlit, le module vous demande d'inscrire un email pour avoir des news. C'est embetant car il n'y a pas d'option "non-interractive" à la commande `streamlit run`.

Pour éviter ce comportement, faites:
```bach
echo '[general]\nemail = ""' > ~/.streamlit/credentials.toml
```

Lancez streamlit avec 

```bash
python -m streamlit run src/streamlit/app.py
```