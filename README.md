## NFL QA Datasette Instance

This repo contains the supporting code for maintaining an instance of NFL Data

gcloud auth login
gcloud config set project precise-cabinet-280004
gcloud config set run/region us-west1
datasette publish cloudrun data.db --service sleeper-datasette --static -:static
