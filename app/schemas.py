from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class TransactionTypeEnum(int, Enum):
    """Enumeration of transaction types for DHPO."""
    CLAIM = 2
    REMITTANCE = 4
    PRIOR_REQUEST = 8
    PRIOR_AUTH = 16
    INVOICE = 32

class DirectionEnum(int, Enum):
    """Enumeration for transaction direction (sent or received)."""
    SENT = 1
    RECEIVED = 2

class TransactionStatusEnum(int, Enum):
    """Enumeration for transaction status (new or already downloaded)."""
    NEW_ONLY = 1
    ALREADY_DOWNLOADED = 2

class SearchTransactionsQueryParams(BaseModel):
    direction: DirectionEnum
    transaction_id: TransactionTypeEnum
    transaction_status: TransactionStatusEnum
    min_record_count: int
    max_record_count: int
    caller_license: Optional[str] = None
    e_partner: Optional[str] = None
    transaction_file_name: Optional[str] = None
    transaction_from_date: Optional[str] = None
    transaction_to_date: Optional[str] = None

class GetNewTransactionsResponseModel(BaseModel):
    result: int
    xml_transaction: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class GetNewPriorAuthorizationTransactionsResponseModel(BaseModel):
    result: int
    xml_transaction: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class UploadTransactionResponseModel(BaseModel):
    result: int
    error_message: Optional[str] = None
    error_report: Optional[str] = None  # bytes as base64 string if needed

class DownloadTransactionFileResponseModel(BaseModel):
    result: int
    file_name: Optional[str] = None
    file: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class CheckForNewPriorAuthorizationTransactionsResponseModel(BaseModel):
    result: int
    error_message: Optional[str] = None

class SetTransactionDownloadedResponseModel(BaseModel):
    result: int
    error_message: Optional[str] = None

class SearchTransactionsResponseModel(BaseModel):
    result: int
    found_transactions: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
