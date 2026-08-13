py -3 -m mpremote mkdir :/apps/batterymeter
py -3 -m mpremote cp `
    '__init__.py' `
    'metadata.json' `
    'app.py' `
    :/apps/batterymeter/

Write-Host "Deployed. Press the reboop button on the badge."
