# Standard library imports

# Third-party imports
from fastapi import FastAPI, File, UploadFile, Query, Depends
from dotenv import load_dotenv

# Local imports
from app.dhpo_client import EClaimLinkClient
from app.schemas import (
    GetNewTransactionsResponseModel,
    GetNewPriorAuthorizationTransactionsResponseModel,
    UploadTransactionResponseModel,
    DownloadTransactionFileResponseModel,
    CheckForNewPriorAuthorizationTransactionsResponseModel,
    SetTransactionDownloadedResponseModel,
    SearchTransactionsResponseModel,
    SearchTransactionsQueryParams,
)

app = FastAPI(title="DHPO Web Service API", description="API wrapper for Dubai Health Post Office SOAP services.")

# Load environment variables from .env file at startup
load_dotenv()


@app.get("/get-new-transactions", response_model=GetNewTransactionsResponseModel)
def get_new_transactions() -> GetNewTransactionsResponseModel:
    """Retrieve new transactions that haven't been flagged as downloaded."""
    return GetNewTransactionsResponseModel(**EClaimLinkClient().get_new_transactions().__dict__)


@app.get("/get-new-prior-auth", response_model=GetNewPriorAuthorizationTransactionsResponseModel)
def get_new_prior_authorization_transactions() -> GetNewPriorAuthorizationTransactionsResponseModel:
    """Retrieve new prior request or prior authorization transactions."""
    return GetNewPriorAuthorizationTransactionsResponseModel(**EClaimLinkClient().get_new_prior_authorization_transactions().__dict__)


@app.post("/upload-transaction", response_model=UploadTransactionResponseModel)
def upload_transaction(file: UploadFile = File(...)) -> UploadTransactionResponseModel:
    """Upload a new transaction XML file for validation and processing."""
    content = file.file.read()
    return UploadTransactionResponseModel(**EClaimLinkClient().upload_transaction(file_content=content, file_name=file.filename).__dict__)


@app.get("/download-transaction-file", response_model=DownloadTransactionFileResponseModel)
def download_transaction_file(
    file_id: str = Query(..., description="Unique file ID retrieved from previous transaction listing"),
) -> DownloadTransactionFileResponseModel:
    """Download a previously uploaded transaction file."""
    return DownloadTransactionFileResponseModel(**EClaimLinkClient().download_transaction_file(file_id).__dict__)


@app.post("/set-transaction-downloaded", response_model=SetTransactionDownloadedResponseModel)
def set_transaction_downloaded(
    file_id: str = Query(..., description="File ID to be marked as downloaded to prevent repeated downloads"),
) -> SetTransactionDownloadedResponseModel:
    """Mark a file as downloaded in the DHPO system."""
    return SetTransactionDownloadedResponseModel(**EClaimLinkClient().set_transaction_downloaded(file_id).__dict__)


@app.get("/check-new-prior-auth", response_model=CheckForNewPriorAuthorizationTransactionsResponseModel)
def check_new_prior_authorization_transactions() -> CheckForNewPriorAuthorizationTransactionsResponseModel:
    """Check whether new prior authorizations are available without downloading them."""
    return CheckForNewPriorAuthorizationTransactionsResponseModel(**EClaimLinkClient().check_for_new_prior_authorization_transactions().__dict__)


@app.get("/search-transactions", response_model=SearchTransactionsResponseModel)
def search_transactions(
    params: SearchTransactionsQueryParams = Depends()
) -> SearchTransactionsResponseModel:
    """Search for transactions based on direction, partner licenses, and filtering criteria."""
    response = EClaimLinkClient().search_transactions(
        direction=params.direction.value,
        transaction_id=params.transaction_id.value,
        transaction_status=params.transaction_status.value,
        min_record_count=params.min_record_count,
        max_record_count=params.max_record_count,
        caller_license=params.caller_license,
        e_partner=params.e_partner,
        transaction_file_name=params.transaction_file_name,
        transaction_from_date=params.transaction_from_date,
        transaction_to_date=params.transaction_to_date,
    )
    return SearchTransactionsResponseModel(**response.__dict__)
