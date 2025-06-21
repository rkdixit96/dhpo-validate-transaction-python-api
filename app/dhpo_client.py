"""
EClaimLinkClient: Singleton SOAP client for DHPO eClaimLink API.
Handles authentication, SSL, and provides typed methods for API endpoints.
"""

from typing import Optional, Dict
import os
import logging
import ssl
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from zeep import Client
from zeep.transports import Transport
import xmltodict
from app.schemas import (
    GetNewTransactionsResponseModel,
    GetNewPriorAuthorizationTransactionsResponseModel,
    UploadTransactionResponseModel,
    DownloadTransactionFileResponseModel,
    CheckForNewPriorAuthorizationTransactionsResponseModel,
    SetTransactionDownloadedResponseModel,
    SearchTransactionsResponseModel,
)

# Configure logging
logger = logging.getLogger(__name__)

class SSLAdapter(HTTPAdapter):
    """Adapter for custom SSL context (lowers security for weak DH keys)."""
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context)

class EClaimLinkClient:
    """Singleton SOAP client for DHPO eClaimLink API."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, '_initialized', False):
            return
        wsdl_url = os.environ.get("DHPO_WSDL_URL", "https://dhpo.eclaimlink.ae/ValidateTransactions.asmx?WSDL")
        self.login = os.environ.get("DHPO_LOGIN")
        self.password = os.environ.get("DHPO_PASSWORD")
        if not self.login or not self.password:
            raise ValueError("DHPO_LOGIN and DHPO_PASSWORD environment variables must be set.")
        session = Session()
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        session.mount('https://', SSLAdapter(ssl_context=ctx))
        transport = Transport(session=session)
        self.client = Client(wsdl=wsdl_url, transport=transport)
        self.service = self.client.service
        self._initialized = True

    def _parse_xml(self, xml_str: Optional[str]) -> Optional[Dict]:
        """Parse XML string to dict, return None on error."""
        if xml_str:
            try:
                return xmltodict.parse(xml_str)
            except Exception as e:
                logger.error(f"XML parsing error: {e}")
                return None
        return None

    def get_new_transactions(self) -> GetNewTransactionsResponseModel:
        """Fetch new transactions from DHPO."""
        r = self.service.GetNewTransactions(login=self.login, pwd=self.password)
        return GetNewTransactionsResponseModel(
            result=r.GetNewTransactionsResult,
            xml_transaction=self._parse_xml(r.xmlTransaction),
            error_message=r.errorMessage
        )

    def get_new_prior_authorization_transactions(self) -> GetNewPriorAuthorizationTransactionsResponseModel:
        """Fetch new prior authorization transactions."""
        r = self.service.GetNewPriorAuthorizationTransactions(login=self.login, pwd=self.password)
        return GetNewPriorAuthorizationTransactionsResponseModel(
            result=r.GetNewPriorAuthorizationTransactionsResult,
            xml_transaction=self._parse_xml(r.xmlTransaction),
            error_message=r.errorMessage
        )

    def upload_transaction(self, file_content: bytes, file_name: str) -> UploadTransactionResponseModel:
        """Upload a transaction file to DHPO."""
        r = self.service.UploadTransaction(
            login=self.login,
            pwd=self.password,
            fileContent=file_content,
            fileName=file_name
        )
        return UploadTransactionResponseModel(
            result=r.UploadTransactionResult,
            error_message=r.errorMessage,
            error_report=r.errorReport
        )

    def download_transaction_file(self, file_id: str) -> DownloadTransactionFileResponseModel:
        """Download a transaction file by ID."""
        r = self.service.DownloadTransactionFile(
            login=self.login,
            pwd=self.password,
            fileId=file_id
        )
        return DownloadTransactionFileResponseModel(
            result=r.DownloadTransactionFileResult,
            file_name=r.fileName,
            file=self._parse_xml(r.file),
            error_message=r.errorMessage
        )

    def check_for_new_prior_authorization_transactions(self) -> CheckForNewPriorAuthorizationTransactionsResponseModel:
        """Check for new prior authorization transactions."""
        r = self.service.CheckForNewPriorAuthorizationTransactions(
            login=self.login,
            pwd=self.password
        )
        return CheckForNewPriorAuthorizationTransactionsResponseModel(
            result=r.CheckForNewPriorAuthorizationTransactionsResult,
            error_message=r.errorMessage
        )

    def set_transaction_downloaded(self, field_id: str) -> SetTransactionDownloadedResponseModel:
        """Mark a transaction as downloaded by field ID."""
        r = self.service.SetTransactionDownloaded(
            login=self.login,
            pwd=self.password,
            fieldId=field_id
        )
        return SetTransactionDownloadedResponseModel(
            result=r.SetTransactionDownloadedResult,
            error_message=r.errorMessage
        )

    def search_transactions(
        self,
        direction: int,
        transaction_id: int,
        transaction_status: int,
        min_record_count: int,
        max_record_count: int,
        caller_license: Optional[str] = None,
        e_partner: Optional[str] = None,
        transaction_file_name: Optional[str] = None,
        transaction_from_date: Optional[str] = None,
        transaction_to_date: Optional[str] = None
    ) -> SearchTransactionsResponseModel:
        """Search for transactions with filters."""
        r = self.service.SearchTransactions(
            login=self.login,
            pwd=self.password,
            direction=direction,
            transactionID=transaction_id,
            TransactionStatus=transaction_status,
            minRecordCount=min_record_count,
            maxRecordCount=max_record_count,
            callerLicense=caller_license,
            ePartner=e_partner,
            transactionFileName=transaction_file_name,
            transactionFromDate=transaction_from_date,
            transactionToDate=transaction_to_date
        )
        return SearchTransactionsResponseModel(
            result=r.SearchTransactionsResult,
            found_transactions=self._parse_xml(r.foundTransactions),
            error_message=r.errorMessage
        )
