@echo off
echo Installing gcloud beta components...

FOR /F "delims=" %%i in ( '"C:\Users\SPATHIVA\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" components copy-bundled-python' ) DO (
    SET CLOUDSDK_PYTHON=%%i
)

gcloud components install beta --quiet

echo Beta components installed. Now trying to set IAM policy...
gcloud beta run services add-iam-policy-binding --region=us-central1 --member=allUsers --role=roles/run.invoker trending-resolver

echo Done!