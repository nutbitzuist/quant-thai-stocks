#!/bin/bash
cd frontend
railway link --project a54028cf-667f-4889-989c-7574b61ae6e4
railway service create --name frontend || railway service
railway up --detach
